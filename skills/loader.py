
import os
import importlib.util
import inspect
from langchain_core.tools import tool, Tool

# Decorator to mark a function as a dynamic skill
def skill(func):
    """
    Decorator to register a function as a Nexus Skill.
    Works just like @tool but marks it for the loader.
    """
    # Create the tool
    t = tool(func)
    # Tag the TOOL object, not just the function
    t._is_nexus_skill = True
    return t

class SkillLoader:
    def __init__(self, skills_dir="skills"):
        self.skills_dir = skills_dir
        self.loaded_skills = []

    def load_skills(self):
        """
        Dynamically loads all python modules in the skills directory 
        and extracts functions decorated with @skill.
        """
        self.loaded_skills = []
        
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
            return []

        print(f"[Skills] 🧠 Scanning '{self.skills_dir}' for new capabilities...")

        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py") and filename != "__init__.py" and filename != "loader.py":
                module_path = os.path.join(self.skills_dir, filename)
                module_name = filename[:-3]
                
                try:
                    # Dynamic Import
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Scan for skills
                    count = 0
                    for name, obj in inspect.getmembers(module):
                        if hasattr(obj, "_is_nexus_skill"):
                            self.loaded_skills.append(obj)
                            count += 1
                        
                        # Also accept standard LangChain tools if clearly named
                        elif hasattr(obj, "func") and isinstance(obj, Tool):
                             self.loaded_skills.append(obj)
                             count += 1
                             
                    if count > 0:
                        print(f"[Skills] ✨ Loaded {count} skills from {module_name}")
                        
                except Exception as e:
                    print(f"[Skills] ⚠️ Failed to load {filename}: {e}")

        return self.loaded_skills
