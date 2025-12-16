# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import asyncio

from pyrogram import filters, types

from anony import anon, app, boot, config


@app.on_message(filters.command(["ping"]) & filters.group & ~app.bl_users)
async def ping(_, message: types.Message):
    start = asyncio.get_event_loop().time()
    m = await message.reply_photo(
        photo=config.PING_IMG,
        caption="🏓 Pinging...",
    )
    end = asyncio.get_event_loop().time()
    uptime = int(end - boot)
    await m.edit_caption(
        f"🏓 **Pong!**\n\n💬 **Latency:** `{(end - start) * 1000:.3f}ms`\n📡 **Ping:** `{await anon.ping()}ms`\n⏱️ **Uptime:** `{uptime // 3600}h {(uptime % 3600) // 60}m`"
    )
