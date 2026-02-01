"""
Nexus Subagent Manager
======================
Manages background "senses" and subagents that run independently of the main brain.
"""

from typing import Dict, List, Any
import threading

class NexusSubagent:
    """Base class for all background subagents."""
    def __init__(self, name: str, interval: float = 1.0):
        self.name = name
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        """Start the subagent loop."""
        pass

    def stop(self):
        """Stop the subagent."""
        pass

    def _loop(self):
        """Main logic loop."""
        pass

class SubagentManager:
    """
    The Hive Master.
    Responsibility:
    1. Initialize all subagents (Eyes, Ears, etc.)
    2. Manage the Event Bus (Signal routing)
    3. Provide a unified status report to the Brain
    """
    
    def __init__(self):
        self.subagents: Dict[str, NexusSubagent] = {}
        # TODO: Initialize Event Bus here
    
    def register_agent(self, agent: NexusSubagent):
        """Add a new subagent to the hive."""
        self.subagents[agent.name] = agent
        
    def start_all(self):
        """Wake up the hive."""
        print("[Hive] Awakening subagents...")
        for name, agent in self.subagents.items():
            agent.start()
            
    def stop_all(self):
        """Sleep the hive."""
        print("[Hive] Putting subagents to sleep...")
        for agent in self.subagents.values():
            agent.stop()

# Singleton
_hive = None

def get_hive() -> SubagentManager:
    global _hive
    if _hive is None:
        _hive = SubagentManager()
    return _hive
