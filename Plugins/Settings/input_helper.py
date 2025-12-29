# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat

import asyncio
from flask import Flask
from pyrogram import enums
from Plugins.helper import user_states, get_styled_text

async def timeout_handler(client, message, user_id, state_key, delay=30):
    await asyncio.sleep(delay)
    if user_id in user_states and user_states[user_id].get("state") == state_key:
        del user_states[user_id]
        try:
            await message.edit_text(
                get_styled_text("❌ Input Timed Out. Please try again."),
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass


# Rexbots
# Don't Remove Credit
# Telegram Channel @RexBots_Official 
#Supoort group @rexbotschat