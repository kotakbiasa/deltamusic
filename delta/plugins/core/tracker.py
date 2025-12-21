# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from delta import app, db


@app.on_message(filters.group, group=1)
async def track_groups(_, m: types.Message):
    """Auto-track all groups where bot receives messages."""
    if not await db.is_chat(m.chat.id):
        await db.add_chat(m.chat.id)


@app.on_message(filters.private, group=1)
async def track_users(_, m: types.Message):
    """Auto-track all users who message the bot."""
    if m.from_user and not await db.is_user(m.from_user.id):
        await db.add_user(m.from_user.id)
