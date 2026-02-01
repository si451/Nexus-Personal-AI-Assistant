"""
Agent Spawner (Factory)
=======================
Allows Nexus to dynamically create and spawn new subagents.
This is the core of "Self-Replication".
"""
import os
import threading
import importlib.util
from soul.subconscious import get_subconscious

class AgentFactory:
    def __init__(self):
        self.active_agents = {}
        self.agents_dir = "agents"
        
    def spawn_agent(self, agent_name: str, python_code: str):
        """
        Dynamically creates a new agent file and starts it.
        agent_name: e.g. "crypto_watcher"
        """
        try:
            # 1. Write the file
            filename = f"{agent_name}_agent.py"
            path = os.path.join(self.agents_dir, filename)
            
            # Simple check to avoid overwriting core agents without care
            if os.path.exists(path):
                 print(f"[Factory] Agent {agent_name} already exists. Reloading not fully supported yet.")
                 pass
                 
            with open(path, "w", encoding="utf-8") as f:
                f.write(python_code)
                
            print(f"[Factory] Created agent file: {path}")
            
            # 2. Dynamic Import
            spec = importlib.util.spec_from_file_location(f"agents.{agent_name}_agent", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 3. Find the 'get_X_agent' or Main Class
            # Convention: We look for a function that starts with 'get_' and ends with '_agent'
            start_func = None
            for attr in dir(module):
                if attr.startswith("get_") and attr.endswith("_agent"):
                    start_func = getattr(module, attr)
                    break
            
            if start_func:
                agent_instance = start_func()
                if hasattr(agent_instance, 'start'):
                    agent_instance.start()
                    self.active_agents[agent_name] = agent_instance
                    return f"Successfully spawned and started {agent_name}"
                else:
                    return f"Agent {agent_name} loaded but has no 'start' method."
            else:
                return f"Could not find factory function (get_X_agent) in {filename}"
                
        except Exception as e:
            return f"Failed to spawn agent: {e}"

# Singleton
_factory = None
def get_agent_factory():
    global _factory
    if _factory is None:
        _factory = AgentFactory()
    return _factory
