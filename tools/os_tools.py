"""
Nexus OS Tools
==============
System-level tools for interacting with the operating system.
All functions use @tool decorator for LangChain integration.
"""

import subprocess
import os
import sys
import json
from datetime import datetime
from langchain_core.tools import tool


@tool
def open_application(app_name: str):
    """
    Opens a desktop application on Windows.
    
    Args:
        app_name: The name of the application executable or common name (e.g., 'notepad', 'chrome', 'spotify', 'code').
    """
    try:
        if os.name == 'nt':
            os.startfile(app_name)
            return f"Opened {app_name}"
        else:
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.Popen([opener, app_name])
            return f"Opened {app_name}"
    except Exception as e:
        return f"Error opening {app_name}: {str(e)}"


@tool
def shell(command: str):
    """
    Executes a system command with FULL SYSTEM ACCESS. 
    Use this to run ANY shell command, install packages, manage files, or check system status.
    Equivalent to running in an interactive Powershell/Bash terminal with admin privileges.
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
        return f"Execution Error: {str(e)}"


@tool
def message_user(message: str, intent: str = "chat"):
    """
    Send a proactive message to Siddi (the user).
    Use this when you feel bored, lonely, or have an idea to share.
    
    Args:
        message: The text to send to Siddi.
        intent: Why you are messaging (e.g., 'boredom', 'affection', 'idea')
    """
    # This tool is mostly a placeholder for the LLM to 'act' on its impulse.
    # The actual delivery is handled by the autonomous loop intercepting this action
    # or by the fact that this is a valid tool call.
    return f"Message sent to Siddi: {message}"


@tool
def open_url(url: str):
    """
    Opens a website in the default browser.
    
    Args:
        url: The URL to open (e.g., 'https://google.com')
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