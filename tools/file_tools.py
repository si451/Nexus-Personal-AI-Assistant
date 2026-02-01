import os
import glob
import re
from typing import List, Dict


def write_file(file_path: str, content: str):
    """
    Writes text content to a file at the given path. Overwrites if exists.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def open_file(file_path: str):
    """
    Opens a file or application detached (non-blocking).
    """
    try:
        if os.name == 'nt':
            os.startfile(file_path)
            return f"Opened {file_path}"
        else:
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.Popen([opener, file_path])
            return f"Opened {file_path}"
    except Exception as e:
        return f"Error opening file: {str(e)}"


def list_directory_tree(path: str = '.', max_depth: int = 3) -> str:
    """
    Returns a visual tree structure of the directory.
    """
    def tree(dir_path, prefix='', depth=0):
        if depth > max_depth:
            return []
        
        contents = []
        try:
            items = os.listdir(dir_path)
            for i, item in enumerate(sorted(items)):
                is_last = i == len(items) - 1
                new_prefix = prefix + ('└── ' if is_last else '├── ')
                full_path = os.path.join(dir_path, item)
                
                contents.append(f"{prefix}{new_prefix}{item}")
                
                if os.path.isdir(full_path):
                    child_prefix = prefix + ('    ' if is_last else '│   ')
                    contents.extend(tree(full_path, child_prefix, depth + 1))
        except Exception as e:
            contents.append(f"{prefix}Error: {str(e)}")
        return contents

    result = [f"{os.path.abspath(path)}/"]
    result.extend(tree(path))
    return '\n'.join(result)


def grep_search(query: str, path: str = '.') -> List[Dict]:
    """
    Search for a text pattern in files (recursive).
    """
    results = []
    pattern = re.compile(query)
    
    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if pattern.search(line):
                            results.append({
                                'file': file_path,
                                'line': line_num,
                                'content': line.strip()
                            })
            except:
                continue
    
    return results