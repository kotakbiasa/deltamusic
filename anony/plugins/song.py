# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import os
from pathlib import Path

from pyrogram import filters, types

from anony import app, config, lang, yt
from anony.helpers import thumb, utils


@app.on_message(filters.command(["song"]) & ~app.bl_users)
@lang.language()
async def song_download(_, m: types.Message):
    """Download and send audio file from YouTube."""
    
    # Check if user provided query or URL
    if len(m.command) < 2:
        await m.reply_text(m.lang["song_usage"])
        return
    
    query = " ".join(m.command[1:])
    sent = await m.reply_text(m.lang["song_searching"])
    
    # Search or get YouTube video info
    if yt.valid(query):
        # Direct URL provided
        file = await yt.search(query, sent.id, video=False)
    else:
        # Search query
        file = await yt.search(query, sent.id, video=False)
    
    if not file:
        await sent.edit_text(
            m.lang["song_not_found"].format(config.SUPPORT_CHANNEL)
        )
        await utils.auto_delete(sent)
        return
    
    # Download the audio
    await sent.edit_text(m.lang["song_downloading"])
    
    # Check if already downloaded
    audio_path = f"downloads/{file.id}.mp3"
    webm_path = f"downloads/{file.id}.webm"
    
    if not Path(audio_path).exists() and not Path(webm_path).exists():
        downloaded_file = await yt.download(file.id, video=False)
        if not downloaded_file:
            await sent.edit_text(
                m.lang["song_not_found"].format(config.SUPPORT_CHANNEL)
            )
            await utils.auto_delete(sent)
            return
        audio_path = downloaded_file
    elif Path(webm_path).exists():
        audio_path = webm_path
    
    # Check file size (50MB = 52428800 bytes)
    file_size = os.path.getsize(audio_path)
    if file_size > 52428800:  # 50MB limit for Telegram audio
        await sent.edit_text(m.lang["song_size_limit"])
        await utils.auto_delete(sent)
        return
    
    # Download thumbnail for audio metadata
    thumb_path = None
    if file.thumbnail:
        try:
            thumb_path = f"cache/{file.id}_thumb.jpg"
            await thumb.save_thumb(thumb_path, file.thumbnail)
        except:
            pass
    
    # Send audio file
    await m.reply_audio(
        audio=audio_path,
        title=file.title,
        performer=file.channel_name or "Unknown Artist",
        duration=file.duration_sec,
        thumb=thumb_path,
        caption=f"🎵 **{file.title}**\n👤 {file.channel_name}\n⏱️ {file.duration}\n\n📥 Diunduh oleh {m.from_user.mention}",
    )
    
    # Delete the status message
    await sent.delete()
    
    # Clean up thumbnail
    if thumb_path and Path(thumb_path).exists():
        try:
            os.remove(thumb_path)
        except:
            pass
