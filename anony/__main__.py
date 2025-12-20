# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import asyncio
import importlib

from pyrogram import idle

from anony import (anon, app, config, db,
                   logger, stop, userbot, yt, tasks)
from anony.plugins import all_modules


async def main():
    await db.connect()
    
    # Startup banner
    logger.info("🎵 ═══════════ DELTA MUSIC BOT v3.0.1 ═══════════ 🎵")
    logger.info("⚡ Initializing bot components...")
    
    await app.boot()
    await userbot.boot()
    await anon.boot()

    for module in all_modules:
        importlib.import_module(f"anony.plugins.{module}")
    logger.info(f"Loaded {len(all_modules)} modules.")

    if config.COOKIES_URL:
        await yt.save_cookies(config.COOKIES_URL)

    sudoers = await db.get_sudoers()
    app.sudoers.update(sudoers)
    app.bl_users.update(await db.get_blacklisted())
    logger.info(f"👥 Loaded {len(app.sudoers)} sudo users.")
    
    # Start cleanup scheduler (import directly to avoid circular import)
    from anony.helpers._cleanup import cleanup
    cleanup_task = asyncio.create_task(cleanup.start())
    tasks.append(cleanup_task)
    logger.info("🧹 File cleanup scheduler started")

    # Start Dashboard Server
    try:
        from anony.dashboard.server import run_dashboard_server
        dashboard_task = asyncio.create_task(run_dashboard_server())
        tasks.append(dashboard_task)
        logger.info("📊 Dashboard server task started")
    except ImportError:
        logger.warning("⚠️ Dashboard module not found, skipping dashboard startup")
    except Exception as e:
        logger.error(f"❌ Failed to start dashboard: {e}")
    
    logger.info("✅ Bot is ready and running!")
    logger.info("🎵 ═══════════════════════════════════════════════ 🎵")

    await idle()
    await stop()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
