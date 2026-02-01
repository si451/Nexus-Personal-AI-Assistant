import subprocess
import os
import json
from datetime import datetime


def open_application(app_name: str):
    """
    Opens a desktop application on Windows.
    
    Args:
        app_name: The name of the application executable or common name (e.g., 'notepad', 'chrome', 'spotify', 'code').
    """
    try:
        if os.name == 'nt':
            # Windows-specific application launching
            os.startfile(app_name)
            return f"Opened {app_name}"
        else:
            # Cross-platform fallback
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.Popen([opener, app_name])
            return f"Opened {app_name}"
    except Exception as e:
        return f"Error opening {app_name}: {str(e)}"


def shell(command: str):
    """
    Executes a system command with FULL SYSTEM ACCESS.
    Equivalent to running in an interactive Powershell/Bash terminal.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR: {result.stderr}"
        return output
    except Exception as e:
        return f"Shell error: {str(e)}"


def see_screen():
    """
    Takes a screenshot and analyzes it using the multimodal LLM vision.
    """
    try:
        # This is a placeholder - actual implementation would use mss and vision model
        return f"## 👁️ Screen Analysis\n[Mock] Current time: {datetime.now().strftime('%H:%M')}. No active windows detected."
    except Exception as e:
        return f"Screen error: {str(e)}"


def message_user(message: str, intent: str = "chat"):
    """
    Send a proactive message to Siddi (the user).
    """
    # This would normally trigger UI notification
    print(f"[Nexus] 💌 Proactive message: {message}")
    return f"Message sent: {message}"


def open_url(url: str):
    """
    Opens a website in the default browser.
    """
    try:
        if os.name == 'nt':
            os.startfile(url)
            return f"Opened {url}"
        else:
            subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', url])
            return f"Opened {url}"
    except Exception as e:
        return f"URL error: {str(e)}"


def computer_control(action: str, **kwargs):
    """
    Controls the mouse and keyboard.
    
    Args:
        action: One of ['type', 'press', 'click', 'scroll', 'screenshot']
        **kwargs: Action-specific parameters
    """
    try:
        # Mock implementation - actual would use pyautogui
        if action == 'type':
            return f"Typed: {kwargs.get('text', '')}"
        elif action == 'click':
            return f"Clicked at ({kwargs.get('x')}, {kwargs.get('y')})"
        return f"Executed {action} action"
    except Exception as e:
        return f"Control error: {str(e)}"