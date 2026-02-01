
"""
Skill: Shell Manager (OpenClaw Parity)
======================================
Robust process management for Nexus.
Allows background execution, output buffering, and timeouts.
Replaces simple `subprocess.run` with a persistent process registry.
"""

import subprocess
import threading
import time
import queue
import os
import signal
from typing import Dict, Optional, Any
from skills.loader import skill

# Configuration matching OpenClaw defaults
MAX_OUTPUT_CHARS = 200_000
DEFAULT_TIMEOUT = 1800  # 30 minutes

class ProcessManager:
    """
    Manages background processes, capturing their output and state.
    Singleton-style usage via the module-level instance.
    """
    def __init__(self):
        self.processes: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def _enqueue_output(self, out, pid):
        """Reads output from a pipe and appends to the process buffer."""
        process_data = self.processes.get(pid)
        if not process_data: return

        for line in iter(out.readline, b''):
            try:
                decoded = line.decode('utf-8', errors='replace')
            except:
                decoded = str(line)
                
            with self.lock:
                # Buffer limit check
                if len(process_data['output']) > MAX_OUTPUT_CHARS:
                    process_data['truncated'] = True
                    # Keep end of log (simulating 'tail')
                    keep_len = MAX_OUTPUT_CHARS // 2
                    process_data['output'] = "...[TRUNCATED]...\n" + process_data['output'][-keep_len:]
                
                process_data['output'] += decoded
        out.close()

    def start_process(self, cmd: str, background: bool = False, timeout: int = DEFAULT_TIMEOUT) -> str:
        """Starts a process and returns its ID."""
        try:
            # Use shell=True for flexibility, but be careful with input
            # Redirect stderr to stdout to capture everything in one stream
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False, # We decode manually to handle errors
                bufsize=1   # Line buffered
            )
            
            pid = str(proc.pid)
            
            with self.lock:
                self.processes[pid] = {
                    "cmd": cmd,
                    "process": proc,
                    "start_time": time.time(),
                    "timeout": timeout,
                    "output": "",
                    "truncated": False,
                    "background": background,
                    "status": "running"
                }

            # Start background thread to read output
            t = threading.Thread(target=self._enqueue_output, args=(proc.stdout, pid))
            t.daemon = True
            t.start()
            
            return pid
            
        except Exception as e:
            return f"Error starting process: {e}"

    def check_process(self, pid: str) -> Dict:
        """Check status and get partial output."""
        with self.lock:
            proc_data = self.processes.get(pid)
            if not proc_data:
                return {"error": "Process not found"}
            
            proc = proc_data["process"]
            return_code = proc.poll()
            
            current_output = proc_data["output"]
            # Clear buffer after reading to prevent re-reading same logs? 
            # OpenClaw keeps a rolling tail. Let's keep it but maybe offer a 'read & clear' option later.
            # For now, we return the whole buffer (truncated handled by insertion).
            
            status = "running"
            if return_code is not None:
                status = "completed" if return_code == 0 else "failed"
                proc_data["status"] = status
            
            # Check timeout
            if status == "running" and (time.time() - proc_data["start_time"] > proc_data["timeout"]):
                self.kill_process(pid)
                status = "timed_out"
                proc_data["output"] += "\n[System] Process killed due to timeout."

            return {
                "pid": pid,
                "cmd": proc_data["cmd"],
                "status": status,
                "exit_code": return_code,
                "output": current_output,
                "truncated": proc_data["truncated"]
            }

    def kill_process(self, pid: str) -> str:
        with self.lock:
            proc_data = self.processes.get(pid)
            if not proc_data: return "Process not found"
            
            proc = proc_data["process"]
            if proc.poll() is None:
                # Kill it
                import signal
                try:
                    # Windows might need specialized kill commands
                    proc.terminate()
                    # Give it a second
                    time.sleep(0.5)
                    if proc.poll() is None:
                        proc.kill()
                    return f"Process {pid} killed."
                except Exception as e:
                    return f"Error killing process: {e}"
            return "Process already finished."

# Global Instance
_manager = ProcessManager()

# ==================== TOOLS (Exposed via @skill) ====================

@skill
def shell_exec(command: str, background: bool = False, timeout_seconds: int = 1800):
    """
    Execute a shell command with robust management.
    
    Args:
        command: The command line to run (e.g., 'npm install', 'python script.py')
        background: If True, returns immediately with a PID. If False, waits for completion.
        timeout_seconds: Max time allowed for the command (default 30 mins).
    """
    pid = _manager.start_process(command, background, timeout_seconds)
    
    if str(pid).startswith("Error"):
        return pid
        
    if background:
        return f"Process started in background. PID: {pid}. Use `shell_check('{pid}')` to see output."
    
    # Foreground execution: Wait loop
    start_time = time.time()
    while True:
        info = _manager.check_process(pid)
        if info["status"] != "running":
            return f"**Command Finished** ({info['status']})\nOutput:\n{info['output']}"
        
        if time.time() - start_time > timeout_seconds:
             _manager.kill_process(pid)
             return f"Timeout reached. Process {pid} killed.\nPartial Output:\n{info['output']}"
             
        time.sleep(1) # Polling interval

@skill
def shell_check(pid: str):
    """
    Check the status and output of a running background process.
    """
    info = _manager.check_process(pid)
    if "error" in info: return info["error"]
    
    status_icon = "🟢" if info["status"] == "running" else "🔴"
    return f"**Process {pid}: {info['status']}** {status_icon}\nCmd: `{info['cmd']}`\n\nOutput:\n{info['output']}"

@skill
def shell_kill(pid: str):
    """
    Terminate a running process by PID.
    """
    return _manager.kill_process(pid)
