"""
Nexus Desktop Control Tools
============================
Full keyboard and mouse automation using pyautogui.
Gives Nexus the ability to physically control the computer.
"""

import pyautogui
import time
from langchain_core.tools import tool

# Safety: prevent pyautogui from moving to corner to trigger failsafe
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3  # Small delay between actions for stability


@tool
def type_text(text: str, interval: float = 0.02):
    """
    Types text at the current cursor position, simulating keyboard input.
    
    Args:
        text: The text to type
        interval: Delay between keystrokes in seconds (default 0.02)
    """
    try:
        pyautogui.typewrite(text, interval=interval) if text.isascii() else pyautogui.write(text)
        return f"Typed: '{text[:50]}{'...' if len(text) > 50 else ''}'"
    except Exception as e:
        return f"Type error: {e}"


@tool
def press_key(key: str):
    """
    Presses a single key. Supports special keys like:
    enter, tab, escape, space, backspace, delete,
    up, down, left, right, home, end, pageup, pagedown,
    f1-f12, capslock, numlock, printscreen, volumeup, volumedown, volumemute
    
    Args:
        key: The key to press (e.g., 'enter', 'tab', 'escape', 'f5')
    """
    try:
        pyautogui.press(key.lower())
        return f"Pressed key: {key}"
    except Exception as e:
        return f"Key press error: {e}"


@tool
def hotkey(keys: str):
    """
    Presses a keyboard shortcut (combo of keys pressed simultaneously).
    
    Args:
        keys: Comma-separated key names (e.g., 'ctrl,c' for copy, 'alt,tab' for switch window, 'ctrl,shift,s' for save as)
    
    Common shortcuts:
        - 'ctrl,c' = Copy
        - 'ctrl,v' = Paste
        - 'ctrl,z' = Undo
        - 'ctrl,s' = Save
        - 'alt,tab' = Switch window
        - 'alt,f4' = Close window
        - 'win,d' = Show desktop
        - 'win,e' = Open Explorer
        - 'ctrl,shift,esc' = Task Manager
    """
    try:
        key_list = [k.strip().lower() for k in keys.split(',')]
        pyautogui.hotkey(*key_list)
        return f"Pressed hotkey: {'+'.join(key_list)}"
    except Exception as e:
        return f"Hotkey error: {e}"


@tool
def click_at(x: int, y: int, button: str = "left", clicks: int = 1):
    """
    Clicks the mouse at specific screen coordinates.
    
    Args:
        x: X coordinate on screen
        y: Y coordinate on screen
        button: 'left', 'right', or 'middle' (default: 'left')
        clicks: Number of clicks (1=single, 2=double) (default: 1)
    """
    try:
        pyautogui.click(x=x, y=y, button=button, clicks=clicks)
        return f"Clicked {button} at ({x}, {y}) x{clicks}"
    except Exception as e:
        return f"Click error: {e}"


@tool
def move_mouse(x: int, y: int, duration: float = 0.3):
    """
    Moves the mouse cursor to specific screen coordinates.
    
    Args:
        x: Target X coordinate
        y: Target Y coordinate
        duration: Movement duration in seconds (default 0.3, set to 0 for instant)
    """
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return f"Mouse moved to ({x}, {y})"
    except Exception as e:
        return f"Move error: {e}"


@tool
def scroll_wheel(amount: int, x: int = None, y: int = None):
    """
    Scrolls the mouse wheel. Positive = up, negative = down.
    
    Args:
        amount: Number of scroll units (positive=up, negative=down)
        x: Optional X coordinate to scroll at (default: current position)
        y: Optional Y coordinate to scroll at (default: current position)
    """
    try:
        if x is not None and y is not None:
            pyautogui.scroll(amount, x=x, y=y)
        else:
            pyautogui.scroll(amount)
        direction = "up" if amount > 0 else "down"
        return f"Scrolled {direction} by {abs(amount)} units"
    except Exception as e:
        return f"Scroll error: {e}"


@tool
def drag_mouse(start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5):
    """
    Drags from one point to another (click-hold-move-release).
    Useful for moving windows, selecting text, or drag-and-drop operations.
    
    Args:
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        end_x: Ending X coordinate
        end_y: Ending Y coordinate
        duration: Drag duration in seconds (default 0.5)
    """
    try:
        pyautogui.moveTo(start_x, start_y, duration=0.1)
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
        return f"Dragged from ({start_x},{start_y}) to ({end_x},{end_y})"
    except Exception as e:
        return f"Drag error: {e}"


@tool
def get_mouse_position():
    """
    Returns the current mouse cursor position on screen.
    Useful for figuring out where to click.
    """
    pos = pyautogui.position()
    screen = pyautogui.size()
    return f"Mouse at ({pos.x}, {pos.y}) — Screen size: {screen.width}x{screen.height}"


@tool
def screenshot_region(x: int = 0, y: int = 0, width: int = 0, height: int = 0):
    """
    Takes a screenshot of a specific region and saves it.
    If no coordinates given, captures the entire screen.
    
    Args:
        x: Left edge X coordinate (default 0)
        y: Top edge Y coordinate (default 0) 
        width: Width of region (default 0 = full screen)
        height: Height of region (default 0 = full screen)
    """
    try:
        import os
        os.makedirs("screenshots", exist_ok=True)
        filename = f"screenshots/capture_{int(time.time())}.png"
        
        if width > 0 and height > 0:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
        else:
            screenshot = pyautogui.screenshot()
        
        screenshot.save(filename)
        return f"Screenshot saved to {filename}"
    except Exception as e:
        return f"Screenshot error: {e}"


DESKTOP_TOOLS = [
    type_text, press_key, hotkey, click_at,
    move_mouse, scroll_wheel, drag_mouse,
    get_mouse_position, screenshot_region
]
