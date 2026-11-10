import asyncio
import logging

import numpy as np
from dotenv import load_dotenv
from livekit import api, rtc
from livekit.agents import JobContext, WorkerOptions, cli

from phone_stt import transcribe_audio

load_dotenv()

logger = logging.getLogger("voicebridge")
logging.basicConfig(level=logging.INFO)


async def find_other_rooms(current_room: str):
    lkapi = api.LiveKitAPI()
    try:
        res = await lkapi.room.list_rooms(api.ListRoomsRequest())
        return [
            r.name
            for r in res.rooms
            if r.name.startswith("pre") and r.name != current_room
        ]
    finally:
        await lkapi.aclose()


# Audio configuration
RATE = 16000            # Whisper expects 16 kHz
SPEECH_RMS = 500        # Loudness threshold for speech detection
SILENCE_SECS = 0.8      # Silence duration that ends an utterance
MIN_SECS = 0.4          # Ignore clips shorter than this


async def listen(track: rtc.Track, queue: asyncio.Queue):
    stream = rtc.AudioStream(
        track,
        sample_rate=RATE,
        num_channels=1
    )

    buf = []
    speaking = False
    silent = 0

    async for event in stream:
        samples = np.frombuffer(
            event.frame.data,
            dtype=np.int16
        )

        rms = float(
            np.sqrt(
                np.mean(samples.astype(np.float32) ** 2)
            )
        )

        if rms > SPEECH_RMS:
            speaking, silent = True, 0
            buf.append(samples)

        elif speaking:
            buf.append(samples)
            silent += len(samples)

            if silent > SILENCE_SECS * RATE:
                audio = np.concatenate(buf)

                buf, speaking, silent = [], False, 0

                if len(audio) > MIN_SECS * RATE:
                    queue.put_nowait(audio)


async def stt_worker(queue: asyncio.Queue):
    while True:
        audio = await queue.get()

        try:
            text, conf, secs = await asyncio.to_thread(
                transcribe_audio,
                audio
            )

            if not text:
                continue

            logger.info(
                'Heard (%.0f%%, %.1fs): "%s"',
                conf,
                secs,
                text
            )

        except Exception:
            logger.exception("Speech transcription failed")

        finally:
            queue.task_done()


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    logger.info("Joined room: %s", ctx.room.name)

    audio_source = rtc.AudioSource(sample_rate=48000, num_channels=1)
    tasks = set()
    queue: asyncio.Queue = asyncio.Queue()
    answered = asyncio.Event()

    worker_task = asyncio.create_task(stt_worker(queue))
    tasks.add(worker_task)
    worker_task.add_done_callback(tasks.discard)

    @ctx.room.on("participant_attributes_changed")
    def on_attrs(changed, p):
        if "sip.callStatus" in changed:
            logger.info("Call status -> %s", p.attributes.get("sip.callStatus"))

    @ctx.room.on("room_metadata_changed")
    def on_meta(old_metadata, new_metadata):
        if new_metadata == "answer":
            answered.set()

    @ctx.room.on("track_subscribed")
    def on_track(track, publication, participant):
        if (
            track.kind == rtc.TrackKind.KIND_AUDIO
            and participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
        ):
            logger.info("Receiving audio from %s", participant.identity)
            t = asyncio.create_task(listen(track, queue))
            tasks.add(t)
            t.add_done_callback(tasks.discard)

    try:
        caller = await ctx.wait_for_participant()
    except RuntimeError:
        logger.info("Caller hung up before the call was answered")
        return
    logger.info("Incoming call from %s - waiting for answer", caller.identity)

    if ctx.room.metadata == "answer":
        answered.set()
    await answered.wait()

    audio_track = rtc.LocalAudioTrack.create_audio_track("bridge-audio", audio_source)
    await ctx.room.local_participant.publish_track(
        audio_track,
        rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE),
    )
    logger.info("Call answered - published audio track")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="Agent 2"
        )
    )