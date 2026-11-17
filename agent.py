
import asyncio
import logging
import wave
import struct
import io
from pathlib import Path
from collections import deque
from math import gcd

import numpy as np
from scipy.signal import resample_poly
import torch
from silero_vad import load_silero_vad

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import JobContext, WorkerOptions, cli

from speech_to_text import speech_to_text
from translator import translate_text, get_target_language
from text_to_speech import synthesize_to_wav

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicebridge")

GREETING_FILE = Path(__file__).parent / "greeting.wav"

INPUT_SAMPLE_RATE = 48000
OUTPUT_SAMPLE_RATE = 48000
WHISPER_SAMPLE_RATE = 16000

# Silero VAD settings
# At 16 kHz, Silero processes 512 samples (32 ms) per chunk.
VAD_CHUNK_16K = 512
VAD_CHUNK_48K = 1536

VAD_START_THRESHOLD = 0.55
VAD_END_THRESHOLD = 0.35

SILENCE_DURATION = 0.8
MIN_SPEECH_DURATION = 0.5
MAX_SPEECH_DURATION = 12.0

# Preserve 320 ms of audio before speech detection.
PRE_ROLL_CHUNKS = 10

playback_lock = asyncio.Lock()
processing_lock = asyncio.Lock()


async def play_translated_audio(audio_source, wav_bytes):
    """Play Piper WAV audio through LiveKit."""

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav:
        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        audio_data = wav.readframes(wav.getnframes())

    if sample_width != 2:
        raise ValueError("Piper audio must be 16-bit PCM.")

    samples = np.frombuffer(audio_data, dtype=np.int16)

    if channels > 1:
        samples = samples.reshape(-1, channels).mean(axis=1)
        samples = np.clip(
            samples, -32768, 32767
        ).astype(np.int16)

    if sample_rate != OUTPUT_SAMPLE_RATE:
        divisor = gcd(sample_rate, OUTPUT_SAMPLE_RATE)

        samples = resample_poly(
            samples.astype(np.float32),
            OUTPUT_SAMPLE_RATE // divisor,
            sample_rate // divisor,
        )

        samples = np.clip(
            samples, -32768, 32767
        ).astype(np.int16)

    frame_size = OUTPUT_SAMPLE_RATE // 100

    async with playback_lock:
        for position in range(0, len(samples), frame_size):
            chunk = samples[position:position + frame_size]

            if len(chunk) == 0:
                continue

            if len(chunk) < frame_size:
                chunk = np.pad(
                    chunk,
                    (0, frame_size - len(chunk)),
                )

            frame = rtc.AudioFrame(
                data=chunk.tobytes(),
                sample_rate=OUTPUT_SAMPLE_RATE,
                num_channels=1,
                samples_per_channel=frame_size,
            )

            await audio_source.capture_frame(frame)


async def process_speech(
    audio_samples,
    participant_identity,
    audio_source,
):
    """Transcribe, translate, synthesize, and play speech."""

    if len(audio_samples) == 0:
        return

    # VAD already provides 16-kHz mono PCM.
    audio_16k = np.asarray(
        audio_samples, dtype=np.int16
    )

    try:
        logger.info("Transcribing caller speech...")

        result = await asyncio.to_thread(
            speech_to_text,
            audio_16k,
            WHISPER_SAMPLE_RATE,
        )

        (
            recognized_text,
            detected_language,
            confidence,
            duration,
        ) = result

        if not recognized_text:
            logger.info("No speech recognized.")
            return

        source_language = (
            str(detected_language)
            .lower()
            .split("-")[0]
        )

        logger.info("Caller: %s", recognized_text)
        logger.info(
            "Detected language: %s",
            source_language,
        )
        logger.info("Confidence: %s", confidence)

        if source_language not in ("en", "de"):
            logger.warning(
                "Unsupported language detected: %s",
                source_language,
            )
            return

        target_language = get_target_language(
            source_language
        )

        (
            translated_text,
            translation_time,
        ) = await asyncio.to_thread(
            translate_text,
            recognized_text,
            source_language,
        )

        if not translated_text:
            logger.warning(
                "Translation returned empty text."
            )
            return

        logger.info(
            "Translated text: %s",
            translated_text,
        )
        logger.info(
            "Translation time: %.2f seconds",
            translation_time,
        )

        wav_bytes, tts_time = await asyncio.to_thread(
            synthesize_to_wav,
            translated_text,
            target_language,
        )

        logger.info(
            "Speech generation time: %.2f seconds",
            tts_time,
        )

        await play_translated_audio(
            audio_source,
            wav_bytes,
        )

        logger.info(
            "Translated speech played for %s",
            participant_identity,
        )

    except Exception:
        logger.exception(
            "Translation or speech playback failed."
        )


async def read_caller_audio(
    track,
    participant_identity,
    audio_source,
):
    """Detect speech using streaming Silero VAD."""

    logger.info(
        "Starting VAD audio reception from: %s",
        participant_identity,
    )

    audio_stream = rtc.AudioStream(track)

    # Independent VAD state for each subscribed audio track.
    vad_model = await asyncio.to_thread(
        load_silero_vad
    )
    vad_model.reset_states()

    pending_48k = np.empty(0, dtype=np.int16)

    pre_roll = deque(maxlen=PRE_ROLL_CHUNKS)

    speech_chunks = []
    speech_started = False

    silence_seconds = 0.0
    voiced_seconds = 0.0
    buffered_seconds = 0.0

    tasks = set()

    async def submit_utterance():
        nonlocal speech_chunks
        nonlocal speech_started
        nonlocal silence_seconds
        nonlocal voiced_seconds
        nonlocal buffered_seconds

        if (
            speech_chunks
            and voiced_seconds >= MIN_SPEECH_DURATION
        ):
            complete_audio = np.concatenate(
                speech_chunks
            )

            logger.info(
                "VAD accepted %.2f s of voiced audio",
                voiced_seconds,
            )

            async def run_in_order():
                async with processing_lock:
                    await process_speech(
                        complete_audio,
                        participant_identity,
                        audio_source,
                    )

            task = asyncio.create_task(
                run_in_order()
            )

            tasks.add(task)
            task.add_done_callback(
                tasks.discard
            )

        else:
            logger.debug(
                "VAD rejected short/noisy audio"
            )

        speech_chunks = []
        speech_started = False

        silence_seconds = 0.0
        voiced_seconds = 0.0
        buffered_seconds = 0.0

        pre_roll.clear()
        vad_model.reset_states()

    try:
        async for event in audio_stream:
            frame = event.frame

            if (
                frame.sample_rate != INPUT_SAMPLE_RATE
                or frame.num_channels != 1
            ):
                logger.warning(
                    "Skipping audio frame: "
                    "rate=%s channels=%s",
                    frame.sample_rate,
                    frame.num_channels,
                )
                continue

            samples = np.frombuffer(
                frame.data,
                dtype=np.int16,
            ).copy()

            if samples.size == 0:
                continue

            pending_48k = np.concatenate(
                (pending_48k, samples)
            )

            while pending_48k.size >= VAD_CHUNK_48K:

                chunk_48k = pending_48k[
                    :VAD_CHUNK_48K
                ]

                pending_48k = pending_48k[
                    VAD_CHUNK_48K:
                ]

                chunk_16k = resample_poly(
                    chunk_48k.astype(np.float32),
                    1,
                    3,
                )

                chunk_16k = np.clip(
                    chunk_16k,
                    -32768,
                    32767,
                ).astype(np.int16)

                normalized = torch.from_numpy(
                    chunk_16k.astype(np.float32)
                    / 32768.0
                )

                with torch.inference_mode():
                    speech_probability = float(
                        vad_model(
                            normalized,
                            WHISPER_SAMPLE_RATE,
                        ).item()
                    )

                chunk_seconds = (
                    VAD_CHUNK_16K
                    / WHISPER_SAMPLE_RATE
                )

                if not speech_started:

                    if (
                        speech_probability
                        >= VAD_START_THRESHOLD
                    ):
                        speech_started = True

                        speech_chunks = list(
                            pre_roll
                        )

                        speech_chunks.append(
                            chunk_16k
                        )

                        buffered_seconds = (
                            len(speech_chunks)
                            * chunk_seconds
                        )

                        voiced_seconds = (
                            chunk_seconds
                        )

                        silence_seconds = 0.0

                        pre_roll.clear()

                        logger.info(
                            "VAD speech started "
                            "(probability=%.2f)",
                            speech_probability,
                        )

                    else:
                        pre_roll.append(
                            chunk_16k
                        )

                    continue

                speech_chunks.append(
                    chunk_16k
                )

                buffered_seconds += (
                    chunk_seconds
                )

                if (
                    speech_probability
                    >= VAD_END_THRESHOLD
                ):
                    voiced_seconds += (
                        chunk_seconds
                    )
                    silence_seconds = 0.0

                else:
                    silence_seconds += (
                        chunk_seconds
                    )

                if (
                    silence_seconds >= SILENCE_DURATION
                    or buffered_seconds
                    >= MAX_SPEECH_DURATION
                ):
                    await submit_utterance()

    except asyncio.CancelledError:
        raise

    except Exception:
        logger.exception(
            "Error receiving audio from: %s",
            participant_identity,
        )

    finally:
        # Submit a final phrase when the stream ends.
        if speech_started:
            await submit_utterance()

        await audio_stream.aclose()

        logger.info(
            "Audio reception stopped for: %s",
            participant_identity,
        )


async def play_greeting(ctx: JobContext):
    """Play the existing greeting WAV file."""

    if not GREETING_FILE.exists():
        logger.error(
            "Missing greeting file: %s",
            GREETING_FILE,
        )
        return

    with wave.open(str(GREETING_FILE), "rb") as wav:
        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        audio_data = wav.readframes(
            wav.getnframes()
        )

    if sample_width != 2:
        raise ValueError(
            "Greeting must be 16-bit PCM WAV audio"
        )

    if channels != 1:
        raise ValueError(
            "Greeting must be mono audio"
        )

    source = rtc.AudioSource(
        sample_rate,
        channels,
    )

    track = rtc.LocalAudioTrack.create_audio_track(
        "greeting",
        source,
    )

    await ctx.room.local_participant.publish_track(
        track
    )

    logger.info(
        "Greeting audio track published"
    )

    samples = struct.unpack(
        f"<{len(audio_data) // 2}h",
        audio_data,
    )

    frame_size = sample_rate // 100

    for position in range(
        0,
        len(samples),
        frame_size,
    ):
        chunk = samples[
            position:position + frame_size
        ]

        if len(chunk) < frame_size:
            chunk += (0,) * (
                frame_size - len(chunk)
            )

        frame = rtc.AudioFrame(
            data=struct.pack(
                f"<{len(chunk)}h",
                *chunk,
            ),
            sample_rate=sample_rate,
            num_channels=channels,
            samples_per_channel=frame_size,
        )

        await source.capture_frame(
            frame
        )

    logger.info(
        "Greeting playback finished"
    )


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    logger.info(
        "Agent joined room: %s",
        ctx.room.name,
    )

    translation_source = rtc.AudioSource(
        OUTPUT_SAMPLE_RATE,
        1,
    )

    translation_track = (
        rtc.LocalAudioTrack.create_audio_track(
            "translated-speech",
            translation_source,
        )
    )

    await ctx.room.local_participant.publish_track(
        translation_track
    )

    logger.info(
        "Translation audio track published"
    )

    @ctx.room.on("track_subscribed")
    def on_track_subscribed(
        track,
        publication,
        participant,
    ):

        if track.kind == rtc.TrackKind.KIND_AUDIO:

            logger.info(
                "Receiving audio from: %s",
                participant.identity,
            )

            asyncio.create_task(
                read_caller_audio(
                    track,
                    participant.identity,
                    translation_source,
                )
            )

    for participant in (
        ctx.room.remote_participants.values()
    ):

        logger.info(
            "Already in room: %s (kind=%s)",
            participant.identity,
            participant.kind,
        )

    @ctx.room.on("participant_connected")
    def on_join(participant):

        logger.info(
            "Participant joined: %s (kind=%s)",
            participant.identity,
            participant.kind,
        )

    @ctx.room.on("participant_disconnected")
    def on_leave(participant):

        logger.info(
            "Participant left: %s",
            participant.identity,
        )

    await asyncio.sleep(1)

    await play_greeting(ctx)


if __name__ == "__main__":

    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="Agent 2",
        )
    )
