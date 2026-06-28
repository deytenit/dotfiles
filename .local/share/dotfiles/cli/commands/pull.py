"""Pull command for deytefiles."""

import os
import subprocess
from .base import BaseCommand
from ..logger import log_info, log_success, log_error, log_warning
from ..git_ops import GitRepository


class PullCommand(BaseCommand):
    """Pull dotfiles repository from remote."""

    def execute(self):
        log_info("Pulling dotfiles from remote...")

        try:
            repo = GitRepository(self.args.repo_root)
            os.chdir(repo.repo_root)
            log_info(f"Repository: {repo.repo_root}")

            branch = repo.get_current_branch()
            log_info(f"Current branch: {branch}")

            log_info(f"Pulling changes from origin/{branch} with rebase...")
            result = repo.pull_rebase('origin', branch)

            if result.returncode != 0:
                if 'conflict' in result.stderr.lower() or 'conflict' in result.stdout.lower():
                    log_error("Rebase conflict detected!")
                    log_info("Aborting rebase...")
                    repo.abort_rebase()

                    error_msg = "Rebase conflict detected. Manual intervention required."
                    log_error(error_msg)
                    self.notify("Deytefiles Pull Failed", error_msg, success=False)
                    return 1

                error_msg = f"Pull failed:\n{result.stderr or result.stdout}"
                log_error(error_msg)
                self.notify("Deytefiles Pull Failed", "Pull failed. Check the logs.", success=False)
                return 1

            log_success("Dotfiles pulled successfully!")
            self.notify(
                "Deytefiles Pull Complete",
                f"Successfully pulled dotfiles on branch '{branch}'",
                success=True
            )
            return 0

        except subprocess.CalledProcessError:
            error_msg = "Pull failed. Check the logs for details."
            log_error(error_msg)
            self.notify("Deytefiles Pull Failed", error_msg, success=False)
            return 1
        except KeyboardInterrupt:
            log_warning("\nPull interrupted by user")
            return 130
        except Exception as e:
            log_error(f"Unexpected error: {e}")
            self.notify("Deytefiles Pull Failed", f"Unexpected error: {str(e)}", success=False)
            return 1
