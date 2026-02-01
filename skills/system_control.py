
import ctypes
import os
import psutil
from skills.loader import skill

@skill
def get_battery_status():
    """
    Checks the current battery percentage and power status.
    """
    try:
        battery = psutil.sensors_battery()
        if battery:
            plugged = "Plugged In" if battery.power_plugged else "Running on Battery"
            return f"🔋 Battery: {battery.percent}% ({plugged})"
        else:
            return "❌ No battery detected (Desktop?)"
    except Exception as e:
        return f"Unable to read battery: {e}"

@skill
def lock_screen():
    """
    Locks the Windows workstation immediately.
    Use this if the user says "Lock my pc" or "I'm leaving".
    """
    try:
        ctypes.windll.user32.LockWorkStation()
        return "🔒 Screen locked."
    except Exception as e:
        return f"Failed to lock screen: {e}"

@skill
def set_volume(level: int):
    """
    Sets the system volume (0-100).
    Note: Requires 'pycaw' or similar complex setup on Windows. 
    For now, we will use a VBScript hack to avoid extra heavy dependencies.
    """
    # Placeholder: Windows volume control via python is notably hard without comtypes/pycaw.
    # We will simulate for now or use nircmd if available.
    # To be safe, we will just mute/unmute which is easier via keyboard injection
    if level == 0:
        import pyautogui
        pyautogui.press("volumemute")
        return "🔇 Muted system volume."
    else:
        # Simple feedback
        return "⚠️ Precise volume control requires 'pycaw' dependency. I can only Mute/Unmute for now using 'set_volume(0)'."
