
from skills.loader import skill
import subprocess
import os
import sys
import threading
import time
import json

# Registry of running subagents
_subagents = {}

@skill
def create_subagent(name: str, task_description: str, loop_interval: int = 60):
    """
    Create a new specialized sub-agent (a Python script) to perform a background task.
    
    Args:
        name: Name of the agent (e.g., 'weather_watcher', 'folder_guard')
        task_description: What it should do (e.g., 'Check if new files appear in Downloads')
        loop_interval: How often it runs its loop (in seconds)
    """
    agent_dir = os.path.join(os.getcwd(), 'agents')
    os.makedirs(agent_dir, exist_ok=True)
    
    filename = os.path.join(agent_dir, f"{name}.py")
    
    # Template for a simple persistent agent
    code = f'''"""
Nexus Sub-Agent: {name}
Task: {task_description}
Interval: {loop_interval}s
"""
import time
import os
from datetime import datetime

def perform_task():
    print(f"[{{datetime.now()}}] {name} working: {task_description}")
    # TODO: Implement actual logic based on description
    # This is a template. Nexus needs to edit this file to add specific logic.
    pass

if __name__ == "__main__":
    print("🤖 Sub-agent {name} started. PID: {{os.getpid()}}")
    try:
        while True:
            perform_task()
            time.sleep({loop_interval})
    except KeyboardInterrupt:
        print("🛑 Sub-agent {name} stopping.")
'''
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(code)
        
    return f"Created sub-agent template at {filename}. I should now EDIT this file to implement the specific logic for '{task_description}'."

@skill
def run_subagent(name: str):
    """
    Launch a sub-agent in a background process.
    """
    agent_dir = os.path.join(os.getcwd(), 'agents')
    filename = os.path.join(agent_dir, f"{name}.py")
    
    if not os.path.exists(filename):
        return f"Agent {name} does not exist. Create it first."
        
    global _subagents
    if name in _subagents and _subagents[name].poll() is None:
        return f"Agent {name} is already running (PID: {_subagents[name].pid})."
        
    # Start process
    proc = subprocess.Popen([sys.executable, filename], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
    
    _subagents[name] = proc
    return f"🚀 Launched {name} (PID: {proc.pid}) in background."

@skill
def stop_subagent(name: str):
    """Stop a running sub-agent."""
    global _subagents
    if name not in _subagents:
        return f"Agent {name} is not known/running."
        
    proc = _subagents[name]
    if proc.poll() is None:
        proc.terminate()
        return f"Terminated {name}."
    else:
        return f"{name} was already stopped."

@skill
def list_subagents():
    """List all running sub-agents."""
    global _subagents
    status = []
    for name, proc in _subagents.items():
        state = "Running" if proc.poll() is None else f"Stopped (Exit: {proc.returncode})"
        status.append(f"- {name}: {state} (PID: {proc.pid})")
    
    if not status: return "No active sub-agents."
    return "\\n".join(status)
