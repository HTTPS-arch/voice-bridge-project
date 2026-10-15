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

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    logger.info("Joined room: %s", ctx.room.name)

    @ctx.room.on("participant_attributes_changed")
    def on_attrs(changed, p):
        if "sip.callStatus" in changed:
            logger.info("Call status -> %s", p.attributes.get("sip.callStatus"))

    audio_source = rtc.AudioSource(sample_rate=48000, num_channels=1)
    audio_track = rtc.LocalAudioTrack.create_audio_track("bridge-audio", audio_source)
    await ctx.room.local_participant.publish_track(
        audio_track,
        rtc.TrackPublishOptions(source=rtc.TrackSource.SOURCE_MICROPHONE),
    )
    logger.info("Published audio track")

    caller = await ctx.wait_for_participant()
    logger.info("Caller: %s kind=%s attrs=%s",
                caller.identity, caller.kind, dict(caller.attributes))

    others = await find_other_rooms(ctx.room.name)
    logger.info("Other active call rooms: %s", others)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name="Agent 2"))