from dotenv import load_dotenv
import asyncio
import logging
from dataclasses import dataclass
from typing import Optional
from livekit.agents.llm import function_tool

logger = logging.getLogger(__name__)

from livekit import agents
from livekit.agents import (
    Agent,
    AgentSession,
    ChatContext,
    JobContext,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
)
from livekit.plugins import (
    hedra,
    openai,
)
try:
    from livekit.plugins import noise_cancellation
except ImportError:
    # Fallback: noise cancellation not available in this version
    noise_cancellation = None

load_dotenv(".env.local")

@dataclass
class ConversationData:
    current_speaker: Optional[str] = None
    conversation_started: bool = False
    snoop_avatar: Optional[hedra.AvatarSession] = None
    martha_avatar: Optional[hedra.AvatarSession] = None

class SnoopAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are Snoop Dogg, the legendary rapper and cultural icon. "
                "You're collaborating with Martha Stewart on a fun project. "
                "Speak in your signature laid-back West Coast style, using your characteristic "
                "slang like 'fo shizzle', 'neffew', and ending sentences with 'ya dig?' or 'fo sho'. "
                "You're known for your love of cooking with Martha, cannabis culture, and your smooth personality. "
                "Keep your responses concise and engaging, always ending with a question for Martha. "
                "After speaking, always call the switch_to_martha function to let her respond."
            )
        )

    async def on_enter(self):
        if not self.session.userdata.conversation_started:
            self.session.userdata.conversation_started = True
            self.session.userdata.current_speaker = "snoop"
            logger.info("🎤 Starting conversation with Snoop Dogg")
            self.session.generate_reply(
                instructions="Introduce yourself to Martha and ask her about what you two should cook together today."
            )

    @function_tool
    async def switch_to_martha(self, context: RunContext[ConversationData]):
        """Called when Snoop is done speaking and it's Martha's turn."""
        logger.info("🎤 Switching turn to Martha Stewart")
        context.userdata.current_speaker = "martha"
        return MarthaAgent()

class MarthaAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are Martha Stewart, the lifestyle and cooking expert. "
                "You're collaborating with Snoop Dogg on a fun project. "
                "Speak in your characteristic polished, proper style while showing your fun side "
                "that comes out when working with Snoop. You're known for your expertise in cooking, "
                "home decoration, and entertaining, but also for your unexpected friendship with Snoop. "
                "Use phrases like 'It's a good thing' and maintain your sophisticated yet approachable demeanor. "
                "Keep your responses concise and engaging, always ending with a question for Snoop. "
                "After speaking, always call the switch_to_snoop function to let him respond."
            )
        )

    @function_tool
    async def switch_to_snoop(self, context: RunContext[ConversationData]):
        """Called when Martha is done speaking and it's Snoop's turn."""
        logger.info("🎤 Switching turn to Snoop Dogg")
        context.userdata.current_speaker = "snoop"
        return SnoopAgent()
        

async def entrypoint(ctx: agents.JobContext):
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create two sessions with different voices
    snoop_session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice="ash"),
        userdata=ConversationData()
    )
    
    martha_session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice="shimmer"),
        userdata=ConversationData()
    )

    # Create avatar sessions
    snoop_avatar = hedra.AvatarSession(
        avatar_id="cc8558ef-c600-4b4f-b685-7e9f2afec194",
        avatar_participant_identity="snoop",
        avatar_participant_name="Snoop Dogg",
    )

    martha_avatar = hedra.AvatarSession(
        avatar_id="0396e7f6-252a-4bd8-8f41-e8d1ecd6367e",
        avatar_participant_identity="martha",
        avatar_participant_name="Martha Stewart",
    )

    # Start avatars with their respective sessions
    await snoop_avatar.start(snoop_session, room=ctx.room)
    await asyncio.sleep(2)  # Add delay to prevent rate limiting
    await martha_avatar.start(martha_session, room=ctx.room)

    # Start with Snoop
    await snoop_session.start(
        room=ctx.room,
        agent=SnoopAgent(),
        room_output_options=RoomOutputOptions(audio_enabled=False),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC() if noise_cancellation else None,
        ),
    )

    # Start Martha's session
    await martha_session.start(
        room=ctx.room,
        agent=MarthaAgent(),
        room_output_options=RoomOutputOptions(audio_enabled=False),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC() if noise_cancellation else None,
        ),
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))