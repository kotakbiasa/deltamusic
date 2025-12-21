# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from delta import app, db


@app.on_my_chat_member(filters.group)
async def track_new_chats(_, m: types.ChatMemberUpdated):
    """Track when bot is added to or removed from groups."""
    new_status = m.new_chat_member.status if m.new_chat_member else None
    old_status = m.old_chat_member.status if m.old_chat_member else None
    
    # Bot was added to group (became member/admin)
    if new_status in ["member", "administrator"] and old_status in [None, "left", "kicked"]:
        if not await db.is_chat(m.chat.id):
            await db.add_chat(m.chat.id)
    
    # Bot was removed from group
    elif new_status in ["left", "kicked"] and old_status in ["member", "administrator"]:
        if await db.is_chat(m.chat.id):
            await db.rm_chat(m.chat.id)


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
