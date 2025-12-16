# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import app, db


@app.on_message(filters.command(["blacklist", "unblacklist"]) & ~app.bl_users)
@app.only_sudoers
async def blacklist_cmd(_, message: types.Message):
    """Blacklist/unblacklist a user or chat."""
    
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>Penggunaan:</b>\n\n/blacklist [chat_id|user_id]"
        )
    
    try:
        target_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("Hanya chat ID dan user ID yang didukung.")
    
    is_blacklist = message.command[0] == "blacklist"
    
    if is_blacklist:
        if target_id in app.bl_users or target_id in db.blacklisted:
            return await message.reply_text("Chat ini sudah ada di daftar hitam.")
        await db.add_blacklist(target_id)
        app.bl_users.append(target_id)
        await message.reply_text("Chat ini telah ditambahkan ke daftar hitam.")
    else:
        if target_id not in app.bl_users and target_id not in db.blacklisted:
            return await message.reply_text("Chat ini tidak ada di daftar hitam.")
        await db.del_blacklist(target_id)
        if target_id in app.bl_users:
            app.bl_users.remove(target_id)
        await message.reply_text("Chat ini telah dihapus dari daftar hitam.")
