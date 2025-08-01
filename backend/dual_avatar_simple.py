import asyncio
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

logger = logging.getLogger("dual-avatar-simple")
load_dotenv()

class SimpleAlternatingAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a dual avatar host system with Martha Stewart and Snoop Dogg alternating responses."
        )
        self.turn_count = 0
        self.martha_avatar = None
        self.snoop_avatar = None
        
    async def on_user_speech_committed(self, user_speech):
        """Handle user speech and alternate between avatars"""
        if not user_speech.text:
            return
            
        # Determine which avatar should respond
        is_martha_turn = (self.turn_count % 2) == 0
        self.turn_count += 1
        
        if is_martha_turn:
            logger.info(f"Martha responding (turn {self.turn_count})")
            # Martha's response
            await self.session.generate_reply(
                instructions=f"You are Martha Stewart. Respond elegantly to: '{user_speech.text}'. Keep it conversational and mention that Snoop will respond next."
            )
        else:
            logger.info(f"Snoop responding (turn {self.turn_count})")
            # Snoop's response  
            await self.session.generate_reply(
                instructions=f"You are Snoop Dogg. Respond in your laid-back style to: '{user_speech.text}'. Keep it cool and mention Martha will respond next, nephew."
            )


async def entrypoint(ctx: JobContext):
    """Main entrypoint - creates both avatars and manages alternation"""
    logger.info("Starting simple dual avatar session")
    
    # Create Martha's avatar session
    martha_avatar = hedra.AvatarSession(
        avatar_id="0396e7f6-252a-4bd8-8f41-e8d1ecd6367e"  # Martha's avatar
    )
    
    # Create Snoop's avatar session  
    snoop_avatar = hedra.AvatarSession(
        avatar_id="cc8558ef-c600-4b4f-b685-7e9f2afec194"  # Snoop's avatar
    )
    
    # Create the main agent session
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice="ash"),
    )
    
    # Start both avatars simultaneously
    logger.info("Starting Martha's avatar")
    await martha_avatar.start(session, room=ctx.room)
    
    logger.info("Starting Snoop's avatar") 
    await snoop_avatar.start(session, room=ctx.room)
    
    # Wait a moment for both avatars to initialize
    await asyncio.sleep(2)
    
    # Create and start the alternating agent
    agent = SimpleAlternatingAgent()
    agent.martha_avatar = martha_avatar
    agent.snoop_avatar = snoop_avatar
    
    await session.start(
        room=ctx.room,
        agent=agent,
        room_output_options=RoomOutputOptions(audio_enabled=False),  # Avatars handle audio
        room_input_options=RoomInputOptions(),
    )
    
    # Initial greeting from Martha
    logger.info("Martha giving initial greeting")
    await session.generate_reply(
        instructions="You are Martha Stewart. Greet the audience warmly and introduce yourself and Snoop as co-hosts. Mention you'll be alternating responses. Keep it brief and elegant."
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
