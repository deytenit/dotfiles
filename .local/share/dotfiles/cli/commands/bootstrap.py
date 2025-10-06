"""Bootstrap command for deytefiles."""

import os
import sys
import subprocess
from pathlib import Path
from .base import BaseCommand
from ..logger import log_info, log_success, log_error, log_warning
from ..git_ops import GitRepository


class BootstrapCommand(BaseCommand):
    """Run the bootstrap process to set up dotfiles."""
    
    def execute(self):
        """
        Execute bootstrap command.
        
        This command:
        1. Executes bootstrap.py from the repository root
        2. Processes all .strap files
        3. Creates symlinks and copies files
        4. Applies cron jobs
        
        Returns:
            int: Exit code (0 for success, non-zero for failure)
        """
        log_info("Starting bootstrap process...")
        
        try:
            # Navigate to repo root
            repo = GitRepository()
            repo_root = repo.repo_root
            os.chdir(repo_root)
            
            bootstrap_script = repo_root / 'bootstrap.py'
            
            if not bootstrap_script.exists():
                log_error(f"Bootstrap script not found: {bootstrap_script}")
                self.notify(
                    "Deytefiles Bootstrap Failed",
                    "bootstrap.py not found in repository root",
                    success=False
                )
                return 1
            
            log_info(f"Executing: {bootstrap_script}")
            
            # Run bootstrap.py
            result = subprocess.run(
                [sys.executable, str(bootstrap_script)],
                check=False
            )
            
            if result.returncode == 0:
                log_success("Bootstrap completed successfully!")
                self.notify(
                    "Deytefiles Bootstrap Complete",
                    "Dotfiles have been successfully bootstrapped",
                    success=True
                )
                return 0
            else:
                log_error(f"Bootstrap failed with exit code {result.returncode}")
                self.notify(
                    "Deytefiles Bootstrap Failed",
                    f"Bootstrap process failed with exit code {result.returncode}",
                    success=False
                )
                return result.returncode
                
        except KeyboardInterrupt:
            log_warning("\nBootstrap interrupted by user")
            return 130
        except Exception as e:
            log_error(f"Unexpected error during bootstrap: {e}")
            self.notify(
                "Deytefiles Bootstrap Failed",
                f"Unexpected error: {str(e)}",
                success=False
            )
            return 1

