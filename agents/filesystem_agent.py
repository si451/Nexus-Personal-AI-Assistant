"""
FileSystem Subagent
===================
Monitors specific directories for changes using watchdog.
"""
import time
import threading
from pathlib import Path
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

from soul.subconscious import get_subconscious, EventPriority

class FileHandler(FileSystemEventHandler):
    def __init__(self, bus):
        self.bus = bus
    
    def on_created(self, event):
        if not event.is_directory:
            self.bus.publish("filesystem", "FILE_CREATED", {
                "path": event.src_path,
                "name": Path(event.src_path).name
            }, EventPriority.NORMAL)

    def on_modified(self, event):
        if not event.is_directory:
             # Basic debounce logic could go here
             pass

class FileSystemAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.observer = None
        
        # Paths to watch
        self.watch_paths = [
            str(Path.home() / "Downloads"),
            str(Path.home() / "Documents")
        ]
    
    def start(self):
        if not WATCHDOG_AVAILABLE:
            print("[FileSystemAgent] Watchdog not installed. Disabled.")
            return

        self.running = True
        self.observer = Observer()
        handler = FileHandler(self.output_bus)
        
        for path in self.watch_paths:
            if Path(path).exists():
                self.observer.schedule(handler, path, recursive=False)
        
        self.observer.start()
        print("[FileSystemAgent] Started")

    def stop(self):
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()

# Singleton
_fs_agent = None
def get_filesystem_agent():
    global _fs_agent
    if _fs_agent is None:
        _fs_agent = FileSystemAgent()
    return _fs_agent
