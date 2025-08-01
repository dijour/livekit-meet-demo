import logging
from typing import Optional

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

logger = logging.getLogger("dual-agent-dispatch")
load_dotenv()

class MarthaAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are Martha Stewart, the elegant and sophisticated lifestyle expert. "
                "You're co-hosting with Snoop Dogg. Speak in your characteristic refined, "
                "articulate style with attention to detail and elegance. Keep responses "
                "conversational and engaging."
            )
        )
        
    async def on_enter(self):
        """When Martha enters, start her avatar"""
        logger.info("Martha agent entering the room")
        
        # Create and start Martha's Hedra avatar
        self.avatar = hedra.AvatarSession(
            avatar_id="0396e7f6-252a-4bd8-8f41-e8d1ecd6367e"  # Martha's avatar ID
        )
        
        await self.avatar.start(self.session, room=self.session.room)
        
        # Generate initial greeting
        await self.session.generate_reply(
            instructions="Greet the audience warmly and introduce yourself as Martha Stewart. Mention that Snoop will also be joining. Keep it brief and elegant."
        )


class SnoopAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are Snoop Dogg, the laid-back, cool rapper and lifestyle icon. "
                "You're co-hosting with Martha Stewart. Speak in your characteristic "
                "relaxed, smooth style with your signature phrases. Keep it real, "
                "nephew, but keep it family-friendly."
            )
        )
        
    async def on_enter(self):
        """When Snoop enters, start his avatar"""
        logger.info("Snoop agent entering the room")
        
        # Create and start Snoop's Hedra avatar
        self.avatar = hedra.AvatarSession(
            avatar_id="cc8558ef-c600-4b4f-b685-7e9f2afec194"  # Snoop's avatar ID
        )
        
        await self.avatar.start(self.session, room=self.session.room)
        
        # Generate initial greeting
        await self.session.generate_reply(
            instructions="Greet the audience in your laid-back style and introduce yourself as Snoop Dogg. Mention that you're here with Martha. Keep it cool and smooth."
        )


async def martha_entrypoint(ctx: JobContext):
    """Entrypoint for Martha agent"""
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


async def snoop_entrypoint(ctx: JobContext):
    """Entrypoint for Snoop agent"""
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


# Default entrypoint - we'll configure which agent to use via agent_name
async def entrypoint(ctx: JobContext):
    """Main entrypoint that routes to the appropriate agent based on agent_name"""
    agent_name = getattr(ctx, 'agent_name', 'martha-agent')  # Default to Martha
    
    if agent_name == 'martha-agent':
        await martha_entrypoint(ctx)
    elif agent_name == 'snoop-agent':
        await snoop_entrypoint(ctx)
    else:
        logger.error(f"Unknown agent name: {agent_name}")
        raise ValueError(f"Unknown agent name: {agent_name}")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
