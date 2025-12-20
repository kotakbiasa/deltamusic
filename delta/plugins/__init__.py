# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


from pathlib import Path

def _list_modules():
    """
    List all Python module filenames (without extension) from current directory
    and all subdirectories, excluding __init__.py files.

    Returns:
        list: A list of module names as strings.
    """
    mod_dir = Path(__file__).parent
    modules = []
    
    # Get modules from root plugins directory
    for file in mod_dir.glob("*.py"):
        if file.is_file() and file.name != "__init__.py":
            modules.append(file.stem)
    
    # Get modules from subdirectories (playback, admin, user, core)
    for subdir in mod_dir.iterdir():
        if subdir.is_dir() and not subdir.name.startswith("__"):
            for file in subdir.glob("*.py"):
                if file.is_file() and file.name != "__init__.py":
                    # Include subdirectory in module name (e.g., "playback.play")
                    modules.append(f"{subdir.name}.{file.stem}")
    
    return modules

all_modules = frozenset(sorted(_list_modules()))
