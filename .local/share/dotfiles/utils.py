import os
import sys
import shutil
import platform

# Platform constants
PLATFORM_DARWIN = 1
PLATFORM_LINUX = 2
PLATFORM_ANY = 3

def get_current_platform():
    """Determines the current platform code."""
    system = platform.system().lower()
    if system == 'darwin':
        return PLATFORM_DARWIN
    elif system == 'linux':
        return PLATFORM_LINUX
    else:
        # Consider other systems as unsupported for platform-specific actions
        # but allow PLATFORM_ANY
        return 0 # Or raise an error if you prefer stricter handling

def _log(name, message):
    """Helper function for logging."""
    print(f"[bootstrap/{name}] {message}")

def _resolve_path(path):
    """Expands ~ and makes path absolute."""
    return os.path.abspath(os.path.expanduser(path))

def _handle_link(name, source, target, current_platform, platform_flag): # <-- Added platform_flag parameter
    """Handles the linking logic for a single entry."""
    source_abs = _resolve_path(source)
    target_abs = _resolve_path(target)
    
    # Check platform compatibility using the PASSED argument
    if platform_flag != PLATFORM_ANY and platform_flag != current_platform:
        _log(name, f"Skipping link {target} (platform mismatch)")
        return

    _log(name, f"Linking {target_abs} -> {source_abs}")

    # Ensure source exists
    if not os.path.exists(source_abs):
        _log(name, f"ERROR: Source path does not exist: {source_abs}")
        return

    # Ensure target directory exists
    target_dir = os.path.dirname(target_abs)
    try:
        os.makedirs(target_dir, exist_ok=True)
    except OSError as e:
        _log(name, f"ERROR: Could not create directory {target_dir}: {e}")
        return

    # Handle existing target (force linking)
    if os.path.lexists(target_abs): # Use lexists to check for broken symlinks too
        try:
            # Check if it's a directory trying to be overwritten by a file link or vice-versa
            # Although os.remove/unlink should handle this, logging can be useful
            if os.path.isdir(target_abs) and not os.path.islink(target_abs) and os.path.isfile(source_abs):
                 _log(name, f"WARNING: Target {target_abs} is a directory, removing to link a file.")
            elif os.path.isfile(target_abs) and not os.path.islink(target_abs) and os.path.isdir(source_abs):
                 _log(name, f"WARNING: Target {target_abs} is a file, removing to link a directory.")
            
            # Remove existing file or link
            if os.path.islink(target_abs) or os.path.isfile(target_abs):
                 os.remove(target_abs)
                 _log(name, f"Removed existing target: {target_abs}")
            elif os.path.isdir(target_abs) and not os.path.islink(target_abs): # Check it's a real directory, not a link to one
                 # Safety check: generally avoid auto-removing directories unless intended
                 # If you want to replace a directory with a link TO a directory, 
                 # shutil.rmtree might be needed, but handle with extreme care.
                 # For now, we'll error if trying to replace a dir with a link.
                 # If the source is also a directory, symlinking should work fine
                 # without removing the target dir first if the target name doesn't conflict.
                 # However, the explicit request is to FORCE the link. Let's remove it.
                 _log(name, f"INFO: Target {target_abs} is a directory. Attempting to remove for linking.")
                 shutil.rmtree(target_abs) # Be careful with this!
                 _log(name, f"Removed existing directory: {target_abs}")

        except OSError as e:
            _log(name, f"ERROR: Could not remove existing target {target_abs}: {e}")
            return

    # Create the symbolic link
    try:
        os.symlink(source_abs, target_abs, target_is_directory=os.path.isdir(source_abs)) # Add target_is_directory for Windows compatibility if needed, fine on Unix.
        _log(name, f"Successfully linked {target_abs} -> {source_abs}")
    except OSError as e:
        _log(name, f"ERROR: Could not create symlink {target_abs}: {e}")
    except Exception as e:
        _log(name, f"ERROR: An unexpected error occurred during linking {target_abs}: {e}")


def _handle_copy(name, source, target, current_platform, platform_flag):
    """Handles the copying logic for a single entry."""
    source_abs = _resolve_path(source)
    target_abs = _resolve_path(target)

    # Check platform compatibility
    if platform_flag != PLATFORM_ANY and platform_flag != current_platform:
        _log(name, f"Skipping copy {target} (platform mismatch)")
        return

    _log(name, f"Preparing to copy {target_abs} <- {source_abs}")

    # Ensure source exists
    if not os.path.exists(source_abs):
        _log(name, f"ERROR: Source path does not exist: {source_abs}")
        return
        
    # Ensure target directory exists
    target_dir = os.path.dirname(target_abs)
    try:
        os.makedirs(target_dir, exist_ok=True)
    except OSError as e:
        _log(name, f"ERROR: Could not create directory {target_dir}: {e}")
        return

    # Ask for user confirmation
    prompt = f"Copy '{os.path.basename(source_abs)}' to '{target_abs}'?"
    if os.path.exists(target_abs):
        prompt += " (Target exists and will be overwritten)"
    prompt += " [Y/n]: "

    try:
        user_input = input(prompt).strip().lower()
    except EOFError: # Handle non-interactive environments gracefully
        user_input = 'n'
        _log(name, "Non-interactive mode detected, skipping copy confirmation.")


    if user_input == '' or user_input == 'y' or user_input == 'yes':
        try:
             # Remove existing file/dir before copying if necessary
            if os.path.lexists(target_abs):
                if os.path.isdir(target_abs) and not os.path.islink(target_abs):
                    shutil.rmtree(target_abs)
                    _log(name, f"Removed existing directory: {target_abs}")
                elif os.path.isfile(target_abs) or os.path.islink(target_abs):
                     os.remove(target_abs)
                     _log(name, f"Removed existing file/link: {target_abs}")

            # Perform the copy (copy2 preserves metadata like permissions)
            if os.path.isdir(source_abs):
                shutil.copytree(source_abs, target_abs, symlinks=True) # copy dirs recursively
            else:
                shutil.copy2(source_abs, target_abs) 
            _log(name, f"Successfully copied {target_abs} <- {source_abs}")
        except OSError as e:
            _log(name, f"ERROR: Could not copy {source_abs} to {target_abs}: {e}")
        except Exception as e:
            _log(name, f"ERROR: An unexpected error occurred during copying {target_abs}: {e}")

    else:
        _log(name, f"Skipped copy {target_abs} by user request.")

# The main function called by .strap files
def process_config(config):
    """
    Processes the configuration dictionary to link and copy files.

    Args:
        config (dict): A dictionary with the following structure:
            {
                'name': str,          # Name for logging scope (e.g., 'zsh', 'nvim')
                'link': [            # List of items to symlink
                    [source, target, platform_flag], ...
                ],
                'copy': [            # List of items to copy
                    [source, target, platform_flag], ...
                ]
            }
          source: Relative path from the .strap file OR an absolute path.
          target: Destination path (use ~ for home directory).
          platform_flag: 1 (Darwin), 2 (Linux), 3 (Any).
    """
    if not isinstance(config, dict):
        print("[bootstrap/utils] ERROR: Invalid config format - must be a dictionary.")
        return

    name = config.get('name', 'unknown')
    link_tasks = config.get('link', [])
    copy_tasks = config.get('copy', [])

    if not isinstance(link_tasks, list):
         print(f"[bootstrap/{name}] ERROR: Invalid 'link' format - must be a list.")
         link_tasks = []
    if not isinstance(copy_tasks, list):
        print(f"[bootstrap/{name}] ERROR: Invalid 'copy' format - must be a list.")
        copy_tasks = []


    current_platform = get_current_platform()
    _log(name, f"Processing on platform: {platform.system()} ({current_platform})")

    # Process links
    for entry in link_tasks:
        if isinstance(entry, (list, tuple)) and len(entry) == 3:
            source, target, platform_flag = entry
            if isinstance(source, str) and isinstance(target, str) and isinstance(platform_flag, int):
                 _handle_link(name, source, target, current_platform, platform_flag)
            else:
                 _log(name, f"ERROR: Invalid link entry format: {entry}. Must be [str, str, int].")

        else:
            _log(name, f"ERROR: Invalid link entry format: {entry}. Must be a list/tuple of 3 elements.")

    # Process copies
    for entry in copy_tasks:
        if isinstance(entry, (list, tuple)) and len(entry) == 3:
            source, target, platform_flag = entry
            if isinstance(source, str) and isinstance(target, str) and isinstance(platform_flag, int):
                _handle_copy(name, source, target, current_platform, platform_flag)
            else:
                _log(name, f"ERROR: Invalid copy entry format: {entry}. Must be [str, str, int].")
        else:
             _log(name, f"ERROR: Invalid copy entry format: {entry}. Must be a list/tuple of 3 elements.")

    _log(name, "Processing finished.")

# --- Example Usage (for testing utils.py directly) ---
if __name__ == "__main__":
    print("Testing utils.py...")
    # Create dummy files/dirs for testing relative paths
    test_dir = "_util_test"
    os.makedirs(os.path.join(test_dir, "source_files"), exist_ok=True)
    with open(os.path.join(test_dir, "source_files", "test_link_src.txt"), "w") as f:
        f.write("link source")
    with open(os.path.join(test_dir, "source_files", "test_copy_src.txt"), "w") as f:
        f.write("copy source")
    os.makedirs(os.path.join(test_dir, "source_files", "test_dir_src"), exist_ok=True)
    with open(os.path.join(test_dir, "source_files", "test_dir_src", "dummy.txt"), "w") as f:
        f.write("in dir")


    test_config = {
        'name': 'test',
        'link': [
            # Relative source from this test script location
            ['./_util_test/source_files/test_link_src.txt', '~/.config/dotfiles_test/test_link_target.txt', 3],
             ['./_util_test/source_files/test_dir_src', '~/.config/dotfiles_test/test_dir_target_link', 3], # Link a dir
        ],
        'copy': [
            ['./_util_test/source_files/test_copy_src.txt', '~/.config/dotfiles_test/test_copy_target.txt', 3],
        ]
    }
    process_config(test_config)
    print("\nTest finished. Check '~/.config/dotfiles_test/' for results.")
    # Clean up dummy files - uncomment carefully after verifying
    # print("Cleaning up test files...")
    # target_test_dir = os.path.expanduser('~/.config/dotfiles_test')
    # if os.path.exists(target_test_dir):
    #      shutil.rmtree(target_test_dir)
    # if os.path.exists(test_dir):
    #      shutil.rmtree(test_dir)
    # print("Cleanup done.")


