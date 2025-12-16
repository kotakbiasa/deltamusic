# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pyrogram import types

from anony import app, config, lang
from anony.core.lang import lang_codes


class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton

    def cancel_dl(self, text) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, callback_data=f"cancel_dl")]])

    def controls(
        self,
        chat_id: int,
        status: str = None,
        timer: str = None,
        remove: bool = False,
    ) -> types.InlineKeyboardMarkup:
        keyboard = []
        if status:
            keyboard.append(
                [self.ikb(text=status, callback_data=f"controls status {chat_id}")]
            )
        elif timer:
            keyboard.append(
                [self.ikb(text=timer, callback_data=f"controls status {chat_id}")]
            )

        if not remove:
            keyboard.append(
                [
                    self.ikb(text="▷", callback_data=f"controls resume {chat_id}"),
                    self.ikb(text="II", callback_data=f"controls pause {chat_id}"),
                    self.ikb(text="⥁", callback_data=f"controls replay {chat_id}"),
                    self.ikb(text="‣‣I", callback_data=f"controls skip {chat_id}"),
                    self.ikb(text="▢", callback_data=f"controls stop {chat_id}"),
                ]
            )
        return self.ikm(keyboard)

    def stats_buttons(self, _lang: dict, is_sudo: bool = False) -> types.InlineKeyboardMarkup:
        """Main stats menu buttons."""
        keyboard = [
            [
                self.ikb(text="🎵 Top Tracks", callback_data="GetStatsNow Tracks"),
                self.ikb(text="👥 Top Users", callback_data="GetStatsNow Users"),
            ],
            [
                self.ikb(text="📢 Top Groups", callback_data="GetStatsNow Chats"),
                self.ikb(text="📊 This Group", callback_data="GetStatsNow Here"),
            ],
            [
                self.ikb(text="🤖 Bot Info", callback_data="TopOverall s"),
            ],
        ]
        if is_sudo:
            keyboard.append([
                self.ikb(text="⚙️ System Info", callback_data="bot_stats_sudo s"),
            ])
        return self.ikm(keyboard)

    def back_stats_markup(self, _lang: dict) -> types.InlineKeyboardMarkup:
        """Back button for stats."""
        return self.ikm([[self.ikb(text="« Kembali", callback_data="stats_back")]])

    def overall_stats_markup(self, _lang: dict, main: bool = False) -> types.InlineKeyboardMarkup:
        """Overall stats navigation."""
        if main:
            return self.ikm([[self.ikb(text="« Kembali", callback_data="stats_back")]])
        return self.ikm([[
            self.ikb(text="« Kembali", callback_data="TopOverall s")
        ]])

    def help_markup(
        self, _lang: dict, back: bool = False
    ) -> types.InlineKeyboardMarkup:
        if back:
            rows = [
                [
                    self.ikb(text=_lang["back"], callback_data="help back"),
                    self.ikb(text=_lang["close"], callback_data="help close"),
                ]
            ]
        else:
            # Language button removed - Indonesian only
            # Manual mapping to skip help_3 (Bahasa)
            help_map = [
                ("admins", "help_0"),
                ("auth", "help_1"),
                ("blist", "help_2"),
                # help_3 (Bahasa) - SKIPPED
                ("ping", "help_4"),
                ("play", "help_5"),
                ("queue", "help_6"),
                ("stats", "help_7"),
                ("sudo", "help_8"),
            ]
            buttons = [
                self.ikb(text=_lang[help_key], callback_data=f"help {cb}")
                for cb, help_key in help_map
            ]
            rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]

        return self.ikm(rows)

    def lang_markup(self, _lang: str) -> types.InlineKeyboardMarkup:
        langs = lang.get_languages()

        buttons = [
            self.ikb(
                text=f"{name} ({code}) {'✔️' if code == _lang else ''}",
                callback_data=f"lang_change {code}",
            )
            for code, name in langs.items()
        ]
        rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
        return self.ikm(rows)

    def ping_markup(self, text: str) -> types.InlineKeyboardMarkup:
        return self.ikm([[self.ikb(text=text, url=config.SUPPORT_CHANNEL)]])

    def play_queued(
        self, chat_id: int, item_id: str, _text: str
    ) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(
                        text=_text, callback_data=f"controls force {chat_id} {item_id}"
                    )
                ]
            ]
        )

    def queue_markup(
        self, chat_id: int, _text: str, playing: bool
    ) -> types.InlineKeyboardMarkup:
        _action = "pause" if playing else "resume"
        return self.ikm(
            [[self.ikb(text=_text, callback_data=f"controls {_action} {chat_id} q")]]
        )

    def settings_markup(
        self, lang: dict, admin_only: bool, cmd_delete: bool, language: str, chat_id: int
    ) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(
                        text=lang["play_mode"] + " ➜",
                        callback_data="settings",
                    ),
                    self.ikb(text=admin_only, callback_data="settings play"),
                ],
                [
                    self.ikb(
                        text=lang["cmd_delete"] + " ➜",
                        callback_data="settings",
                    ),
                    self.ikb(text=cmd_delete, callback_data="settings delete"),
                ],
                # Language option removed - Indonesian only
            ]
        )

    def start_key(
        self, lang: dict, private: bool = False
    ) -> types.InlineKeyboardMarkup:
        rows = [
            [
                self.ikb(
                    text=lang["add_me"],
                    url=f"https://t.me/{app.username}?startgroup=true",
                )
            ],
            [self.ikb(text=lang["help"], callback_data="help")],
            [
                self.ikb(text=lang["channel"], url=config.SUPPORT_CHANNEL),
                self.ikb(text=lang["donate"], callback_data="donate"),
            ],
        ]
        if private:
            # Source button removed
            pass
        else:
            # Language button removed - Indonesian only
            pass
        return self.ikm(rows)

    def yt_key(self, link: str) -> types.InlineKeyboardMarkup:
        return self.ikm(
            [
                [
                    self.ikb(text="❐", copy_text=link),
                    self.ikb(text="Youtube", url=link),
                ],
            ]
        )
