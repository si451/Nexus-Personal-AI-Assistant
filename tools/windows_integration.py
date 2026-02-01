"""
Nexus Windows Integration Tools
===============================
Provides deep integration with Windows OS features:
1. Task Scheduler (schtasks)
2. App State Tracking (psutil)
"""

import subprocess
import psutil
import time
from langchain_core.tools import tool

@tool
def schedule_task(task_name: str, schedule_type: str, time_str: str, command: str):
    """
    Schedules a Windows task using schtasks.
    
    Args:
        task_name: Name of the task (e.g., "NexusMaintenance")
        schedule_type: DAILY, WEEKLY, ONCE, MINUTE, etc.
        time_str: Time to run (HH:mm) or modifier (e.g., 1 for every 1 minute)
        command: The command to execute
    
    Example:
        schedule_task("NexusCleanup", "DAILY", "03:00", "python c:/path/cleanup.py")
    """
    # Sanitize inputs to prevent injection (basic)
    if '"' in task_name or '"' in command:
        return "Error: Task name and command cannot contain double quotes."
        
    cmd_str = f'schtasks /create /tn "{task_name}" /tr "{command}" /sc {schedule_type} /st {time_str} /f'
    
    try:
        # Run command
        result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Successfully scheduled task '{task_name}'"
        else:
            return f"Failed to schedule task: {result.stderr}"
    except Exception as e:
        return f"Error executing schtasks: {e}"

@tool
def get_app_state(app_name: str):
    """
    Checks if an application is running and its state (active/idle).
    
    Args:
        app_name: Name of the process (e.g., "code", "chrome", "spotify")
    """
    app_name = app_name.lower()
    if not app_name.endswith(".exe"):
        pass # psutil matches name without extension usually, but let's be flexible
        
    found = []
    for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent']):
        try:
            if app_name in proc.info['name'].lower():
                found.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    if not found:
        return f"App '{app_name}' is NOT running."
        
    # Summarize
    count = len(found)
    status = found[0]['status']
    return f"App '{app_name}' is RUNNING ({count} processes). Status: {status}"

WINDOWS_TOOLS = [schedule_task, get_app_state]
