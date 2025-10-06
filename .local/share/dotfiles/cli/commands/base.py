"""Base command class for deytefiles CLI."""

from abc import ABC, abstractmethod
from ..notifications import NotificationSystem


class BaseCommand(ABC):
    """Base class for all CLI commands."""
    
    def __init__(self, args):
        """
        Initialize command with parsed arguments.
        
        Args:
            args: Parsed command-line arguments
        """
        self.args = args
        self.quiet = getattr(args, 'quiet', False)
    
    @abstractmethod
    def execute(self):
        """
        Execute the command.
        
        Returns:
            int: Exit code (0 for success, non-zero for failure)
        """
        pass
    
    def notify(self, title, message, success=True):
        """
        Send a notification if not in quiet mode.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            success (bool): Whether this is a success notification
        """
        if not self.quiet:
            NotificationSystem.send(title, message, success)

