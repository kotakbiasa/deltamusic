# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

"""
Broadcast Module
~~~~~~~~~~~~~~~
Enhanced broadcast functionality with concurrent sending, retry logic,
categorized error handling, and comprehensive progress tracking.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from pyrogram import enums, filters, types
from pyrogram.errors import (
    ChatWriteForbidden,
    FloodWait,
    PeerIdInvalid,
    UserIsBlocked,
)

from delta import app, db

logger = logging.getLogger(__name__)

# ======================== CONFIGURATION ========================

# Performance settings
MAX_CONCURRENT_SENDS = 10  # Maximum concurrent message sends
BATCH_DELAY = 0.3  # Delay between batches (seconds)
RETRY_ATTEMPTS = 3  # Number of retry attempts for failed sends
RETRY_BASE_DELAY = 1.0  # Base delay for exponential backoff (seconds)

# Progress update settings
PROGRESS_UPDATE_INTERVAL = 5  # Update progress every N messages
MIN_UPDATE_DELAY = 2.0  # Minimum seconds between progress updates

# Message templates
HELP_MESSAGE = """ℹ️ <b>Penggunaan Broadcast</b>

<blockquote>Reply ke pesan yang ingin di-broadcast

<b>Default Behavior:</b>
• <code>/broadcast</code> → Kirim ke semua users
• <code>/gcast</code> → Kirim ke semua groups/chats

<b>Flags (opsional):</b>
• <code>-chat</code>: Tambahkan chats/groups ke target
• <code>-user</code>: Tambahkan users ke target
• <code>-copy</code>: Hapus tag forwarded dari pesan
• <code>-pin</code>: Pin status message

<b>Contoh:</b>
• <code>/broadcast -copy</code> → Users saja dengan copy
• <code>/gcast -user -copy</code> → Chats + Users dengan copy
• <code>/broadcast -chat -pin</code> → Users + Chats, pin status</blockquote>"""


# ======================== ENUMS & DATA CLASSES ========================


class ErrorCategory(Enum):
    """Categories of broadcast errors."""
    FORBIDDEN = "forbidden"
    BLOCKED = "blocked"
    FLOOD = "flood"
    INVALID = "invalid"
    OTHER = "other"


@dataclass
class BroadcastStats:
    """Statistics for broadcast operation."""
    total: int = 0
    success: int = 0
    failed: int = 0
    retried: int = 0
    errors_by_category: Dict[ErrorCategory, int] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    
    def add_error(self, category: ErrorCategory) -> None:
        """Add an error to the statistics."""
        self.failed += 1
        self.errors_by_category[category] = self.errors_by_category.get(category, 0) + 1
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time
    
    def get_speed(self) -> float:
        """Get processing speed (messages/second)."""
        elapsed = self.get_elapsed_time()
        processed = self.success + self.failed
        return processed / elapsed if elapsed > 0 else 0.0
    
    def get_eta(self) -> Optional[int]:
        """Get estimated time remaining in seconds."""
        speed = self.get_speed()
        remaining = self.total - (self.success + self.failed)
        return int(remaining / speed) if speed > 0 else None
    
    def get_progress_percentage(self) -> float:
        """Get progress percentage."""
        processed = self.success + self.failed
        return (processed / self.total * 100) if self.total > 0 else 0.0


@dataclass
class BroadcastState:
    """Global state for broadcast control."""
    running: bool = False
    cancelled: bool = False
    stats: Optional[BroadcastStats] = None
    last_update_time: float = 0.0
    
    def reset(self) -> None:
        """Reset state for new broadcast."""
        self.running = False
        self.cancelled = False
        self.stats = None
        self.last_update_time = 0.0


# Global broadcast state
broadcast_state = BroadcastState()


# ======================== HELPER FUNCTIONS ========================


def categorize_error(error: Exception) -> ErrorCategory:
    """Categorize an error for statistics.
    
    Args:
        error: The exception to categorize
        
    Returns:
        ErrorCategory enum value
    """
    if isinstance(error, ChatWriteForbidden):
        return ErrorCategory.FORBIDDEN
    elif isinstance(error, UserIsBlocked):
        return ErrorCategory.BLOCKED
    elif isinstance(error, FloodWait):
        return ErrorCategory.FLOOD
    elif isinstance(error, PeerIdInvalid):
        return ErrorCategory.INVALID
    else:
        return ErrorCategory.OTHER


def format_time(seconds: Optional[int]) -> str:
    """Format seconds into human-readable time.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string (e.g., "2m 30s")
    """
    if seconds is None:
        return "Unknown"
    
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m"


def format_progress_bar(percentage: float, length: int = 20) -> str:
    """Create a text-based progress bar.
    
    Args:
        percentage: Progress percentage (0-100)
        length: Length of the progress bar
        
    Returns:
        Progress bar string
    """
    filled = int(length * percentage / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {percentage:.1f}%"


def format_error_summary(stats: BroadcastStats) -> str:
    """Format error summary for display.
    
    Args:
        stats: Broadcast statistics
        
    Returns:
        Formatted error summary
    """
    if not stats.errors_by_category:
        return ""
    
    error_lines = []
    error_map = {
        ErrorCategory.FORBIDDEN: "🚫 Forbidden",
        ErrorCategory.BLOCKED: "⛔ Blocked",
        ErrorCategory.FLOOD: "⏱️ FloodWait",
        ErrorCategory.INVALID: "❓ Invalid",
        ErrorCategory.OTHER: "⚠️ Other",
    }
    
    for category, count in sorted(stats.errors_by_category.items(), key=lambda x: x[1], reverse=True):
        error_lines.append(f"{error_map.get(category, 'Unknown')}: {count}")
    
    return "\n".join(error_lines)


async def send_with_retry(
    message: types.Message,
    target: int,
    use_copy: bool,
    max_attempts: int = RETRY_ATTEMPTS
) -> Tuple[bool, Optional[ErrorCategory]]:
    """Send message with retry logic.
    
    Args:
        message: Message to send
        target: Target chat/user ID
        use_copy: Whether to copy or forward
        max_attempts: Maximum retry attempts
        
    Returns:
        Tuple of (success: bool, error_category: Optional[ErrorCategory])
    """
    for attempt in range(max_attempts):
        try:
            if use_copy:
                await message.copy(target)
            else:
                await message.forward(target)
            return True, None
        except FloodWait as e:
            if attempt < max_attempts - 1:
                # Wait and retry for FloodWait
                wait_time = min(e.value, 60)  # Cap at 60 seconds
                logger.warning(f"FloodWait {wait_time}s for {target}, waiting...")
                await asyncio.sleep(wait_time)
            else:
                return False, categorize_error(e)
        except Exception as e:
            # For other errors, apply exponential backoff
            if attempt < max_attempts - 1:
                wait_time = RETRY_BASE_DELAY * (2 ** attempt)
                await asyncio.sleep(wait_time)
            else:
                logger.warning(f"Failed to send to {target} after {max_attempts} attempts: {e}")
                return False, categorize_error(e)
    
    return False, ErrorCategory.OTHER


async def broadcast_to_target(
    message: types.Message,
    target: int,
    use_copy: bool,
    stats: BroadcastStats,
    semaphore: asyncio.Semaphore
) -> None:
    """Broadcast to a single target with rate limiting.
    
    Args:
        message: Message to broadcast
        target: Target chat/user ID
        use_copy: Whether to copy or forward
        stats: Statistics tracker
        semaphore: Semaphore for rate limiting
    """
    async with semaphore:
        # Check if broadcast was cancelled
        if broadcast_state.cancelled:
            return
        
        success, error_category = await send_with_retry(message, target, use_copy)
        
        if success:
            stats.success += 1
        elif error_category:
            stats.add_error(error_category)
        
        # Small delay to prevent overwhelming the API
        await asyncio.sleep(BATCH_DELAY)


def format_broadcast_status(
    stats: BroadcastStats,
    is_final: bool = False,
    is_cancelled: bool = False
) -> str:
    """Format broadcast status message.
    
    Args:
        stats: Broadcast statistics
        is_final: Whether this is the final status
        is_cancelled: Whether broadcast was cancelled
        
    Returns:
        Formatted status message
    """
    processed = stats.success + stats.failed
    progress_pct = stats.get_progress_percentage()
    elapsed_time = stats.get_elapsed_time()
    speed = stats.get_speed()
    
    # Header
    if is_cancelled:
        header = "🚫 <b>Broadcast Dibatalkan</b>"
    elif is_final:
        header = "✅ <b>Broadcast Selesai</b>"
    else:
        header = "📡 <b>Broadcasting...</b>"
    
    # Progress bar (only for in-progress)
    progress_section = ""
    if not is_final and not is_cancelled:
        progress_bar = format_progress_bar(progress_pct)
        eta = stats.get_eta()
        eta_str = format_time(eta)
        progress_section = f"\n{progress_bar}\n<b>ETA:</b> {eta_str}\n"
    
    # Stats section
    stats_lines = [
        f"<b>Sukses:</b> {stats.success}",
        f"<b>Gagal:</b> {stats.failed}",
        f"<b>Progress:</b> {processed}/{stats.total}",
    ]
    
    if is_final or is_cancelled:
        stats_lines.append(f"<b>Waktu:</b> {format_time(int(elapsed_time))}")
        stats_lines.append(f"<b>Kecepatan:</b> {speed:.1f} msg/s")
    
    # Error breakdown (only if there are errors)
    error_section = ""
    if stats.failed > 0 and (is_final or is_cancelled):
        error_summary = format_error_summary(stats)
        if error_summary:
            error_section = f"\n\n<b>Error Breakdown:</b>\n{error_summary}"
    
    return (
        f"{header}\n\n"
        f"{progress_section}"
        f"<blockquote>{''.join(f'{line}\\n' for line in stats_lines).rstrip()}"
        f"{error_section}</blockquote>"
    )


async def update_progress(
    message: types.Message,
    stats: BroadcastStats,
    force: bool = False
) -> None:
    """Update progress message.
    
    Args:
        message: Status message to update
        stats: Current statistics
        force: Force update regardless of time constraints
    """
    current_time = time.time()
    time_since_update = current_time - broadcast_state.last_update_time
    
    # Only update if enough time has passed or forced
    if not force and time_since_update < MIN_UPDATE_DELAY:
        return
    
    try:
        status_text = format_broadcast_status(stats)
        await message.edit_text(status_text, parse_mode=enums.ParseMode.HTML)
        broadcast_state.last_update_time = current_time
    except Exception as e:
        logger.debug(f"Failed to update progress: {e}")


# ======================== COMMAND HANDLERS ========================


@app.on_message(filters.command(["broadcast", "gcast"]) & filters.user(app.owner))
async def broadcast_message(_, message: types.Message) -> None:
    """Broadcast message to all chats/users.
    
    Args:
        _: Client instance (unused)
        message: Command message
    """
    # Check if another broadcast is running
    if broadcast_state.running:
        await message.reply_text(
            "⚠️ <b>Broadcast Sedang Berjalan</b>\n\n"
            "<blockquote>Tunggu hingga broadcast sebelumnya selesai atau batalkan dengan /cancelcast</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Validate reply
    if not message.reply_to_message:
        await message.reply_text(HELP_MESSAGE, parse_mode=enums.ParseMode.HTML)
        return
    
    # Parse flags
    flags = message.command[1:] if len(message.command) > 1 else []
    add_chat = "-chat" in flags
    add_user = "-user" in flags
    use_copy = "-copy" in flags
    pin_status = "-pin" in flags
    
    # Determine targets based on command and flags
    targets: List[int] = []
    target_desc: List[str] = []
    
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
    
    # Validate targets
    if not targets:
        await message.reply_text(
            "❌ <b>Tidak Ada Target</b>\n\n"
            "<blockquote>Tidak ada chat atau user yang tersedia untuk broadcast</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Initialize broadcast state
    broadcast_state.running = True
    broadcast_state.cancelled = False
    broadcast_state.stats = BroadcastStats(total=len(targets))
    broadcast_state.last_update_time = time.time()
    
    # Send initial status
    sent = await message.reply_text(
        f"📡 <b>Mempersiapkan Broadcast...</b>\n\n"
        f"<blockquote><b>Target:</b> {', '.join(target_desc)}\n"
        f"<b>Total:</b> {len(targets)}\n"
        f"<b>Mode:</b> {'Copy' if use_copy else 'Forward'}\n"
        f"<b>Concurrent:</b> {MAX_CONCURRENT_SENDS}</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )
    
    # Pin status message if requested
    if pin_status:
        try:
            await sent.pin(disable_notification=True)
        except Exception as e:
            logger.debug(f"Failed to pin message: {e}")
    
    # Create semaphore for rate limiting
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_SENDS)
    
    # Create broadcast tasks
    tasks = [
        broadcast_to_target(
            message.reply_to_message,
            target,
            use_copy,
            broadcast_state.stats,
            semaphore
        )
        for target in targets
    ]
    
    # Process broadcasts with periodic progress updates
    progress_task = None
    try:
        # Create background task for progress updates
        async def progress_updater():
            while broadcast_state.running and not broadcast_state.cancelled:
                await update_progress(sent, broadcast_state.stats)
                await asyncio.sleep(MIN_UPDATE_DELAY)
        
        progress_task = asyncio.create_task(progress_updater())
        
        # Execute all broadcast tasks
        await asyncio.gather(*tasks)
        
    finally:
        # Cancel progress updater
        if progress_task:
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass
        
        # Final status update
        broadcast_state.running = False
        
        status_text = format_broadcast_status(
            broadcast_state.stats,
            is_final=not broadcast_state.cancelled,
            is_cancelled=broadcast_state.cancelled
        )
        
        try:
            await sent.edit_text(status_text, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            logger.error(f"Failed to update final status: {e}")
        
        # Unpin if it was pinned
        if pin_status:
            try:
                await sent.unpin()
            except Exception as e:
                logger.debug(f"Failed to unpin message: {e}")


@app.on_message(filters.command(["cancelcast"]) & filters.user(app.owner))
async def cancel_broadcast(_, message: types.Message) -> None:
    """Cancel ongoing broadcast.
    
    Args:
        _: Client instance (unused)
        message: Command message
    """
    if not broadcast_state.running:
        await message.reply_text(
            "ℹ️ <b>Tidak Ada Broadcast</b>\n\n"
            "<blockquote>Tidak ada broadcast yang sedang berjalan</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    broadcast_state.cancelled = True
    await message.reply_text(
        "⏳ <b>Membatalkan Broadcast...</b>\n\n"
        "<blockquote>Broadcast akan dihentikan. Tunggu sebentar...</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )
