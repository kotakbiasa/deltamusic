# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

"""
Dashboard Admin Commands - Control dashboard from Telegram
"""

from pyrogram import enums, filters, types

from anony import app, config, logger


# Custom sudo filter that checks at runtime
def sudo_filter(_, __, message):
    """Runtime check for sudo users"""
    if not message.from_user:
        return False
    return message.from_user.id in app.sudoers or message.from_user.id == config.OWNER_ID

sudo_users_filter = filters.create(sudo_filter)


@app.on_message(filters.command(["dashboard"]) & ~app.bl_users)
async def dashboard_command(_, message: types.Message):
    """
    Dashboard management (Admin/Sudo) or Mini App access (All users)
    
    Usage:
        /dashboard - Show dashboard info / Open Mini App
        /dashboard start - Start dashboard server (Sudo only)
        /dashboard stop - Stop dashboard server (Sudo only)
    """
    
    is_sudo = message.from_user.id in app.sudoers or message.from_user.id == config.OWNER_ID
    
    if len(message.command) == 1:
        # For non-sudo users, show Mini App button
        if not is_sudo:
            from os import getenv
            miniapp_url = getenv("WEBAPP_URL", "http://localhost:8000/miniapp")
            
            keyboard = types.InlineKeyboardMarkup([[
                types.InlineKeyboardButton(
                    text="📊 Open Dashboard",
                    web_app=types.WebAppInfo(url=miniapp_url)
                )
            ]])
            
            await message.reply_text(
                "📊 <b>DeltaMusic Dashboard</b>\n\n"
                "<blockquote>Lihat statistik real-time:\n"
                "• 👥 Total Users & Groups\n"
                "• 🎵 Top Tracks & Users\n"
                "• 📈 Play Trends\n"
                "• 🏆 Leaderboards\n\n"
                "Klik tombol di bawah untuk membuka!</blockquote>",
                parse_mode=enums.ParseMode.HTML,
                reply_markup=keyboard
            )
            return
        
        # Show dashboard info for sudo users
        dashboard_url = f"http://localhost:8000"  # Adjust based on your deployment
        
        await message.reply_text(
            f"📊 <b>Statistics Dashboard</b>\n\n"
            f"<blockquote>"
            f"🌐 <b>URL:</b> <code>{dashboard_url}</code>\n\n"
            f"<b>Commands:</b>\n"
            f"• <code>/dashboard start</code> - Start server\n"
            f"• <code>/dashboard stop</code> - Stop server\n\n"
            f"💡 Dashboard shows real-time statistics:\n"
            f"• Top tracks & users\n"
            f"• Active voice calls\n"
            f"• Daily play counts\n"
            f"• Group rankings"
            f"</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Admin-only commands
    if not is_sudo:
        return await message.reply_text(
            "❌ <b>Unauthorized</b>\n\n"
            "<blockquote>This command is for admins only.</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
    
    command = message.command[1].lower()
    
    if command == "start":
        await message.reply_text(
            f"📊 <b>Starting Dashboard Server...</b>\n\n"
            f"<blockquote>Please start the dashboard manually using:\n"
            f"<code>python -m dashboard.server</code>\n\n"
            f"Or use: <code>python dashboard/server.py</code></blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
    
    elif command == "stop":
        await message.reply_text(
            f"📊 <b>Dashboard Server</b>\n\n"
            f"<blockquote>To stop the dashboard, press Ctrl+C in the terminal "
            f"where it's running.</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
    
    else:
        await message.reply_text(
            f"❌ <b>Invalid Command</b>\n\n"
            f"<blockquote>Use: <code>/dashboard start</code> or <code>/dashboard stop</code></blockquote>",
            parse_mode=enums.ParseMode.HTML
        )

