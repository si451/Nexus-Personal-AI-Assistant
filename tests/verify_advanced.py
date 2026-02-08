"""
Verification Script for Advanced Agents & Spawner
=================================================
Tests:
1. AgentFactory (Spawning a new agent dynamicallly).
2. Initialization of Voice, Peripheral, Window agents.
"""
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.getcwd())

from soul.subconscious import get_subconscious

def verify_factory():
    print("\n--- Testing Agent Factory ---")
    try:
        from soul.agent_factory import get_agent_factory
        factory = get_agent_factory()
        
        # Define a dynamic agent code
        code = """
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
"""
        print("Spawning 'test_dynamic' agent...")
        res = factory.spawn_agent("test_dynamic", code)
        print(f"Result: {res}")
        return "Successfully" in res
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def verify_advanced_agents():
    print("\n--- Testing Advanced Agents Init ---")
    agents = []
    try:
        from agents.voice_agent import get_voice_agent
        from agents.peripheral_agent import get_peripheral_agent
        from agents.window_agent import get_window_agent
        
        print("Initializing Voice Agent...")
        v = get_voice_agent()
        v.start()
        agents.append(v)

        print("Initializing Peripheral Agent...")
        p = get_peripheral_agent()
        p.start()
        agents.append(p)

        print("Initializing Window Agent...")
        w = get_window_agent()
        w.start()
        agents.append(w)
        
        print("✅ Advanced Agents Initialized without crash.")
        
        # Check window agent specifically
        try:
             print("Window Agent Check: Minimizing nothing...")
             # Just checking if internal lib works
             import pygetwindow
             print(f"Active Window: {pygetwindow.getActiveWindow().title}")
        except:
             print("Window check minor fail (maybe no window active)")
             
        time.sleep(2)
        for a in agents: a.stop()
        return True
        
    except Exception as e:
        print(f"FAIL: {e}")
        return False

if __name__ == "__main__":
    f_ok = verify_factory()
    a_ok = verify_advanced_agents()
    
    if f_ok and a_ok:
        print("\n✅ ADVANCED SYSTEMS GO")
    else:
        print("\n❌ SOME TESTS FAILED")
