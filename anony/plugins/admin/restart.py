# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import asyncio
import os
import sys

from pyrogram import filters, types

from anony import app


@app.on_message(filters.command(["restart", "reboot"]) & filters.user(app.owner))
async def restart_bot(_, message: types.Message):
    """Restart the bot."""
    await message.reply_text("Merestart...")
    await asyncio.sleep(1)
    await message.reply_text(
        "Restart sedang berlangsung. Jangan khawatir, hanya butuh beberapa detik..."
    )
    os.execl(sys.executable, sys.executable, "-m", "anony")


@app.on_message(filters.command(["update"]) & filters.user(app.owner))
async def update_bot(_, message: types.Message):
    """Update and restart bot."""
    sent = await message.reply_text("Checking for updates...")
    os.system("git pull")
    await sent.edit_text("Updated! Restarting...")
    await asyncio.sleep(1)
    os.execl(sys.executable, sys.executable, "-m", "anony")


@app.on_message(filters.command(["logs"]) & filters.user(app.owner))
async def get_logs(_, message: types.Message):
    """Get bot logs."""
    if not os.path.exists("log.txt"):
        return await message.reply_text("Log file tidak ditemukan.")
    await message.reply_document("log.txt", caption="📄 **Bot Logs**")
