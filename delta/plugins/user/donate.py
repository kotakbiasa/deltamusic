# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import enums, filters, types

from delta import app, config


@app.on_message(filters.command(["donate"]) & filters.private & ~app.bl_users)
async def donate_command(_, message: types.Message):
    """Donate command handler."""
    donate_text = "✨ <b>Dukung Bot Musik Tetap Hidup!</b> ✨\n\n<blockquote>Suka dengan fitur bot ini? Bantu kami agar server tetap menyala dan bot bisa terus memutar musik tanpa henti! 🚀\nDonasi kalian sangat berarti untuk membayar biaya server bulanan kami. 🔌</blockquote>\n\nYuk scan QR di bawah ini untuk donasi! 👇"
    
    await message.reply_text(
        text=donate_text,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton(text="🎁 Dukung Kami", url=config.DONATE_QR_IMAGE)]]
        ),
        quote=True,
    )
