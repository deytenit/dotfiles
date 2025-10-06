import os
import sys
import shutil
import platform
import subprocess
import tempfile
import re

# Platform constants
PLATFORM_DARWIN = 1
PLATFORM_LINUX = 2
PLATFORM_ANY = 3

# Cron management markers
CRON_BEGIN_MARKER = "# BEGIN DEYTENIT DOTFILES STRAP CRON"
CRON_END_MARKER = "# END DEYTENIT DOTFILES STRAP CRON"

# Global list to collect cron entries from all strap files
COLLECTED_CRON_ENTRIES = []

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

def _validate_cron_time(time_expr):
    """
    Validates a cron time expression.
    
    Args:
        time_expr (str): Cron time expression (e.g., "0 * * * *")
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not isinstance(time_expr, str):
        return False, "Time expression must be a string"
    
    parts = time_expr.strip().split()
    if len(parts) != 5:
        return False, f"Cron time expression must have 5 fields, got {len(parts)}"
    
    # Basic validation for each field
    # Minute (0-59), Hour (0-23), Day of Month (1-31), Month (1-12), Day of Week (0-7)
    ranges = [(0, 59), (0, 23), (1, 31), (1, 12), (0, 7)]
    field_names = ["minute", "hour", "day of month", "month", "day of week"]
    
    for i, (part, (min_val, max_val), field_name) in enumerate(zip(parts, ranges, field_names)):
        # Allow special characters: * , - /
        if part == '*':
            continue
        
        # Check for step values (*/n)
        if '/' in part:
            base, step = part.split('/', 1)
            if base != '*' and not base.isdigit():
                # Could be a range like 1-5/2
                if '-' not in base:
                    return False, f"Invalid {field_name} field: {part}"
            if not step.isdigit():
                return False, f"Invalid step value in {field_name} field: {part}"
            continue
        
        # Check for ranges (n-m)
        if '-' in part:
            try:
                start, end = part.split('-', 1)
                start_num = int(start)
                end_num = int(end)
                if start_num < min_val or end_num > max_val or start_num > end_num:
                    return False, f"Invalid range in {field_name} field: {part} (should be {min_val}-{max_val})"
            except ValueError:
                return False, f"Invalid range in {field_name} field: {part}"
            continue
        
        # Check for lists (n,m,o)
        if ',' in part:
            try:
                values = [int(v) for v in part.split(',')]
                if any(v < min_val or v > max_val for v in values):
                    return False, f"Invalid value in {field_name} list: {part} (should be {min_val}-{max_val})"
            except ValueError:
                return False, f"Invalid list in {field_name} field: {part}"
            continue
        
        # Check for simple numeric value
        try:
            value = int(part)
            if value < min_val or value > max_val:
                return False, f"Invalid {field_name} value: {value} (should be {min_val}-{max_val})"
        except ValueError:
            return False, f"Invalid {field_name} field: {part}"
    
    return True, None

def _validate_cron_entry(name, time_expr, command):
    """
    Validates a complete cron entry.
    
    Args:
        name (str): Name for logging
        time_expr (str): Cron time expression
        command (str): Command to execute
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    # Validate time expression
    is_valid, error_msg = _validate_cron_time(time_expr)
    if not is_valid:
        return False, error_msg
    
    # Validate command
    if not isinstance(command, str) or not command.strip():
        return False, "Command must be a non-empty string"
    
    # Expand ~ in command for path validation
    expanded_command = os.path.expanduser(command)
    
    # Check if command looks like a script path (starts with / or ~)
    if command.startswith('/') or command.startswith('~'):
        script_path = expanded_command.split()[0]  # Get first part (the script path)
        if not os.path.exists(script_path):
            _log(name, f"WARNING: Script path does not exist: {script_path}")
            # Don't fail, just warn - the script might be created later
    
    return True, None

def _handle_cron(name, time_expr, command, current_platform, platform_flag):
    """
    Handles the cron entry validation and collection.
    
    Args:
        name (str): Name for logging
        time_expr (str): Cron time expression
        command (str): Command to execute
        current_platform (int): Current platform code
        platform_flag (int): Required platform flag
    
    Returns:
        str or None: Formatted cron entry if valid, None otherwise
    """
    # Check platform compatibility
    if platform_flag != PLATFORM_ANY and platform_flag != current_platform:
        _log(name, f"Skipping cron entry (platform mismatch): {time_expr} {command}")
        return None
    
    # Only process on supported platforms
    if current_platform not in [PLATFORM_DARWIN, PLATFORM_LINUX]:
        _log(name, f"Skipping cron entry (unsupported platform): {time_expr} {command}")
        return None
    
    # Validate the cron entry
    is_valid, error_msg = _validate_cron_entry(name, time_expr, command)
    if not is_valid:
        _log(name, f"ERROR: Invalid cron entry: {error_msg}")
        _log(name, f"  Time: {time_expr}")
        _log(name, f"  Command: {command}")
        return None
    
    # Expand ~ in command to absolute path
    expanded_command = os.path.expanduser(command)
    
    # Format as cron entry
    cron_entry = f"{time_expr} {expanded_command}"
    _log(name, f"Validated cron entry: {cron_entry}")
    
    return cron_entry

def apply_cron_jobs(all_cron_entries):
    """
    Applies collected cron jobs to the user's crontab.
    Manages a dedicated section between markers.
    
    Args:
        all_cron_entries (list): List of cron entry strings
    """
    if not all_cron_entries:
        _log("cron", "No cron entries to apply")
        return
    
    current_platform = get_current_platform()
    if current_platform not in [PLATFORM_DARWIN, PLATFORM_LINUX]:
        _log("cron", f"Cron jobs not supported on platform: {platform.system()}")
        return
    
    _log("cron", f"Applying {len(all_cron_entries)} cron job(s) to crontab...")
    
    # Read current crontab
    try:
        result = subprocess.run(
            ['crontab', '-l'],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            current_crontab = result.stdout
        else:
            # No crontab exists yet
            current_crontab = ""
            _log("cron", "No existing crontab found, will create new one")
    
    except FileNotFoundError:
        _log("cron", "ERROR: 'crontab' command not found. Is cron installed?")
        return
    except Exception as e:
        _log("cron", f"ERROR: Failed to read crontab: {e}")
        return
    
    # Create backup
    backup_crontab = current_crontab
    
    # Find managed section
    lines = current_crontab.split('\n')
    begin_idx = -1
    end_idx = -1
    
    for i, line in enumerate(lines):
        if line.strip() == CRON_BEGIN_MARKER:
            begin_idx = i
        elif line.strip() == CRON_END_MARKER:
            end_idx = i
            break
    
    # Build new managed section
    managed_section = [CRON_BEGIN_MARKER]
    managed_section.extend(all_cron_entries)
    managed_section.append(CRON_END_MARKER)
    
    # Update crontab content
    if begin_idx != -1 and end_idx != -1:
        # Replace existing managed section
        _log("cron", "Updating existing managed cron section")
        new_lines = lines[:begin_idx] + managed_section + lines[end_idx + 1:]
    elif begin_idx != -1 or end_idx != -1:
        # Markers are corrupted (only one found)
        _log("cron", "ERROR: Cron markers are corrupted (only one marker found)")
        _log("cron", "Please manually fix your crontab before proceeding")
        return
    else:
        # No managed section exists, append it
        _log("cron", "Creating new managed cron section")
        # Add a blank line before markers if crontab is not empty
        if current_crontab.strip():
            new_lines = lines + [''] + managed_section
        else:
            new_lines = managed_section
    
    # Build new crontab content
    new_crontab = '\n'.join(new_lines)
    
    # Ensure newline at end of file
    if not new_crontab.endswith('\n'):
        new_crontab += '\n'
    
    # Write to temporary file
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.crontab') as tmp_file:
            tmp_file.write(new_crontab)
            tmp_file_path = tmp_file.name
        
        _log("cron", f"Wrote new crontab to temporary file: {tmp_file_path}")
        
        # Validate by installing the temporary crontab
        result = subprocess.run(
            ['crontab', tmp_file_path],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            _log("cron", "Successfully updated crontab!")
            _log("cron", f"Added {len(all_cron_entries)} cron job(s)")
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
        else:
            # Validation failed, restore backup
            _log("cron", "ERROR: Crontab validation failed!")
            _log("cron", f"Error output: {result.stderr}")
            _log("cron", "Rolling back to previous crontab...")
            
            # Restore backup
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.crontab') as backup_file:
                backup_file.write(backup_crontab if backup_crontab else "")
                backup_file_path = backup_file.name
            
            subprocess.run(['crontab', backup_file_path], check=False)
            os.unlink(backup_file_path)
            os.unlink(tmp_file_path)
            
            _log("cron", "Rollback completed. Original crontab restored.")
    
    except Exception as e:
        _log("cron", f"ERROR: Failed to update crontab: {e}")
        _log("cron", "Attempting to restore backup...")
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.crontab') as backup_file:
                backup_file.write(backup_crontab if backup_crontab else "")
                backup_file_path = backup_file.name
            
            subprocess.run(['crontab', backup_file_path], check=False)
            os.unlink(backup_file_path)
            _log("cron", "Backup restored successfully")
        except Exception as restore_error:
            _log("cron", f"ERROR: Failed to restore backup: {restore_error}")

def _handle_link(name, source, target, current_platform, platform_flag):
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
    Processes the configuration dictionary to link, copy files, and collect cron jobs.

    Args:
        config (dict): A dictionary with the following structure:
            {
                'name': str,          # Name for logging scope (e.g., 'zsh', 'nvim')
                'link': [            # List of items to symlink
                    [source, target, platform_flag], ...
                ],
                'copy': [            # List of items to copy
                    [source, target, platform_flag], ...
                ],
                'cron': [            # List of cron jobs to manage (optional)
                    [time_expr, command, platform_flag], ...
                ]
            }
          source: Relative path from the .strap file OR an absolute path.
          target: Destination path (use ~ for home directory).
          time_expr: Cron time expression (e.g., "0 * * * *").
          command: Command or script to execute.
          platform_flag: 1 (Darwin), 2 (Linux), 3 (Any).
    """
    global COLLECTED_CRON_ENTRIES
    
    if not isinstance(config, dict):
        print("[bootstrap/utils] ERROR: Invalid config format - must be a dictionary.")
        return

    name = config.get('name', 'unknown')
    link_tasks = config.get('link', [])
    copy_tasks = config.get('copy', [])
    cron_tasks = config.get('cron', [])

    if not isinstance(link_tasks, list):
         print(f"[bootstrap/{name}] ERROR: Invalid 'link' format - must be a list.")
         link_tasks = []
    if not isinstance(copy_tasks, list):
        print(f"[bootstrap/{name}] ERROR: Invalid 'copy' format - must be a list.")
        copy_tasks = []
    if not isinstance(cron_tasks, list):
        print(f"[bootstrap/{name}] ERROR: Invalid 'cron' format - must be a list.")
        cron_tasks = []


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

    # Process cron jobs (collect them for later application)
    for entry in cron_tasks:
        if isinstance(entry, (list, tuple)) and len(entry) == 3:
            time_expr, command, platform_flag = entry
            if isinstance(time_expr, str) and isinstance(command, str) and isinstance(platform_flag, int):
                cron_entry = _handle_cron(name, time_expr, command, current_platform, platform_flag)
                if cron_entry:
                    COLLECTED_CRON_ENTRIES.append(cron_entry)
            else:
                _log(name, f"ERROR: Invalid cron entry format: {entry}. Must be [str, str, int].")
        else:
            _log(name, f"ERROR: Invalid cron entry format: {entry}. Must be a list/tuple of 3 elements.")

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