# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import app, db


@app.on_message(filters.command(["activevoice", "activevideo"]) & ~app.bl_users)
@app.only_sudoers
async def active_calls(_, message: types.Message):
    """Show all active voice/video calls."""
    text = "**Panggilan Aktif:**\n\n"
    count = 0
    
    for chat_id in list(db.active_calls.keys()):
        try:
            chat = await app.get_chat(chat_id)
            count += 1
            text += f"{count}. {chat.title} (`{chat_id}`)\n"
        except:
            continue
    
    if count == 0:
        text = "Tidak ada panggilan aktif."
    else:
        text += f"\n**Total:** {count} panggilan"
    
    await message.reply_text(text)
