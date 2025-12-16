# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import asyncio

from pyrogram import filters, types

from anony import app, db


@app.on_message(filters.command(["broadcast", "gcast"]) & filters.user(app.owner))
async def broadcast_message(_, message: types.Message):
    """Broadcast message to all chats/users."""
    
    if not message.reply_to_message:
        return await message.reply_text("Reply ke pesan yang ingin di-broadcast.")
    
    mode = "chats" if message.command[0] == "gcast" else "users"
    targets = await db.get_chats() if mode == "chats" else await db.get_users()
    
    sent = await message.reply_text(f"Broadcasting ke {len(targets)} {mode}...")
    
    success = 0
    failed = 0
    
    for target in targets:
        try:
            await message.reply_to_message.copy(target)
            success += 1
            await asyncio.sleep(0.5)  # Anti-flood
        except:
            failed += 1
    
    await sent.edit_text(
        f"**Broadcast Selesai**\n\n✅ Berhasil: {success}\n❌ Gagal: {failed}"
    )


@app.on_message(filters.command(["cancelcast"]) & filters.user(app.owner))
async def cancel_broadcast(_, message: types.Message):
    """Cancel ongoing broadcast."""
    await message.reply_text("Broadcast dibatalkan.")
