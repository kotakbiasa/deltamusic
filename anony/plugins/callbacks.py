# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import re

from pyrogram import enums, filters, types

from anony import anon, app, db, queue, tg, yt
from anony.helpers import admin_check, buttons, can_manage_vc


@app.on_callback_query(filters.regex("cancel_dl") & ~app.bl_users)
async def cancel_dl(_, query: types.CallbackQuery):
    await query.answer()
    await tg.cancel(query)


@app.on_callback_query(filters.regex("controls") & ~app.bl_users)
@can_manage_vc
async def _controls(_, query: types.CallbackQuery):
    args = query.data.split()
    action, chat_id = args[1], int(args[2])
    q_action = len(args) == 4
    user = query.from_user.mention

    if not await db.get_call(chat_id):
        return await query.answer("Tidak ada streaming yang sedang diputar.", show_alert=True)

    if action == "status":
        return await query.answer()
    await query.answer("Memproses...", show_alert=True)

    if action == "pause":
        if not await db.playing(chat_id):
            return await query.answer(
                "Streaming sudah dijeda!", show_alert=True
            )
        await anon.pause(chat_id)
        if q_action:
            return await query.edit_message_reply_markup(
                reply_markup=buttons.queue_markup(chat_id, "Streaming dijeda", False)
            )
        status = "Streaming dijeda"
        reply = f"{user} menjeda streaming."

    elif action == "resume":
        if await db.playing(chat_id):
            return await query.answer("Streaming tidak dijeda!", show_alert=True)
        await anon.resume(chat_id)
        if q_action:
            return await query.edit_message_reply_markup(
                reply_markup=buttons.queue_markup(chat_id, "Sedang memutar", True)
            )
        reply = f"{user} melanjutkan streaming."

    elif action == "skip":
        await anon.play_next(chat_id)
        status = "Streaming dilewati"
        reply = f"{user} melewati streaming."

    elif action == "force":
        pos, media = queue.check_item(chat_id, args[3])
        if not media or pos == -1:
            return await query.edit_message_text("Lagu ini telah kadaluarsa dari antrian.")

        m_id = queue.get_current(chat_id).message_id
        queue.force_add(chat_id, media, remove=pos)
        try:
            await app.delete_messages(
                chat_id=chat_id, message_ids=[m_id, media.message_id], revoke=True
            )
            media.message_id = None
        except:
            pass

        msg = await app.send_message(chat_id=chat_id, text="Memutar lagu selanjutnya...")
        if not media.file_path:
            media.file_path = await yt.download(media.id, video=media.video)
        media.message_id = msg.id
        return await anon.play_media(chat_id, msg, media)

    elif action == "replay":
        media = queue.get_current(chat_id)
        media.user = user
        await anon.replay(chat_id)
        status = "Streaming diputar ulang"
        reply = f"{user} memutar ulang streaming."

    elif action == "stop":
        await anon.stop(chat_id)
        status = "Streaming dihentikan"
        reply = f"{user} menghentikan streaming."

    try:
        if action in ["skip", "replay", "stop"]:
            await query.message.reply_text(reply, quote=False)
            await query.message.delete()
        else:
            mtext = re.sub(
                r"\n\n<blockquote>.*?</blockquote>",
                "",
                query.message.caption.html or query.message.text.html,
                flags=re.DOTALL,
            )
            keyboard = buttons.controls(
                chat_id, status=status if action != "resume" else None
            )
        await query.edit_message_text(
            f"{mtext}\n\n<blockquote>{reply}</blockquote>", reply_markup=keyboard
        )
    except:
        pass


@app.on_callback_query(filters.regex("help") & ~app.bl_users)
async def _help(_, query: types.CallbackQuery):
    data = query.data.split()
    if len(data) == 1:
        return await query.answer(url=f"https://t.me/{app.username}?start=help")

    if data[1] == "back":
        return await query.edit_message_text(
            text="ℹ️ **Menu Bantuan**\n\nPilih kategori di bawah untuk melihat perintah yang tersedia:", 
            reply_markup=buttons.help_markup({})
        )
    elif data[1] == "close":
        try:
            await query.message.delete()
            return await query.message.reply_to_message.delete()
        except:
            pass

    # Help text mapping - hardcoded from id.json
    help_texts = {
        "help_0": "**Admin Commands**\n\nCommands untuk admin grup.",
        "help_1": "**Auth Commands**\n\nCommands untuk authorization.",
        "help_2": "**Blacklist Commands**\n\nCommands untuk blacklist.",
        "help_3": "**Bahasa Commands**\n\nCommands untuk bahasa.",
        "help_4": "**Ping Commands**\n\nCommands untuk ping.",
        "help_5": "**Play Commands**\n\nCommands untuk memutar musik.",
        "help_6": "**Queue Commands**\n\nCommands untuk queue.",
        "help_7": "**Broadcast Commands**\n\nCommands untuk broadcast.",
        "help_8": "**Sudo Commands**\n\nCommands untuk sudo."
    }
    
    await query.edit_message_text(
        text=help_texts.get(f"help_{data[1]}", "Info tidak tersedia."),
        reply_markup=buttons.help_markup({}, True),
    )


@app.on_callback_query(filters.regex("settings") & ~app.bl_users)
@admin_check
async def _settings_cb(_, query: types.CallbackQuery):
    cmd = query.data.split()
    if len(cmd) == 1:
        return await query.answer()
    await query.answer("Memproses...", show_alert=True)

    chat_id = query.message.chat.id
    _admin = await db.get_play_mode(chat_id)
    _delete = await db.get_cmd_delete(chat_id)
    _language = await db.get_lang(chat_id)

    if cmd[1] == "delete":
        _delete = not _delete
        await db.set_cmd_delete(chat_id, _delete)
    elif cmd[1] == "play":
        await db.set_play_mode(chat_id, _admin)
        _admin = not _admin
    await query.edit_message_reply_markup(
        reply_markup=buttons.settings_markup(
            {},
            _admin,
            _delete,
            _language,
            chat_id,
        )
    )


@app.on_callback_query(filters.regex("donate") & ~app.bl_users)
async def _donate_cb(_, query: types.CallbackQuery):
    """Handle donate button click and show donation info."""
    from anony import config
    
    await query.answer()
    
    donate_text = "✨ **Dukung Bot Musik Tetap Hidup!** ✨\n\nSuka dengan fitur bot ini? Bantu kami agar server tetap menyala dan bot bisa terus memutar musik tanpa henti! 🚀\nDonasi kalian sangat berarti untuk membayar biaya server bulanan kami. 🔌\n\nYuk scan QR di bawah ini untuk donasi! 👇"
    
    await query.message.reply_text(
        text=donate_text,
        parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton(text="🎁 Dukung Kami", url=config.DONATE_QR_IMAGE)]]
        ),
    )
