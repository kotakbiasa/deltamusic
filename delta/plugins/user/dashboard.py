# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

"""
Dashboard Admin Commands - Control dashboard from Telegram
"""

from pyrogram import enums, filters, types

from delta import app, config, logger


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
    
    if not is_sudo:
        # Non-sudo users always see Mini App button
        from os import getenv
        miniapp_url = getenv("WEBAPP_URL", "http://localhost:8000/miniapp")
        
        keyboard = types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton(
                text="📊 Open Dashboard",
                web_app=types.WebAppInfo(url=miniapp_url)
            )
        ]])
        
        await message.reply_text(
            f"📊 <b>{app.name} Dashboard</b>\n\n"
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

    # Sudo users get the Admin Dashboard Info
    # Sudo users get the Admin Dashboard Info
    from os import getenv
    dashboard_url = getenv("DASHBOARD_URL", "http://localhost:8000")
    
    keyboard = types.InlineKeyboardMarkup([[
        types.InlineKeyboardButton(
            text="🌐 Open Dashboard",
            url=dashboard_url
        )
    ]])
    
    await message.reply_text(
        f"📊 <b>{app.name} Dashboard</b>\n\n"
        f"<blockquote>"
        f"✅ <b>Status:</b> Premium (Auto-Started)\n\n"
        f"💡 <b>Features:</b>\n"
        f"• Real-time analytics\n"
        f"• Top tracks & active calls\n"
        f"• User & Group rankings"
        f"</blockquote>",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=keyboard
    )

