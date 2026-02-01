"""
Peripheral Subagent
===================
Monitors USB devices and Webcam usage (if possible) via WMI.
"""
import time
import threading
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

from soul.subconscious import get_subconscious, EventPriority

class PeripheralAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None
        self.c = wmi.WMI() if WMI_AVAILABLE else None
        self.known_devices = set()

    def start(self):
        if not WMI_AVAILABLE:
            print("[PeripheralAgent] WMI not available.")
            return

        self.running = True
        # Populate initial list
        try:
            for usb in self.c.Win32_USBHub():
                 self.known_devices.add(usb.DeviceID)
        except:
            pass
            
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[PeripheralAgent] Started")

    def stop(self):
        self.running = False
        if self.thread:
             self.thread.join(timeout=2)

    def _loop(self):
        while self.running:
            try:
                current_devices = set()
                new_devices = []
                
                for usb in self.c.Win32_USBHub():
                    did = usb.DeviceID
                    current_devices.add(did)
                    if did not in self.known_devices:
                        new_devices.append(usb)
                
                # Check for new
                for dev in new_devices:
                    name = dev.Name if hasattr(dev, 'Name') else "Unknown USB"
                    print(f"[PeripheralAgent] New Device: {name}")
                    self.output_bus.publish("peripheral", "DEVICE_CONNECTED", {
                        "name": name,
                        "id": dev.DeviceID
                    }, EventPriority.HIGH)
                
                self.known_devices = current_devices
                time.sleep(3)
                
            except Exception as e:
                # WMI can be flaky
                time.sleep(5)

# Singleton
_periph_agent = None
def get_peripheral_agent():
    global _periph_agent
    if _periph_agent is None:
        _periph_agent = PeripheralAgent()
    return _periph_agent
