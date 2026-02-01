
from skills.loader import skill
import os
import subprocess

@skill
def grep_search(query: str, path: str = "."):
    """
    Search for a text pattern in files (recursive).
    This is like 'grep -r'. Useful for finding code snippets or specific text.
    """
    try:
        # Use simple python walk to be cross-platform and safe
        matches = []
        path = os.path.abspath(path)
        
        for root, dirs, files in os.walk(path):
            # Skip hidden folders
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith(('.py', '.md', '.txt', '.js', '.json', '.html', '.css')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                if query.lower() in line.lower():
                                    matches.append(f"{file}:{i+1}: {line.strip()[:100]}")
                                    if len(matches) > 20:
                                        return "\n".join(matches) + "\n... (more matches truncated)"
                    except:
                        continue
                        
        return "\n".join(matches) if matches else "No matches found."
    except Exception as e:
        return f"Grep Error: {e}"

@skill
def list_directory_tree(path: str = ".", max_depth: int = 2):
    """
    Returns a visual tree structure of the directory.
    """
    try:
        startpath = os.path.abspath(path)
        tree = []
        
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            if level > max_depth:
                continue
                
            indent = ' ' * 4 * (level)
            tree.append(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 4 * (level + 1)
            for f in files[:10]: # Limit files for brevity
                tree.append(f'{subindent}{f}')
            if len(files) > 10:
                tree.append(f'{subindent}... ({len(files)-10} more)')
                
        return "\n".join(tree[:50]) # Limit output lines
    except Exception as e:
        return f"Tree Error: {e}"
