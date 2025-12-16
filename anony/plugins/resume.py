# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import anon, app, db
from anony.helpers import admin_check


@app.on_message(filters.command(["resume"]) & filters.group & ~app.bl_users)
@admin_check
async def resume(_, message: types.Message):
    if not await db.get_call(message.chat.id):
        return await message.reply_text("Tidak ada streaming yang sedang diputar.")
    if await db.playing(message.chat.id):
        return await message.reply_text("Streaming tidak dijeda!")
    await anon.resume(message.chat.id)
    await message.reply_text(
        f"{message.from_user.mention} melanjutkan streaming."
    )
