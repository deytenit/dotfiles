"""Cross-platform notification system for deytefiles."""

import subprocess
import platform
from .logger import log_warning


class NotificationSystem:
    """Cross-platform notification system."""
    
    @staticmethod
    def send(title, message, success=True):
        """
        Send a native notification to the user.
        
        Args:
            title (str): Notification title
            message (str): Notification message
            success (bool): Whether this is a success (True) or error (False) notification
        """
        system = platform.system().lower()
        
        try:
            if system == 'darwin':
                NotificationSystem._send_macos(title, message, success)
            elif system == 'linux':
                NotificationSystem._send_linux(title, message, success)
        except FileNotFoundError:
            log_warning("Notification system not available")
        except Exception as e:
            log_warning(f"Failed to send notification: {e}")
    
    @staticmethod
    def _send_macos(title, message, success):
        """Send notification on macOS using osascript."""
        sound = "Glass" if success else "Basso"
        script = f'display notification "{message}" with title "{title}" sound name "{sound}"'
        subprocess.run(
            ['osascript', '-e', script],
            check=False,
            capture_output=True
        )
    
    @staticmethod
    def _send_linux(title, message, success):
        """Send notification on Linux using notify-send."""
        urgency = "normal" if success else "critical"
        icon = "dialog-information" if success else "dialog-error"
        subprocess.run(
            ['notify-send', '-u', urgency, '-i', icon, title, message],
            check=False,
            capture_output=True
        )

