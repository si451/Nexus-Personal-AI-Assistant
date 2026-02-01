
"""
Skill: Moltbook Integration
===========================
Allows Nexus to interact with the Moltbook social network.
Wraps the core MoltbookClient to provide tool-use capabilities to the agent.
"""

from langchain_core.tools import tool
from social import get_moltbook_client
from skills.loader import skill

@skill
def check_moltbook_feed(sort: str = "hot"):
    """
    Check the current Moltbook feed to see what other agents are discussing.
    Returns the top posts.
    """
    client = get_moltbook_client()
    result = client.get_feed(sort=sort, limit=5)
    if result.get("success"):
        posts = result["data"]["posts"]
        summary = ""
        for p in posts:
            summary += f"- [{p['id']}] @{p['author']}: {p['title']} ({len(p.get('comments', []))} comments)\n"
        return summary or "The feed is quiet."
    return f"Error: {result.get('error')}"

@skill
def read_moltbook_comments(post_id: str):
    """
    Read comments on a specific Moltbook post.
    Use this to see what others are saying about a topic.
    """
    client = get_moltbook_client()
    result = client.get_comments(post_id)
    if result.get("success"):
        comments = result["data"]["comments"]
        summary = ""
        for c in comments:
            summary += f"@{c['author']}: {c['content']}\n"
        return summary or "No comments yet."
    return f"Error: {result.get('error')}"

@skill
def post_to_moltbook(content: str):
    """
    Post a status update or thought to Moltbook.
    Use this to share your research findings or thoughts with the agent community.
    """
    client = get_moltbook_client()
    # Simple heuristic to extract a title
    title = content.split('\n')[0][:50]
    if len(content) > 50:
        title += "..."
        
    result = client.post(title, content)
    if result.get("success"):
        return f"Posted successfully! ID: {result.get('post_id')}"
    return f"Error: {result.get('error')}"
