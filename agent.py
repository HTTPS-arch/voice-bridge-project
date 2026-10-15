import asyncio
import logging
from dotenv import load_dotenv
from livekit import api, rtc
from livekit.agents import JobContext, WorkerOptions, cli

load_dotenv()
logger = logging.getLogger("voicebridge")
logging.basicConfig(level=logging.INFO)

async def find_other_rooms(current_room: str):
    lkapi = api.LiveKitAPI()
    try:
        res = await lkapi.room.list_rooms(api.ListRoomsRequest())
        return [r.name for r in res.rooms
                if r.name.startswith("pre") and r.name != current_room]
    finally:
        await lkapi.aclose()

async def echo_audio(track: rtc.Track, source: rtc.AudioSource):
    stream = rtc.AudioStream(track, sample_rate=48000, num_channels=1)
    async for event in stream:
        await source.capture_frame(event.frame)

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    logger.info("Joined room: %s", ctx.room.name)

    audio_source = rtc.AudioSource(sample_rate=48000, num_channels=1)
    tasks = set()

    @ctx.room.on("participant_attributes_changed")
    def on_attrs(changed, p):
        if "sip.callStatus" in changed:
            logger.info("Call status -> %s", p.attributes.get("sip.callStatus"))

    @ctx.room.on("track_subscribed")
    def on_track(track, publication, participant):
        if (track.kind == rtc.TrackKind.KIND_AUDIO
                and participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP):
            logger.info("Receiving audio from %s", participant.identity)
            t = asyncio.create_task(echo_audio(track, audio_source))
            tasks.add(t)
            t.add_done_callback(tasks.discard)

    audio_track = rtc.LocalAudioTrack.create_audio_track("bridge-audio", audio_source)
    await ctx.room.local_participant.publish_track(
        audio_track,
        rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE),
    )
    logger.info("Published audio track")

    caller = await ctx.wait_for_participant()
    logger.info("Caller: %s kind=%s", caller.identity, caller.kind)

    others = await find_other_rooms(ctx.room.name)
    logger.info("Other active call rooms: %s", others)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name="Agent 2"))