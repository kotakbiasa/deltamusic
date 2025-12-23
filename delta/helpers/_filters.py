# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

from pyrogram import filters

def _not_blacklisted(_, client, message):
    if not message.from_user:
        return True
    return message.from_user.id not in getattr(client, "bl_users", set())

not_blacklisted = filters.create(_not_blacklisted)


def _is_banned(_, client, message):
    if not message.from_user:
        return False
    return message.from_user.id in getattr(client, "bl_users", set())

BANNED_USERS = filters.create(_is_banned)
