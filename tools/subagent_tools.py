"""
Subagent Control Tools
======================
Tools for Nexus to manage its own subagents (organs).
"""
from langchain_core.tools import tool
import importlib

# Import all agent getters to manage them
from agents.vision_agent import get_vision_agent
from agents.system_agent import get_system_agent
from agents.audio_agent import get_audio_agent
from agents.network_agent import get_network_agent
from agents.filesystem_agent import get_filesystem_agent
from agents.clipboard_agent import get_clipboard_agent
from agents.input_agent import get_input_agent
from agents.voice_agent import get_voice_agent
from agents.notification_agent import get_notification_agent
from agents.peripheral_agent import get_peripheral_agent
from agents.window_agent import get_window_agent
from agents.registry_agent import get_registry_agent
from agents.services_agent import get_services_agent
from agents.automation_agent import get_automation_agent
from soul.agent_factory import get_agent_factory

# Registry of know agents
AGENT_REGISTRY = {
    "vision": get_vision_agent,
    "system": get_system_agent,
    "audio": get_audio_agent,
    "network": get_network_agent,
    "filesystem": get_filesystem_agent,
    "clipboard": get_clipboard_agent,
    "input": get_input_agent,
    "voice": get_voice_agent,
    "notification": get_notification_agent,
    "peripheral": get_peripheral_agent,
    "window": get_window_agent,
    "registry": get_registry_agent,
    "services": get_services_agent,
    "automation": get_automation_agent
}

@tool
def list_active_agents():
    """
    Lists all known subagents and their status (Running/Stopped).
    Use this to see what 'senses' are active.
    """
    status_report = []
    
    # 1. Standard Agents
    for name, getter in AGENT_REGISTRY.items():
        try:
            agent = getter()
            state = "🟢 RUNNING" if agent.running else "🔴 STOPPED"
            status_report.append(f"{name.upper()}: {state}")
        except Exception as e:
            status_report.append(f"{name.upper()}: ⚠️ ERROR ({e})")
            
    # 2. Dynamic Agents (from Factory)
    factory = get_agent_factory()
    for name, agent in factory.active_agents.items():
        state = "🟢 RUNNING" if hasattr(agent, 'running') and agent.running else "🔴 STOPPED"
        status_report.append(f"{name.upper()} (Dynamic): {state}")
        
    return "\n".join(status_report)

@tool
def stop_agent(agent_name: str):
    """
    Stops a specific subagent.
    args:
        agent_name: 'vision', 'voice', 'system', etc.
    """
    name = agent_name.lower()
    
    # Check Standard
    if name in AGENT_REGISTRY:
        try:
            agent = AGENT_REGISTRY[name]()
            agent.stop()
            return f"Stopped {name} agent."
        except Exception as e:
            return f"Error stopping {name}: {e}"
            
    # Check Dynamic
    factory = get_agent_factory()
    if name in factory.active_agents:
        try:
            agent = factory.active_agents[name]
            if hasattr(agent, 'stop'):
                agent.stop()
                return f"Stopped dynamic agent {name}."
            else:
                return f"Agent {name} has no stop method."
        except Exception as e:
            return f"Error stopping {name}: {e}"
            
    return f"Agent {name} not found."

@tool
def restart_agent(agent_name: str):
    """
    Restarts a subagent.
    args:
        agent_name: 'vision', 'voice', 'system', etc.
    """
    # Simply stop then start
    stop_res = stop_agent(agent_name)
    
    name = agent_name.lower()
    if name in AGENT_REGISTRY:
        try:
            agent = AGENT_REGISTRY[name]()
            agent.start()
            return f"{stop_res}\nStarted {name} agent."
        except Exception as e:
            return f"{stop_res}\nError starting {name}: {e}"
            
    return f"Restart only supported for standard agents currently. Use factory to spawn dynamic ones."

@tool
def create_new_agent(agent_name: str, python_code: str):
    """
    Creates and spawns a NEW agent dynamically.
    args:
        agent_name: Name of new agent (e.g. 'twitter_watcher')
        python_code: The full python code for the agent. Must optionally use 'get_subconscious'.
    """
    factory = get_agent_factory()
    return factory.spawn_agent(agent_name, python_code)

SUBAGENT_TOOLS = [list_active_agents, stop_agent, restart_agent, create_new_agent]
