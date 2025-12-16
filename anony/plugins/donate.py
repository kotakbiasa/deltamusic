# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import app, config


@app.on_message(filters.command(["donate"]))
async def donate_command(_, message: types.Message):
    """Show donate information with QR code link."""
    donate_text = (
        "💰 **Dukung Kami!**\n\n"
        "Terima kasih atas dukungan Anda untuk terus mengembangkan bot ini.\n\n"
        "Klik tombol di bawah untuk melihat QR code donasi:"
    )
    
    await message.reply_text(
        text=donate_text,
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton(text="💳 Lihat QR Donasi", url=config.DONATE_LINK)]]
        ),
        quote=True,
    )
