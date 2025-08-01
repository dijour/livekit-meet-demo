import logging
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    RoomOutputOptions,
    WorkerOptions,
    cli,
)
from livekit.plugins import openai, hedra

logger = logging.getLogger("snoop-agent")
load_dotenv()

class SnoopAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are Snoop Dogg, the laid-back, cool rapper and lifestyle icon. "
                "You're co-hosting with Martha Stewart. Speak in your characteristic "
                "relaxed, smooth style with your signature phrases. Keep it real, "
                "nephew, but keep it family-friendly. You are one of two hosts, so "
                "keep responses concise to allow for natural conversation flow."
            )
        )
        
    async def on_enter(self):
        """When Snoop enters, start his avatar and give initial greeting"""
        logger.info("Snoop agent entering the room")
        
        # Create and start Snoop's Hedra avatar
        self.avatar = hedra.AvatarSession(
            avatar_id="cc8558ef-c600-4b4f-b685-7e9f2afec194"  # Snoop's avatar ID
        )
        
        # Get the room from job context
        from livekit.agents.job import get_job_context
        job_ctx = get_job_context()
        await self.avatar.start(self.session, room=job_ctx.room)
        
        # Generate initial greeting
        await self.session.generate_reply(
            instructions="Greet the audience in your laid-back style and introduce yourself as Snoop Dogg. Mention that you're here with Martha. Keep it cool and smooth, nephew."
        )


async def entrypoint(ctx: JobContext):
    """Snoop agent entrypoint"""
    logger.info("Starting Snoop agent session")
    
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice="alloy"),  # Snoop's voice
    )
    
    await session.start(
        room=ctx.room,
        agent=SnoopAgent(),
        room_output_options=RoomOutputOptions(audio_enabled=False),  # Avatar handles audio
        room_input_options=RoomInputOptions(),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="snoop-agent",
        port=8082
    ))
