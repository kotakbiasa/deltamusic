# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import app, db
from anony.helpers import admin_check, utils


@app.on_message(filters.command(["auth"]) & filters.group & ~app.bl_users)
@admin_check
async def auth_user(_, message: types.Message):
    """Add user to authorized users list."""
    
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply ke user atau berikan user ID/username.")
    
    user = await utils.extract_user(message)
    if not user:
        return await message.reply_text("Tidak dapat menemukan user tersebut.")
    
    # Check if user is admin
    admins = await db.get_admins(message.chat.id)
    if user.id in admins:
        return await message.reply_text(
            f"Pengguna sudah menjadi <b>admin</b> dan tidak bisa ditambahkan ke pengguna terotorisasi."
        )
    
    if await db.is_auth(message.chat.id, user.id):
        return await message.reply_text(f"{user.mention} sudah terotorisasi.")
    
    await db.add_auth(message.chat.id, user.id)
    await message.reply_text(f"Menambahkan {user.mention} ke daftar pengguna terotorisasi.")


@app.on_message(filters.command(["unauth"]) & filters.group & ~app.bl_users)
@admin_check
async def unauth_user(_, message: types.Message):
    """Remove user from authorized users list."""
    
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Reply ke user atau berikan user ID/username.")
    
    user = await utils.extract_user(message)
    if not user:
        return await message.reply_text("Tidak dapat menemukan user tersebut.")
    
    if not await db.is_auth(message.chat.id, user.id):
        return await message.reply_text(f"{user.mention} tidak terotorisasi.")
    
    await db.rm_auth(message.chat.id, user.id)
    await message.reply_text(f"Menghapus {user.mention} dari daftar pengguna terotorisasi.")
