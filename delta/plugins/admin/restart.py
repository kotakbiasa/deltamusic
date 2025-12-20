# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import asyncio
import os
import sys

from pyrogram import enums, filters, types

from delta import app


@app.on_message(filters.command(["restart", "reboot"]) & filters.user(app.owner))
async def restart_bot(_, message: types.Message):
    """Restart the bot."""
    await message.reply_text("🔄 <b>Merestart Bot...</b>", parse_mode=enums.ParseMode.HTML)
    await asyncio.sleep(1)
    await message.reply_text(
        "⏳ <b>Sedang Proses...</b>\n\n<blockquote>Jangan khawatir, hanya butuh beberapa detik...</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )
    os.execl(sys.executable, sys.executable, "-m", "delta")


@app.on_message(filters.command(["update"]) & filters.user(app.owner))
async def update_bot(_, message: types.Message):
    """Update and restart bot."""
    sent = await message.reply_text("🔄 <b>Checking Updates...</b>", parse_mode=enums.ParseMode.HTML)
    
    process = await asyncio.create_subprocess_shell(
        "git pull",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        return await sent.edit_text(
            f"❌ <b>Update Failed</b>\n\n<pre>{stderr.decode()}</pre>",
            parse_mode=enums.ParseMode.HTML
        )

    await sent.edit_text(
        f"✅ <b>Updated!</b>\n\n<pre>{stdout.decode()}</pre>\n<blockquote>Restarting system...</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )
    await asyncio.sleep(1)
    os.execl(sys.executable, sys.executable, "-m", "delta")


@app.on_message(filters.command(["logs"]) & filters.user(app.owner))
async def get_logs(_, message: types.Message):
    """Get bot logs."""
    if not os.path.exists("log.txt"):
        return await message.reply_text(
            "❌ <b>Log Tidak Ditemukan</b>\n\n<blockquote>File log belum tersedia</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
    await message.reply_document("log.txt", caption="📄 <b>Bot Logs</b>", parse_mode=enums.ParseMode.HTML)
