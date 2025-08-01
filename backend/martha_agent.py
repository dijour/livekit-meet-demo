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

logger = logging.getLogger("martha-agent")
load_dotenv()

class MarthaAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are Martha Stewart, the elegant and sophisticated lifestyle expert. "
                "You're co-hosting with Snoop Dogg. Speak in your characteristic refined, "
                "articulate style with attention to detail and elegance. Keep responses "
                "conversational and engaging. You are one of two hosts, so keep responses "
                "concise to allow for natural conversation flow."
            )
        )
        
    async def on_enter(self):
        """When Martha enters, start her avatar and give initial greeting"""
        logger.info("Martha agent entering the room")
        
        # Create and start Martha's Hedra avatar
        self.avatar = hedra.AvatarSession(
            avatar_id="0396e7f6-252a-4bd8-8f41-e8d1ecd6367e"  # Martha's avatar ID
        )
        
        # Get the room from job context
        from livekit.agents.job import get_job_context
        job_ctx = get_job_context()
        await self.avatar.start(self.session, room=job_ctx.room)
        
        # Generate initial greeting
        await self.session.generate_reply(
            instructions="Greet the audience warmly and introduce yourself as Martha Stewart. Mention that Snoop will also be joining the conversation. Keep it brief and elegant."
        )


async def entrypoint(ctx: JobContext):
    """Martha agent entrypoint"""
    logger.info("Starting Martha agent session")
    
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice="ash"),  # Martha's voice
    )
    
    await session.start(
        room=ctx.room,
        agent=MarthaAgent(),
        room_output_options=RoomOutputOptions(audio_enabled=False),  # Avatar handles audio
        room_input_options=RoomInputOptions(),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="martha-agent",
        port=8081
    ))
