"""Git operations wrapper for deytefiles."""

import subprocess
from pathlib import Path
from .logger import log_error


class GitRepository:
    """Wrapper for git operations on a repository."""
    
    def __init__(self, repo_path=None):
        """
        Initialize Git repository wrapper.
        
        Args:
            repo_path (Path, optional): Path to repository. If None, auto-detect.
        """
        self.repo_root = repo_path or self._get_root()
    
    def _get_root(self):
        """
        Get the root directory of the git repository.
        
        Returns:
            Path: Absolute path to repository root
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True,
                check=True
            )
            return Path(result.stdout.strip())
        except subprocess.CalledProcessError:
            log_error("Not in a git repository")
            raise
    
    def get_current_branch(self):
        """
        Get the current git branch name.
        
        Returns:
            str: Current branch name
        """
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"
    
    def has_changes(self):
        """
        Check if there are any changes in the repository.
        
        Returns:
            bool: True if there are changes, False otherwise
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False
    
    def add_all(self):
        """Stage all changes."""
        subprocess.run(['git', 'add', '-A'], check=True)
    
    def commit(self, message):
        """
        Create a commit with the given message.
        
        Args:
            message (str): Commit message
        """
        subprocess.run(['git', 'commit', '-m', message], check=True)
    
    def pull_rebase(self, remote='origin', branch=None):
        """
        Pull changes with rebase.
        
        Args:
            remote (str): Remote name (default: 'origin')
            branch (str): Branch name (default: current branch)
            
        Returns:
            subprocess.CompletedProcess: Result of the pull operation
        """
        if branch is None:
            branch = self.get_current_branch()
        
        return subprocess.run(
            ['git', 'pull', '--rebase', remote, branch],
            capture_output=True,
            text=True,
            check=False
        )
    
    def push(self, remote='origin', branch=None, force=False):
        """
        Push changes to remote.
        
        Args:
            remote (str): Remote name (default: 'origin')
            branch (str): Branch name (default: current branch)
            force (bool): Use --force-with-lease if True
        """
        if branch is None:
            branch = self.get_current_branch()
        
        cmd = ['git', 'push']
        if force:
            cmd.append('--force-with-lease')
        cmd.extend([remote, branch])
        
        subprocess.run(cmd, check=True)
    
    def abort_rebase(self):
        """Abort an ongoing rebase."""
        subprocess.run(['git', 'rebase', '--abort'], check=False)

