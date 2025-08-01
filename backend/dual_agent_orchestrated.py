import logging
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    ChatContext,
    JobContext,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
)
from livekit.agents.llm import function_tool
from livekit.plugins import openai, hedra

logger = logging.getLogger("dual-hedra-avatar-orchestrated")
load_dotenv()

@dataclass
class ConversationData:
    """Shared data between Martha and Snoop agents"""
    turn_count: int = 0
    last_speaker: Optional[str] = None
    topic: Optional[str] = None


class MarthaAgent(Agent):
    def __init__(self, *, chat_ctx: Optional[ChatContext] = None) -> None:
        super().__init__(
            instructions=(
                "You are Martha Stewart, the elegant and sophisticated lifestyle expert. "
                "You're co-hosting a cooking show with Snoop Dogg. "
                "Speak in your characteristic refined, articulate style with attention to detail and elegance. "
                "Keep responses conversational and engaging. "
                "After responding to the user, you should hand off to Snoop for the next response."
            ),
            llm=openai.realtime.RealtimeModel(voice="ash"),
            chat_ctx=chat_ctx,
        )
        
        # Create Martha's Hedra avatar
        self.avatar = hedra.AvatarSession(
            avatar_id="0396e7f6-252a-4bd8-8f41-e8d1ecd6367e"  # Martha's avatar ID
        )

    async def on_enter(self):
        """When Martha enters, start her avatar and generate initial response"""
        logger.info("Martha entering the conversation")
        
        # Start Martha's avatar with the session's room
        from livekit.agents.job import get_job_context
        job_ctx = get_job_context()
        await self.avatar.start(self.session, room=job_ctx.room)
        
        # Generate initial greeting
        await self.session.generate_reply(
            instructions="Greet the audience warmly and introduce yourself and mention that Snoop will join the conversation. Keep it brief and elegant."
        )

    @function_tool
    async def handoff_to_snoop(
        self,
        context: RunContext[ConversationData],
        topic: Optional[str] = None,
    ):
        """Hand off the conversation to Snoop Dogg
        
        Args:
            topic: Optional topic or context to pass to Snoop
        """
        logger.info(f"Martha handing off to Snoop. Topic: {topic}")
        
        context.userdata.turn_count += 1
        context.userdata.last_speaker = "martha"
        if topic:
            context.userdata.topic = topic
            
        snoop_agent = SnoopAgent(chat_ctx=context.session.chat_ctx)
        return snoop_agent, "Now let me hand this over to my friend Snoop!"


class SnoopAgent(Agent):
    def __init__(self, *, chat_ctx: Optional[ChatContext] = None) -> None:
        super().__init__(
            instructions=(
                "You are Snoop Dogg, the laid-back, cool rapper and lifestyle icon. "
                "You're co-hosting a cooking show with Martha Stewart. "
                "Speak in your characteristic relaxed, smooth style with your signature phrases. "
                "Keep it real, nephew, but keep it family-friendly. "
                "After responding to the user, you should hand off back to Martha for the next response."
            ),
            llm=openai.realtime.RealtimeModel(voice="alloy"),
            chat_ctx=chat_ctx,
        )
        
        # Create Snoop's Hedra avatar
        self.avatar = hedra.AvatarSession(
            avatar_id="cc8558ef-c600-4b4f-b685-7e9f2afec194"  # Snoop's avatar ID
        )

    async def on_enter(self):
        """When Snoop enters, start his avatar and generate response"""
        logger.info("Snoop entering the conversation")
        
        # Start Snoop's avatar with the session's room
        from livekit.agents.job import get_job_context
        job_ctx = get_job_context()
        await self.avatar.start(self.session, room=job_ctx.room)
        
        # Generate response based on context
        await self.session.generate_reply()

    @function_tool
    async def handoff_to_martha(
        self,
        context: RunContext[ConversationData],
        topic: Optional[str] = None,
    ):
        """Hand off the conversation back to Martha Stewart
        
        Args:
            topic: Optional topic or context to pass to Martha
        """
        logger.info(f"Snoop handing off to Martha. Topic: {topic}")
        
        context.userdata.turn_count += 1
        context.userdata.last_speaker = "snoop"
        if topic:
            context.userdata.topic = topic
            
        martha_agent = MarthaAgent(chat_ctx=context.session.chat_ctx)
        return martha_agent, "Alright, let me pass this back to Martha, she got the skills!"


async def entrypoint(ctx: JobContext):
    """Main entrypoint that starts the dual avatar session"""
    logger.info("Starting orchestrated dual avatar session with Martha and Snoop")
    
    # Create the session with shared conversation data
    session = AgentSession[ConversationData](
        llm=openai.realtime.RealtimeModel(voice="ash"),
        userdata=ConversationData(),
    )

    # Start with Martha as the initial agent
    await session.start(
        agent=MarthaAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(),
        room_output_options=RoomOutputOptions(audio_enabled=False),  # Avatars handle audio
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
