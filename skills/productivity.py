
import time
import threading
import os
from skills.loader import skill

def _timer_thread(seconds: int, label: str):
    time.sleep(seconds)
    # In a real app, this would trigger a notification or playsound
    # For now, we write to a file that the Agent might check, or relying on SSE if we hook it up later.
    # But since we can't easily push async messages from a thread back to the main LLM loop without stored state:
    print(f"⏰ TIMER DONE: {label}")
    # We could write to a 'notifications.txt' file?
    with open("notifications.txt", "a") as f:
        f.write(f"TIMER DONE: {label}\n")

@skill
def set_timer(seconds: int, label: str = "Timer"):
    """
    Sets a countdown timer.
    """
    t = threading.Thread(target=_timer_thread, args=(seconds, label))
    t.start()
    return f"⏳ Timer set for {seconds} seconds ('{label}')."

@skill
def check_notifications():
    """
    Checks if any timers or reminders have finished.
    """
    if os.path.exists("notifications.txt"):
        with open("notifications.txt", "r") as f:
            content = f.read()
        # clear it
        open("notifications.txt", "w").close()
        return f"🔔 Notifications:\n{content}" if content else "🔕 No new notifications."
    return "🔕 No notifications."
