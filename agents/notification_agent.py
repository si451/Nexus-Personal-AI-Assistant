"""
Notification Subagent
=====================
Attempts to listen to Windows Notifications.
NOTE: Real listening requires WinRT asyncio loops which are complex to integrate in this thread model.
For now, we implement a 'Simulation' or 'Sender' that can at least trigger alerts.
"""
import time
import threading
try:
    from winsdk.windows.ui.notifications import ToastNotificationManager
    from winsdk.windows.data.xml.dom import XmlDocument
    WINSDK_AVAILABLE = True
except ImportError:
    WINSDK_AVAILABLE = False

from soul.subconscious import get_subconscious, EventPriority

class NotificationAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[NotificationAgent] Started (Sender Mode)")

    def stop(self):
        self.running = False
        if self.thread:
             self.thread.join(timeout=2)
             
    def send_notification(self, title, message):
        """Sends a system toast"""
        if not WINSDK_AVAILABLE:
            print(f"[NOTE] {title}: {message}")
            return
            
        try:
            # Create toaster
            toaster = ToastNotificationManager.create_toast_notifier("Nexus AI")
            
            # Simple XML
            xml = f"""
            <toast>
                <visual>
                    <binding template='ToastGeneric'>
                        <text>{title}</text>
                        <text>{message}</text>
                    </binding>
                </visual>
            </toast>
            """
            doc = XmlDocument()
            doc.load_xml(xml)
            
            toast = ToastNotificationManager.create_toast_notification(doc)
            toaster.show(toast)
            
        except Exception as e:
            print(f"[NotificationAgent] Error sending toast: {e}")

    def _loop(self):
        while self.running:
            # In a real full implementation, we would attach a listener to UserNotificationListener
            # But that requires 'checked' capability in app manifest and a package identity.
            # python.exe usually doesn't have this.
            # So this agent mainly acts as an ACTUATOR for now.
            time.sleep(10)

# Singleton
_notif_agent = None
def get_notification_agent():
    global _notif_agent
    if _notif_agent is None:
        _notif_agent = NotificationAgent()
    return _notif_agent
