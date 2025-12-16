# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import app, db
from anony.helpers import extract_user


@app.on_message(filters.command(["addsudo"]) & filters.user(app.owner))
async def add_sudo(_, message: types.Message):
    """Add user to sudoers list."""
    
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply ke user atau berikan user ID/username.")
    
    user_id, username, full_name = await extract_user(message)
    if not user_id:
        return await message.reply_text("Tidak dapat menemukan user tersebut.")
    
    if user_id in app.sudoers:
        return await message.reply_text(f"{full_name} sudah menjadi sudoer.")
    
    app.sudoers.append(user_id)
    await db.add_sudo(user_id)
    await message.reply_text(f"Menambahkan {full_name} ke sudoers.")


@app.on_message(filters.command(["rmsudo", "delsudo"]) & filters.user(app.owner))
async def remove_sudo(_, message: types.Message):
    """Remove user from sudoers list."""
    
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply ke user atau berikan user ID/username.")
    
    user_id, username, full_name = await extract_user(message)
    if not user_id:
        return await message.reply_text("Tidak dapat menemukan user tersebut.")
    
    if user_id not in app.sudoers:
        return await message.reply_text(f"{full_name} bukan sudoer.")
    
    app.sudoers.remove(user_id)
    await db.del_sudo(user_id)
    await message.reply_text(f"Menghapus {full_name} dari sudoers.")
