# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import app, db
from anony.helpers import utils


@app.on_message(filters.command(["addsudo"]) & filters.user(app.owner))
async def add_sudo(_, message: types.Message):
    """Add user to sudoers list."""
    
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply ke user atau berikan user ID/username.")
    
    user = await utils.extract_user(message)
    if not user:
        return await message.reply_text("Tidak dapat menemukan user tersebut.")
    
    if user.id in app.sudoers:
        return await message.reply_text(f"{user.mention} sudah menjadi sudoer.")
    
    app.sudoers.append(user.id)
    await db.add_sudo(user.id)
    await message.reply_text(f"Menambahkan {user.mention} ke sudoers.")


@app.on_message(filters.command(["rmsudo", "delsudo"]) & filters.user(app.owner))
async def remove_sudo(_, message: types.Message):
    """Remove user from sudoers list."""
    
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply ke user atau berikan user ID/username.")
    
    user = await utils.extract_user(message)
    if not user:
        return await message.reply_text("Tidak dapat menemukan user tersebut.")
    
    if user.id not in app.sudoers:
        return await message.reply_text(f"{user.mention} bukan sudoer.")
    
    app.sudoers.remove(user.id)
    await db.del_sudo(user.id)
    await message.reply_text(f"Menghapus {user.mention} dari sudoers.")
