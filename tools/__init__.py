"""
Nexus Tools Package
===================
All LangChain @tool-decorated functions for Nexus's capabilities.
"""

from .os_tools import open_application, shell, message_user, open_url
from .file_tools import write_file, open_file, list_directory_tree, grep_search
from .research import duckduckgo_search, arxiv_search, wikipedia_search, quick_search, deep_research

__all__ = [
    'open_application', 'shell', 'message_user',
    'open_url', 'write_file', 'open_file',
    'list_directory_tree', 'grep_search', 'duckduckgo_search',
    'arxiv_search', 'wikipedia_search', 'quick_search', 'deep_research',
]