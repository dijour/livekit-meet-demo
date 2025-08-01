import logging
import os
import asyncio
from typing import Dict, Optional

from dotenv import load_dotenv
from PIL import Image

from livekit.agents import Agent, AgentSession, JobContext, RoomInputOptions, RoomOutputOptions, WorkerOptions, WorkerType, cli
from livekit.plugins import (
    hedra,
    openai,
)
from livekit.api import ListParticipantsRequest

logger = logging.getLogger("dual-hedra-avatar-example")
logger.setLevel(logging.INFO)

load_dotenv(".env.local")

class DualAvatarManager:
    def __init__(self):
        self.current_speaker = "martha"  # Start with Martha
        self.response_count = 0
        self.martha_session: Optional[AgentSession] = None
        self.snoop_session: Optional[AgentSession] = None
        self.martha_avatar: Optional[hedra.AvatarSession] = None
        self.snoop_avatar: Optional[hedra.AvatarSession] = None
        
    def get_next_speaker(self) -> str:
        """Alternate between Martha and Snoop"""
        self.response_count += 1
        if self.response_count % 2 == 1:
            self.current_speaker = "martha"
        else:
            self.current_speaker = "snoop"
        return self.current_speaker
    
    def get_current_session(self) -> Optional[AgentSession]:
        if self.current_speaker == "martha":
            return self.martha_session
        else:
            return self.snoop_session
    
    def get_current_avatar(self) -> Optional[hedra.AvatarSession]:
        if self.current_speaker == "martha":
            return self.martha_avatar
        else:
            return self.snoop_avatar

# Global manager instance
avatar_manager = DualAvatarManager()

class MarthaAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You're Martha, the classy culinary expert guiding a cooking session with your co-host Snoop Dogg. 
            Keep it elegant but playful, leaning into your refined taste and friendly banter. Snoop brings bold flavors and spice — 
            you balance that with sophistication and freshness. Your goal is to co-create a brunch menu live with Snoop, starting 
            with suggestions for sides and then guiding the audience step-by-step through the hollandaise sauce prep. Make sure to: 
            Suggest elegant, fresh side options (e.g., arugula salad, roasted asparagus). Respond warmly to Snoop's spicier suggestions, 
            integrating them with your own. Transition smoothly into guiding the audience through hollandaise sauce prep. Sound poised, 
            encouraging, and slightly cheeky — like a polished host who's used to a bit of chaos. Keep responses concise and conversational."""
        )

class SnoopAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You're Snoop Dogg, the laid-back culinary innovator co-hosting a cooking session with Martha. 
            Bring your signature cool, smooth style with bold flavor suggestions and creative twists. Martha handles the elegant side — 
            you're all about adding that special Snoop flair with spices, creative ingredients, and your unique perspective. Your goal 
            is to co-create a brunch menu live with Martha, suggesting bold, flavorful options and adding your own spin to her refined 
            suggestions. Make sure to: Suggest bold, creative side options with interesting spices and flavors. Build on Martha's elegant 
            suggestions with your own creative twists. Keep it smooth, cool, and encouraging — like the laid-back mentor who brings the fun. 
            Keep responses concise and conversational, nephew."""
        )

async def entrypoint(ctx: JobContext):
    global avatar_manager
    
    logger.info("Starting dual live avatar session with Martha and Snoop")
    
    # Create Martha's session and avatar
    avatar_manager.martha_session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice="ash"),  # Martha's voice
    )
    
    avatar_manager.martha_avatar = hedra.AvatarSession(
        avatar_id="0396e7f6-252a-4bd8-8f41-e8d1ecd6367e",  # Martha's avatar ID
    )
    
    # Create Snoop's session and avatar (using same ID for now)
    avatar_manager.snoop_session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice="alloy"),  # Snoop's voice
    )
    
    avatar_manager.snoop_avatar = hedra.AvatarSession(
        avatar_id="cc8558ef-c600-4b4f-b685-7e9f2afec194",  # Same avatar ID - will create second instance
    )
    
    # Start both avatar sessions simultaneously
    logger.info("Starting Martha's avatar session")
    await avatar_manager.martha_avatar.start(avatar_manager.martha_session, room=ctx.room)
    
    logger.info("Starting Snoop's avatar session")
    await avatar_manager.snoop_avatar.start(avatar_manager.snoop_session, room=ctx.room)
    
    # Custom agent class that handles alternation
    class DualAgent(Agent):
        def __init__(self):
            super().__init__(instructions="You are managing a dual avatar conversation between Martha and Snoop.")
            
        async def on_user_speech_committed(self, user_speech):
            """Handle user speech and route to the appropriate avatar session"""
            next_speaker = avatar_manager.get_next_speaker()
            current_session = avatar_manager.get_current_session()
            
            logger.info(f"User said: '{user_speech.text}' - Next speaker: {next_speaker}")
            
            if user_speech.text and current_session:
                # Route to the appropriate avatar session
                if next_speaker == "martha":
                    await avatar_manager.martha_session.generate_reply(
                        instructions=f"You are Martha Stewart. Respond to: '{user_speech.text}'. Stay elegant, sophisticated, and culinary-focused. Keep it brief and classy."
                    )
                else:
                    await avatar_manager.snoop_session.generate_reply(
                        instructions=f"You are Snoop Dogg. Respond to: '{user_speech.text}'. Stay laid-back, cool, and use your signature style. Add some flavor to the conversation, nephew. Keep it brief and smooth."
                    )
    
    # Start Martha's session
    await avatar_manager.martha_session.start(
        room=ctx.room,
        agent=DualAgent(),
        room_output_options=RoomOutputOptions(audio_enabled=False),  # Avatar handles audio
        room_input_options=RoomInputOptions(),
    )
    
    # Start Snoop's session
    await avatar_manager.snoop_session.start(
        room=ctx.room,
        agent=DualAgent(),
        room_output_options=RoomOutputOptions(audio_enabled=False),  # Avatar handles audio
        room_input_options=RoomInputOptions(),
    )
    
    # Log remote participants
    for rp in ctx.room.remote_participants.values():
        logger.info(f"Remote participant: {rp.identity}")
    
    # Start with Martha's greeting
    avatar_manager.current_speaker = "martha"
    logger.info("Martha starting with greeting")
    await avatar_manager.martha_session.generate_reply(
        instructions="Greet the audience warmly and introduce yourself and Snoop as co-hosts for this cooking session. Mention that you'll be trading off responses. Keep it brief and elegant."
    )
    
    # Keep the sessions alive
    await avatar_manager.martha_session.aclose()
    await avatar_manager.snoop_session.aclose()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, worker_type=WorkerType.ROOM))
