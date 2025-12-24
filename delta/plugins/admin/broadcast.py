# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import asyncio
import logging

from pyrogram import enums, filters, types

from delta import app, db

logger = logging.getLogger(__name__)

# Global state for broadcast control
broadcast_state = {
    "running": False,
    "cancelled": False
}


@app.on_message(filters.command(["broadcast", "gcast"]) & filters.user(app.owner))
async def broadcast_message(_, message: types.Message):
    """Broadcast message to all chats/users."""
    
    # Check if another broadcast is running
    if broadcast_state["running"]:
        return await message.reply_text(
            "⚠️ <b>Broadcast Sedang Berjalan</b>\n\n<blockquote>Tunggu hingga broadcast sebelumnya selesai atau batalkan dengan /cancelcast</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
    
    if not message.reply_to_message:
        return await message.reply_text(
            "ℹ️ <b>Penggunaan Broadcast</b>\n\n"
            "<blockquote>Reply ke pesan yang ingin di-broadcast\n\n"
            "<b>Default Behavior:</b>\n"
            "• <code>/broadcast</code> → Kirim ke semua users\n"
            "• <code>/gcast</code> → Kirim ke semua groups/chats\n\n"
            "<b>Flags (opsional):</b>\n"
            "• <code>-chat</code>: Tambahkan chats/groups ke target\n"
            "• <code>-user</code>: Tambahkan users ke target\n"
            "• <code>-copy</code>: Hapus tag forwarded dari pesan\n\n"
            "<b>Contoh:</b>\n"
            "• <code>/broadcast -copy</code> → Users saja dengan copy\n"
            "• <code>/gcast -user -copy</code> → Chats + Users dengan copy\n"
            "• <code>/broadcast -chat</code> → Users + Chats</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
    
    # Parse flags
    flags = message.command[1:] if len(message.command) > 1 else []
    add_chat = "-chat" in flags
    add_user = "-user" in flags
    use_copy = "-copy" in flags
    
    # Determine targets based on command and flags
    targets = []
    target_desc = []
    
    # Default behavior
    if message.command[0] == "gcast":
        # gcast defaults to chats
        chats = await db.get_chats()
        targets.extend(chats)
        target_desc.append(f"{len(chats)} chats")
        
        # Add users if -user flag present
        if add_user:
            users = await db.get_users()
            targets.extend(users)
            target_desc.append(f"{len(users)} users")
    else:
        # broadcast defaults to users
        users = await db.get_users()
        targets.extend(users)
        target_desc.append(f"{len(users)} users")
        
        # Add chats if -chat flag present
        if add_chat:
            chats = await db.get_chats()
            targets.extend(chats)
            target_desc.append(f"{len(chats)} chats")
    
    if not targets:
        return await message.reply_text(
            "❌ <b>Tidak Ada Target</b>\n\n<blockquote>Tidak ada chat atau user yang tersedia untuk broadcast</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
    
    # Initialize broadcast state
    broadcast_state["running"] = True
    broadcast_state["cancelled"] = False
    
    sent = await message.reply_text(
        f"📡 <b>Broadcasting...</b>\n\n"
        f"<blockquote><b>Target:</b> {', '.join(target_desc)}\n"
        f"<b>Total:</b> {len(targets)}\n"
        f"<b>Mode:</b> {'Copy' if use_copy else 'Forward'}</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )
    
    success = 0
    failed = 0
    
    for idx, target in enumerate(targets, 1):
        # Check if cancelled
        if broadcast_state["cancelled"]:
            await sent.edit_text(
                f"🚫 <b>Broadcast Dibatalkan</b>\n\n"
                f"<blockquote><b>Sukses:</b> {success}\n"
                f"<b>Gagal:</b> {failed}\n"
                f"<b>Tersisa:</b> {len(targets) - idx + 1}</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
            broadcast_state["running"] = False
            return
        
        try:
            if use_copy:
                await message.reply_to_message.copy(target)
            else:
                await message.reply_to_message.forward(target)
            success += 1
        except Exception as e:
            failed += 1
            logger.warning(f"Failed to broadcast to {target}: {e}")
        
        # Update progress every 10 messages
        if idx % 10 == 0 or idx == len(targets):
            try:
                await sent.edit_text(
                    f"📡 <b>Broadcasting...</b>\n\n"
                    f"<blockquote><b>Progress:</b> {idx}/{len(targets)}\n"
                    f"<b>Sukses:</b> {success}\n"
                    f"<b>Gagal:</b> {failed}</blockquote>",
                    parse_mode=enums.ParseMode.HTML
                )
            except:
                pass
        
        # Anti-flood delay
        await asyncio.sleep(0.5)
    
    # Final status
    broadcast_state["running"] = False
    await sent.edit_text(
        f"✅ <b>Broadcast Selesai</b>\n\n"
        f"<blockquote><b>Sukses:</b> {success}\n"
        f"<b>Gagal:</b> {failed}\n"
        f"<b>Total:</b> {len(targets)}</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )


@app.on_message(filters.command(["cancelcast"]) & filters.user(app.owner))
async def cancel_broadcast(_, message: types.Message):
    """Cancel ongoing broadcast."""
    if not broadcast_state["running"]:
        return await message.reply_text(
            "ℹ️ <b>Tidak Ada Broadcast</b>\n\n<blockquote>Tidak ada broadcast yang sedang berjalan</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
    
    broadcast_state["cancelled"] = True
    await message.reply_text(
        "⏳ <b>Membatalkan Broadcast...</b>\n\n<blockquote>Broadcast akan dihentikan setelah pesan saat ini selesai</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )
