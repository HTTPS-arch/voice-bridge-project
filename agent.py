import logging
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import JobContext, WorkerOptions, cli

load_dotenv()
logger = logging.getLogger("voicebridge")
logging.basicConfig(level=logging.INFO)

async def entrypoint(ctx: JobContext):
    await ctx.connect()
    logger.info("Agent joined room: %s", ctx.room.name)

    for p in ctx.room.remote_participants.values():
        logger.info("Already in room: %s (kind=%s)", p.identity, p.kind)

    @ctx.room.on("participant_connected")
    def on_join(p):
        logger.info("Participant joined: %s (kind=%s)", p.identity, p.kind)

    @ctx.room.on("participant_disconnected")
    def on_leave(p):
        logger.info("Participant left: %s", p.identity)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name="Agent 2"))