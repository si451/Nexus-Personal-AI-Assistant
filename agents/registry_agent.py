"""
Registry Subagent
=================
Monitors critical Windows Registry keys (specifically Startup items).
"""
import time
import threading
import winreg
from soul.subconscious import get_subconscious, EventPriority

class RegistryAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None
        self.known_startup = {} # {key_path+name: value}

        self.monitored_keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
        ]

    def start(self):
        self.running = True
        # Populate initial
        self._scan(first_run=True)
        
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[RegistryAgent] Started")

    def stop(self):
        self.running = False
        if self.thread:
             self.thread.join(timeout=2)

    def _get_values(self, hive, path):
        values = {}
        try:
            with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, val, _ = winreg.EnumValue(key, i)
                        values[name] = val
                        i += 1
                    except OSError:
                        break
        except Exception:
            pass
        return values

    def _scan(self, first_run=False):
        current_snapshot = {}
        
        for hive, path in self.monitored_keys:
            vals = self._get_values(hive, path)
            for name, val in vals.items():
                unique_id = f"{path}\\{name}"
                current_snapshot[unique_id] = val
                
                if not first_run and unique_id not in self.known_startup:
                    print(f"[RegistryAgent] New Startup Item: {name}")
                    self.output_bus.publish("registry", "REGISTRY_CHANGED", {
                        "type": "NEW_STARTUP",
                        "name": name,
                        "value": val
                    }, EventPriority.HIGH)
                elif not first_run and self.known_startup.get(unique_id) != val:
                    print(f"[RegistryAgent] Changed Startup Item: {name}")
                    self.output_bus.publish("registry", "REGISTRY_CHANGED", {
                        "type": "MODIFIED_STARTUP",
                        "name": name,
                        "value": val
                    }, EventPriority.NORMAL)
        
        # Check for deletions
        if not first_run:
            for uid in self.known_startup:
                if uid not in current_snapshot:
                     name = uid.split("\\")[-1]
                     print(f"[RegistryAgent] Deleted Startup Item: {name}")
                     self.output_bus.publish("registry", "REGISTRY_CHANGED", {
                        "type": "DELETED_STARTUP",
                        "name": name
                    }, EventPriority.NORMAL)
                    
        self.known_startup = current_snapshot

    def _loop(self):
        while self.running:
            try:
                self._scan()
                time.sleep(10) # Scan every 10s
            except Exception as e:
                print(f"[RegistryAgent] Error: {e}")
                time.sleep(10)

# Singleton
_reg_agent = None
def get_registry_agent():
    global _reg_agent
    if _reg_agent is None:
        _reg_agent = RegistryAgent()
    return _reg_agent
