import time
import threading
from datetime import datetime

# Global notification store
notifications = []


def check_notifications():
    """Checks if any timers or reminders have finished."""
    global notifications
    completed = [n for n in notifications if n['completed']]
    
    # Remove completed notifications
    notifications = [n for n in notifications if not n['completed']]
    
    return {
        'active': len(notifications),
        'completed': completed,
        'next': min([n['target_time'] for n in notifications]) if notifications else None
    }


def set_timer(seconds, label=""):
    """Sets a countdown timer."""
    target_time = time.time() + seconds
    
    def countdown():
        time.sleep(seconds)
        for n in notifications:
            if n['target_time'] == target_time:
                n['completed'] = True
                return

    timer = {
        'target_time': target_time,
        'label': label,
        'completed': False,
        'created': datetime.now().isoformat()
    }
    notifications.append(timer)
    
    # Start countdown in background
    threading.Thread(target=countdown, daemon=True).start()
    
    return {
        'status': 'timer_set',
        'label': label,
        'duration_seconds': seconds,
        'target_time': datetime.fromtimestamp(target_time).isoformat()
    }