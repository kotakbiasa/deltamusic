# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import filters, types

from anony import app, config, yt


@app.on_message(filters.command(["song", "mp3"]) & ~app.bl_users)
async def song_command(_, message: types.Message):
    """Download and send MP3 audio from YouTube."""
    
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>Penggunaan:</b>\n\n<code>/song charlie puth attention</code>\natau\n<code>/song https://youtu.be/VIDEO_ID</code>"
        )
    
    query = message.text.split(None, 1)[1]
    m = await message.reply_text("Mencari lagu...")
    
    try:
        search = await yt.search(query)
        if not search:
            return await m.edit_text("Gagal menemukan atau mengunduh lagu.\n\nJika masalah berlanjut, laporkan ke <a href={}>chat dukungan</a>.".format(config.SUPPORT_CHANNEL))
        
        track = search[0]
        await m.edit_text("Mengunduh audio...")
        
        file_path = await yt.download(track.id, video=False)
        if not file_path:
            return await m.edit_text("Gagal menemukan atau mengunduh lagu.\n\nJika masalah berlanjut, laporkan ke <a href={}>chat dukungan</a>.".format(config.SUPPORT_CHANNEL))
        
        # Check file size
        import os
        file_size = os.path.getsize(file_path)
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            os.remove(file_path)
            return await m.edit_text("File audio terlalu besar (maksimum 50MB).\n\nCoba lagu dengan durasi lebih pendek.")
        
        await message.reply_audio(
            audio=file_path,
            title=track.title,
            performer=track.title,
            duration=track.duration,
            thumb=track.thumb
        )
        await m.delete()
        
        # Cleanup
        try:
            os.remove(file_path)
        except:
            pass
            
    except Exception as e:
        await m.edit_text(f"Error: {str(e)}")
