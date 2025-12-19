# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import enums, filters, types

from anony import app, config, db
from anony.helpers import buttons


@app.on_message(filters.command(["settings"]) & filters.group & ~app.bl_users)
async def player_settings(_, message: types.Message):
    """Display player settings panel."""
    chat_id = message.chat.id
    
    # Get current settings
    loop_mode = await db.get_loop_mode(chat_id)
    admin_only = await db.get_play_mode(chat_id)
    cmd_delete = await db.get_cmd_delete(chat_id)
    video_mode = await db.get_video_mode(chat_id)
    video_quality = await db.get_video_quality(chat_id)
    drama_mode = await db.get_drama_mode(chat_id)
    
    # Format loop mode display
    loop_text = {
        "normal": "▶️ Normal",
        "loop_all": "🔁 Loop All",
        "loop_one": "🔂 Loop One"
    }.get(loop_mode, "▶️ Normal")
    
    text = f"""⚙️ <b>Player Settings</b>

<blockquote>🔁 <b>Loop Mode:</b> {loop_text}
📹 <b>Video Mode:</b> {'✅ Aktif' if video_mode else '❌ Nonaktif'}
🎬 <b>Kualitas:</b> 📺 {video_quality}
👮 <b>Admin Only:</b> {'✅ Aktif' if admin_only else '❌ Nonaktif'}
🗑 <b>Auto Delete:</b> {'✅ Aktif' if cmd_delete else '❌ Nonaktif'}
🎭 <b>Drama (Admin):</b> {'✅ Aktif' if drama_mode else '❌ Nonaktif'}</blockquote>

<i>Klik tombol di bawah untuk mengubah pengaturan</i>"""
    
    await message.reply_text(
        text,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=buttons.player_settings_markup(loop_mode, admin_only, cmd_delete, video_mode, video_quality, drama_mode, chat_id)
    )

