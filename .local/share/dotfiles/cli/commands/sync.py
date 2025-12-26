"""Sync command for deytefiles."""

import os
import subprocess
from datetime import datetime
from .base import BaseCommand
from ..logger import log_info, log_success, log_error, log_warning
from ..git_ops import GitRepository


class SyncCommand(BaseCommand):
    """Sync dotfiles repository with remote."""
    
    def execute(self):
        """
        Execute sync command.
        
        This command:
        1. Adds all changes
        2. Commits with timestamp
        3. Pulls with rebase
        4. Pushes to remote
        5. Sends notification about the result
        
        Returns:
            int: Exit code (0 for success, non-zero for failure)
        """
        log_info("Starting dotfiles sync...")
        
        try:
            # Initialize git repository with explicit path
            repo = GitRepository(self.args.repo_root)
            os.chdir(repo.repo_root)
            log_info(f"Repository: {repo.repo_root}")
            
            # Get current branch
            branch = repo.get_current_branch()
            log_info(f"Current branch: {branch}")
            
            # Check for changes
            if not repo.has_changes():
                log_info("No changes to sync")
                self.notify(
                    "Deytefiles Sync",
                    "No changes to sync",
                    success=True
                )
                return 0
            
            # Stage all changes
            log_info("Staging changes...")
            repo.add_all()
            
            # Create commit message with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = getattr(self.args, 'message', None) or f"auto-sync: {timestamp}"
            
            log_info(f"Committing with message: {commit_message}")
            repo.commit(commit_message)
            
            # Pull with rebase if not in detached HEAD or initial commit
            if branch != "HEAD":
                log_info(f"Pulling changes from origin/{branch} with rebase...")
                result = repo.pull_rebase('origin', branch)
                
                if result.returncode != 0:
                    # Check if it's a rebase conflict
                    if 'conflict' in result.stderr.lower() or 'conflict' in result.stdout.lower():
                        log_error("Rebase conflict detected!")
                        log_info("Aborting rebase...")
                        repo.abort_rebase()
                        
                        error_msg = "Rebase conflict detected. Manual intervention required."
                        log_error(error_msg)
                        self.notify(
                            "Deytefiles Sync Failed",
                            error_msg,
                            success=False
                        )
                        return 1
                    
                    # If not a conflict but still failed
                    log_warning("Pull failed, but continuing with push...")
            
            # Push changes
            log_info(f"Pushing changes to origin/{branch}...")
            force = getattr(self.args, 'force', False)
            repo.push('origin', branch, force=force)
            
            log_success("Dotfiles synced successfully!")
            
            self.notify(
                "Deytefiles Sync Complete",
                f"Successfully synced dotfiles on branch '{branch}'",
                success=True
            )
            
            return 0
            
        except subprocess.CalledProcessError as e:
            error_msg = "Sync failed. Check the logs for details."
            log_error(error_msg)
            self.notify(
                "Deytefiles Sync Failed",
                error_msg,
                success=False
            )
            return 1
        except KeyboardInterrupt:
            log_warning("\nSync interrupted by user")
            return 130
        except Exception as e:
            log_error(f"Unexpected error: {e}")
            self.notify(
                "Deytefiles Sync Failed",
                f"Unexpected error: {str(e)}",
                success=False
            )
            return 1

