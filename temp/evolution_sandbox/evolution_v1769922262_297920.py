"""
Nexus Evolution Engine (The Sandbox)
=====================================
Allows Nexus to safely modify its own code by providing a testing sandbox.
PRIME DIRECTIVE 3: EVOLVE (Safely)
"""

import shutil
import os
import subprocess
import time
import hashlib
from pathlib import Path
from typing import Tuple, Optional

class CodeSandbox:
    def __init__(self):
        self.sandbox_dir = Path("temp/evolution_sandbox")
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        self.active_experiments = {}

    def create_sandbox(self, target_file: str) -> str:
        """
        Creates a copy of the target file in the sandbox.
        Returns the path to the sandboxed file.
        """
        target_path = Path(target_file)
        if not target_path.exists():
            raise FileNotFoundError(f"Source file {target_file} not found")

        # Create unique sandbox name
        timestamp = int(time.time())
        file_hash = hashlib.md5(target_path.stem.encode()).hexdigest()[:6]
        sandbox_filename = f"{target_path.stem}_v{timestamp}_{file_hash}{target_path.suffix}"
        sandbox_path = self.sandbox_dir / sandbox_filename

        # Copy file
        shutil.copy2(target_path, sandbox_path)
        
        self.active_experiments[str(sandbox_path)] = str(target_path)
        return str(sandbox_path)

    def run_simulation(self, sandbox_file: str, test_command: Optional[str] = None) -> Tuple[bool, str]:
        """
        Runs the sandboxed code to verify stability.
        If no test_command provided, just checks syntax/import.
        """
        if not os.path.exists(sandbox_file):
            return False, "Sandbox file not found"

        # 1. Syntax Check (Compile)
        try:
            with open(sandbox_file, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, sandbox_file, 'exec')
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"
        except Exception as e:
            return False, f"Compilation Error: {e}"

        # 2. Runtime Check (if script)
        # If it's a module, we might just try to import it in a separate process
        # If it's a script, we run it with a timeout
        
        try:
            cmd = test_command if test_command else f"python {sandbox_file}"
            
            # Run with timeout to prevent infinite loops
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10 # 10 seconds generic timeout for safety
            )
            
            output = result.stdout + "\n" + result.stderr
            if result.returncode != 0:
                return False, f"Runtime Error (Exit {result.returncode}):\n{output}"
            
            return True, f"Simulation passed!\nOutput:\n{output}"

        except subprocess.TimeoutExpired:
            return False, "Simulation timed out (10s limit)"
        except Exception as e:
            return False, f"Simulation failed: {e}"

    def apply_evolution(self, sandbox_file: str) -> str:
        """
        Promotes the sandboxed file to main (overwrites original).
        Returns status message.
        """
        original_file = self.active_experiments.get(sandbox_file)
        if not original_file:
            return "Error: Unknown sandbox file or original lost."

        # Create backup of original before overwriting
        backup_path = Path(original_file).with_suffix(f".bak_{int(time.time())}")
        shutil.copy2(original_file, backup_path)

        # Overwrite
        try:
            shutil.copy2(sandbox_file, original_file)
            del self.active_experiments[sandbox_file]
            return f"Evolution applied! 🧬\nOriginal backed up to {backup_path}"
        except Exception as e:
            return f"Critical Error applying evolution: {e}"

    def discard_experiment(self, sandbox_file: str):
        """Removes the sandbox file."""
        try:
            os.remove(sandbox_file)
            if sandbox_file in self.active_experiments:
                del self.active_experiments[sandbox_file]
            return "Experiment discarded."
        except:
            pass

# Singleton
_sandbox = None

def get_sandbox() -> CodeSandbox:
    global _sandbox
    if _sandbox is None:
        _sandbox = CodeSandbox()
    return _sandbox

# ==================== TOOLS FOR LLM ====================
from langchain_core.tools import tool

@tool
def create_sandbox(file_path: str):
    """
    Step 1 of Evolution: Create a safe copy of a file to modify.
    Returns the path to the sandboxed file.
    """
    try:
        sandbox = get_sandbox()
        path = sandbox.create_sandbox(file_path)
        return f"Sandbox created at: {path}\nNow use write_file to modify THIS file, not the original."
    except Exception as e:
        return f"Error creating sandbox: {e}"

@tool
def run_sandbox_test(sandbox_file: str, test_command: str = None):
    """
    Step 2 of Evolution: Run the sandboxed file to test functionality.
    Args:
        sandbox_file: Path returned by create_sandbox
        test_command: Optional custom command (e.g. 'python temp/test_script.py')
    """
    try:
        sandbox = get_sandbox()
        success, output = sandbox.run_simulation(sandbox_file, test_command)
        status = "PASSED" if success else "FAILED"
        return f"Simulation {status}.\nOutput:\n{output}"
    except Exception as e:
        return f"Error running simulation: {e}"

@tool
def apply_evolution(sandbox_file: str):
    """
    Step 3 of Evolution: If tests pass, apply changes to the real file.
    CRITICAL: Only call this if run_sandbox_test returned PASSED.
    """
    try:
        sandbox = get_sandbox()
        result = sandbox.apply_evolution(sandbox_file)
        return result
    except Exception as e:
        return f"Error applying evolution: {e}"

EVOLUTION_TOOLS = [create_sandbox, run_sandbox_test, apply_evolution]
