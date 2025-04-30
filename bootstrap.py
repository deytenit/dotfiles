#!/usr/bin/env python3
import os
import sys
import runpy
import platform

# --- Configuration ---
# Directory containing the utility script, relative to this bootstrap script
UTILS_DIR_REL = ".local/share" 
# The specific name of the utility module's directory within UTILS_DIR_REL
UTILS_MODULE_DIR = "dotfiles" 
# Name of the utility file (although we mainly need its directory for PYTHONPATH)
UTILS_FILENAME = "utils.py" 
# Name of the files to search for in subdirectories
STRAP_FILENAME = ".strap"
# --- End Configuration ---


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
    
    # Traverse the directory tree starting from the script's directory
    for root, dirs, files in os.walk(script_dir, topdown=True):
        # Skip the .local directory itself to avoid potential loops or unwanted execution
        if os.path.commonpath([utils_base_path, root]) == utils_base_path:
             log(f"Skipping utils directory: {root}")
             dirs[:] = [] # Don't descend into subdirectories of .local/share
             continue
             
        # Skip .git directories
        if '.git' in dirs:
            dirs.remove('.git')

        if STRAP_FILENAME in files:
            strap_files_found += 1
            strap_file_path = os.path.join(root, STRAP_FILENAME)
            log(f"Found strap file: {os.path.relpath(strap_file_path, script_dir)}")

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
                # Optionally, print traceback for more detailed debugging
                # import traceback
                # traceback.print_exc()

    # --- Restore original sys.path ---
    sys.path = original_sys_path
    # log("Restored original sys.path") # Optional: uncomment for debug


    log(f"Bootstrap finished. Found {strap_files_found} '{STRAP_FILENAME}' files, executed {strap_files_executed}.")

if __name__ == "__main__":
    main()

