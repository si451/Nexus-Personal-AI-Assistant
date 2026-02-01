"""
Browser Tools
=============
Exposes Playwright capabilities to the LLM.
"""
from langchain_core.tools import tool
from agents.browser_agent import get_browser_agent

@tool
def open_browser_url(url: str):
    """
    Opens the real browser to a specific URL.
    Use this to visit websites, login, or inspect pages.
    """
    agent = get_browser_agent()
    return agent.navigate(url)

@tool
def click_element_on_page(selector: str):
    """
    Clicks an element on the current page using a CSS selector (e.g., '#submit-btn', '.nav-link').
    """
    agent = get_browser_agent()
    return agent.click(selector)

@tool
def type_on_page(selector: str, text: str):
    """
    Types text into an input field defined by a CSS selector.
    """
    agent = get_browser_agent()
    return agent.type_text(selector, text)

@tool
def read_current_page():
    """
    Reads the text content of the current browser page.
    """
    agent = get_browser_agent()
    return agent.read_page()

BROWSER_TOOLS = [open_browser_url, click_element_on_page, type_on_page, read_current_page]
