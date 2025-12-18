# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic

"""
Helpers module - Only import modules that don't depend on anony package
"""

# Import Queue class (no anony dependency)
from anony.helpers._queue import Queue

# Import dataclass (no anony dependency usually)
from anony.helpers._dataclass import *

# Note: Other helpers are imported directly where needed to avoid circular imports
# - _cleanup: from anony.helpers._cleanup import cleanup
# - _lyrics: from anony.helpers._lyrics import lyrics_searcher  
# - _decorators: import from anony.helpers._decorators
# - _graceful: import from anony.helpers._graceful
# - _admins: import from anony.helpers._admins
# - _inline: import from anony.helpers._inline
# - _play: import from anony.helpers._play

__all__ = [
    "Queue",
]
