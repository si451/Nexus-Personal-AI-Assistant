
from langchain_community.tools import DuckDuckGoSearchRun
from skills.loader import skill

search = DuckDuckGoSearchRun()

@skill
def deep_research(topic: str):
    """
    Performs a Deep Research session on a topic.
    This triggers a multi-step search (search -> analyzing results -> refining search)
    to provide a comprehensive answer using the Agent's own reasoning loop.
    
    Args:
        topic: The subject to research (e.g. "Latest breakthroughs in Fusion Energy")
    """
    # Simply returning the prompt ensures the Agent *decides* to use its reasoning
    # This tool acts as a "Macro" that expands into multiple actions
    return f"""
    [ACTION REQUIRED]
    Initiate Deep Research Mode for: '{topic}'
    
    1. Search for overview: `search.poll("{topic}")`
    2. Read 2-3 key sources.
    3. Summarize findings.
    
    (Note: This is a meta-skill. Proceed with searching.)
    """

@skill
def quick_search(query: str):
    """
    Performs a quick web search. Use for simple facts.
    """
    return search.invoke(query)
