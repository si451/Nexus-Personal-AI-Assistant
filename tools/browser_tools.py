"""
Browser Tools (System Chrome)
==============================
Opens URLs and interacts with the user's real Chrome browser
using native OS commands and desktop control tools.

No Playwright, no separate browser instance.
"""
import subprocess
import webbrowser
from langchain_core.tools import tool


@tool
def open_browser_url(url: str) -> str:
    """
    Opens a URL in the user's default system browser (Chrome).
    This opens the REAL Chrome that the user already has open,
    not a separate browser instance.
    
    Args:
        url: The URL to open (e.g., 'https://linkedin.com')
    """
    try:
        # Use webbrowser module to open in default browser
        webbrowser.open(url)
        return f"✅ Opened {url} in system Chrome. Use `see_screen` to see the current state, then use desktop control tools (click_at, type_text, etc.) to interact with it."
    except Exception as e:
        return f"❌ Failed to open URL: {e}"


@tool  
def open_chrome_at(url: str) -> str:
    """
    Opens a URL specifically in Google Chrome (not the default browser).
    Use this when you need to ensure Chrome is used.
    
    Args:
        url: The URL to open
    """
    try:
        subprocess.Popen(['start', 'chrome', url], shell=True)
        return f"✅ Opened {url} in Chrome. Use `see_screen` to see what's on screen, then use desktop controls to interact."
    except Exception as e:
        return f"❌ Failed: {e}"


BROWSER_TOOLS = [open_browser_url, open_chrome_at]
