#!/usr/bin/env python3
import os
import sys
import runpy
import platform

# Try to import yaml from different sources
try:
    import yaml
except ImportError:
    # Use vendored YAML parser
    from pathlib import Path
    vendor_path = Path(__file__).parent / '.local' / 'share' / 'dotfiles' / 'vendor'
    sys.path.insert(0, str(vendor_path))
    try:
        import yaml_parser as yaml
    except ImportError as e:
        print(f"[bootstrap] ERROR: Could not import YAML parser: {e}")
        print("[bootstrap] Please ensure .local/share/dotfiles/vendor/yaml_parser.py exists")
        sys.exit(1)

# --- Configuration ---
# Directory containing the utility script, relative to this bootstrap script
UTILS_DIR_REL = ".local/share" 
# The specific name of the utility module's directory within UTILS_DIR_REL
UTILS_MODULE_DIR = "dotfiles" 
# Name of the utility file (although we mainly need its directory for PYTHONPATH)
UTILS_FILENAME = "utils.py" 
# Name of the strap files to search for in subdirectories (legacy Python format)
STRAP_FILENAME = ".strap"
# YAML strap file patterns
STRAP_YAML_PATTERNS = ["strap.yaml", "strap@darwin.yaml", "strap@linux.yaml"]
# --- End Configuration ---


def get_platform_from_filename(filename):
    """
    Extract platform from strap filename.
    
    Args:
        filename (str): Filename like 'strap.yaml', 'strap@darwin.yaml', etc.
        
    Returns:
        str: Platform name ('any', 'darwin', 'linux') or None if not a strap file
    """
    if filename == 'strap.yaml':
        return 'any'
    elif filename.startswith('strap@') and filename.endswith('.yaml'):
        # Extract platform between @ and .yaml
        platform_name = filename[6:-5]  # Remove 'strap@' and '.yaml'
        return platform_name
    return None


def should_process_strap_file(filename, current_platform_name):
    """
    Determine if a strap file should be processed on the current platform.
    
    Args:
        filename (str): Strap filename
        current_platform_name (str): Current platform ('darwin' or 'linux')
        
    Returns:
        bool: True if file should be processed
    """
    file_platform = get_platform_from_filename(filename)
    
    if file_platform is None:
        return False
    
    if file_platform == 'any':
        return True
    
    return file_platform == current_platform_name


def get_current_platform_name():
    """Get current platform name as string."""
    system = platform.system().lower()
    if system == 'darwin':
        return 'darwin'
    elif system == 'linux':
        return 'linux'
    else:
        return 'unknown'


def platform_name_to_code(platform_name):
    """Convert platform name to platform code constant."""
    # Import here to avoid circular dependency
    from dotfiles import utils
    
    if platform_name == 'darwin':
        return utils.PLATFORM_DARWIN
    elif platform_name == 'linux':
        return utils.PLATFORM_LINUX
    else:
        return utils.PLATFORM_ANY


def log(message):
    """Main bootstrap logger."""
    print(f"[bootstrap] {message}")

def main():
    log("Initializing bootstrap...")
    
    # Get the absolute path to the directory containing this bootstrap script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log(f"Running from: {script_dir}")

    # Calculate the absolute path to the directory containing utils.py
    utils_base_path = os.path.abspath(os.path.join(script_dir, UTILS_DIR_REL))
    utils_module_path = os.path.join(utils_base_path, UTILS_MODULE_DIR)
    utils_file_path = os.path.join(utils_module_path, UTILS_FILENAME)

    log(f"Expecting utils module directory at: {utils_module_path}")

    # Verify that utils.py actually exists
    if not os.path.isfile(utils_file_path):
        log(f"ERROR: Utility file not found at expected location: {utils_file_path}")
        log("Please ensure '.local/share/dotfiles/utils.py' exists.")
        sys.exit(1)

    # --- Add utils directory to Python's path ---
    # This allows .strap files to simply 'import dotfiles.utils'
    original_sys_path = list(sys.path)
    if utils_base_path not in sys.path:
         sys.path.insert(0, utils_base_path) # Add the parent dir (.local/share)
         log(f"Temporarily added '{utils_base_path}' to sys.path")


    strap_files_found = 0
    strap_files_executed = 0
    
    # Get current platform
    current_platform_name = get_current_platform_name()
    log(f"Current platform: {current_platform_name}")
    
    # Traverse the directory tree starting from the script's directory
    for root, dirs, files in os.walk(script_dir, topdown=True):
        # Skip .git directories
        if '.git' in dirs:
            dirs.remove('.git')

        # Check for YAML strap files first (new format)
        yaml_strap_files = [f for f in files if f in STRAP_YAML_PATTERNS]
        
        for yaml_file in yaml_strap_files:
            # Check if this file should be processed on current platform
            if not should_process_strap_file(yaml_file, current_platform_name):
                log(f"Skipping {yaml_file} in {os.path.relpath(root, script_dir)} (platform mismatch)")
                continue
            
            strap_files_found += 1
            strap_file_path = os.path.join(root, yaml_file)
            log(f"Found YAML strap file: {os.path.relpath(strap_file_path, script_dir)}")

            try:
                log(f"Processing: {strap_file_path}")
                
                # Load YAML configuration
                with open(strap_file_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                if config is None:
                    log(f"WARNING: Empty YAML file: {strap_file_path}")
                    continue
                
                # Import utils to use process_yaml_config
                if utils_base_path not in sys.path:
                    sys.path.insert(0, utils_base_path)
                
                from dotfiles import utils
                
                # Get platform code
                file_platform_name = get_platform_from_filename(yaml_file)
                platform_code = platform_name_to_code(file_platform_name)
                
                # Process the YAML config
                utils.process_yaml_config(config, root, platform_code)
                
                strap_files_executed += 1
                log(f"Finished processing: {strap_file_path}")
                
            except yaml.YAMLError as e:
                log(f"ERROR processing {strap_file_path}: YAML parse error - {e}")
            except Exception as e:
                log(f"ERROR processing {strap_file_path}: {e}")
                import traceback
                traceback.print_exc()

        # Legacy: Check for old Python .strap files
        if STRAP_FILENAME in files:
            strap_files_found += 1
            strap_file_path = os.path.join(root, STRAP_FILENAME)
            log(f"Found legacy .strap file: {os.path.relpath(strap_file_path, script_dir)}")

            try:
                log(f"Executing: {strap_file_path}")
                # Execute the .strap file. It runs in its own module scope.
                # The modified sys.path allows it to find 'dotfiles.utils'
                runpy.run_path(strap_file_path, run_name="__strap__") 
                strap_files_executed += 1
                log(f"Finished executing: {strap_file_path}")
            except ImportError as e:
                 log(f"ERROR executing {strap_file_path}: Import error - {e}")
                 log(f" -> Ensure '{utils_base_path}' is accessible and contains '{UTILS_MODULE_DIR}/{UTILS_FILENAME}'.")
                 log(f" -> Current sys.path includes: {sys.path}") # Help debugging
            except Exception as e:
                log(f"ERROR executing {strap_file_path}: {e}")

    # --- Restore original sys.path ---
    sys.path = original_sys_path
    # log("Restored original sys.path") # Optional: uncomment for debug

    # --- Apply collected cron jobs ---
    # After all .strap files have been processed, apply the collected cron entries
    try:
        # Import utils to access COLLECTED_CRON_ENTRIES and apply_cron_jobs
        if utils_base_path not in sys.path:
            sys.path.insert(0, utils_base_path)
        
        from dotfiles import utils
        
        if utils.COLLECTED_CRON_ENTRIES:
            log(f"Applying {len(utils.COLLECTED_CRON_ENTRIES)} collected cron job(s)...")
            utils.apply_cron_jobs(utils.COLLECTED_CRON_ENTRIES)
        else:
            log("No cron jobs to apply.")
        
        # Restore sys.path again
        sys.path = original_sys_path
    except ImportError as e:
        log(f"WARNING: Could not import utils to apply cron jobs: {e}")
    except Exception as e:
        log(f"WARNING: Error applying cron jobs: {e}")

    log(f"Bootstrap finished. Found {strap_files_found} strap files, executed {strap_files_executed}.")

if __name__ == "__main__":
    main()

