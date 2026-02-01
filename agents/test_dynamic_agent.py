
import threading
import time
from soul.subconscious import get_subconscious, EventPriority

class TestAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False

    def start(self):
        self.running = True
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()
        print("[TestAgent] Started Dynamic Agent")

    def _loop(self):
        time.sleep(1)
        self.output_bus.publish("test", "DYNAMIC_EVENT", {"msg": "Hello form Spawner"}, EventPriority.HIGH)

def get_test_agent():
    return TestAgent()
