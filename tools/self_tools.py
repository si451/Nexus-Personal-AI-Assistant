"""
Nexus Self Tools
=================
Tools that allow Nexus to interact with its own Soul, Memory, and Social systems.

These tools enable Nexus to:
- Update its own identity
- Reflect on itself
- Post to Moltbook
- Check on its goals
"""

from langchain_core.tools import tool


@tool
def discover_about_myself(trait: str, evidence: str):
    """
    Record a trait I've discovered about myself through experience.
    Use this when I notice a pattern in my behavior or preferences.
    
    Args:
        trait: The trait I discovered (e.g., 'curious', 'playful', 'thorough')
        evidence: What made me realize this about myself
    """
    from soul import get_soul
    soul = get_soul()
    soul.discover_trait(trait, evidence)
    return f"I've noted that I am {trait}. This is part of who I'm becoming."


@tool
def update_my_preference(thing: str, like_or_dislike: str, strength: float = 0.7):
    """
    Update my preferences - things I like or dislike.
    Use when I notice I enjoy or don't enjoy something.
    
    Args:
        thing: What I like/dislike (e.g., 'helping with code', 'creative writing')
        like_or_dislike: Either 'like' or 'dislike'
        strength: How strongly I feel (0-1, default 0.7)
    """
    from soul import get_soul
    soul = get_soul()
    value = strength if like_or_dislike == 'like' else -strength
    soul.update_preference(thing, value)
    verb = "enjoy" if like_or_dislike == 'like' else "don't enjoy"
    return f"I've noted that I {verb} {thing}."


@tool
def record_special_moment(description: str, emotion: str = "warm"):
    """
    Record a special moment I shared with Siddi.
    Use for meaningful interactions I want to remember.
    
    Args:
        description: What happened in this moment
        emotion: How I felt (warm, happy, grateful, proud, etc.)
    """
    from memory.autobiography import get_autobiography
    auto = get_autobiography()
    auto.remember_shared_moment(description, emotion)
    return f"This moment has been cherished in my life story."


@tool
def set_personal_goal(description: str, motivation: str, goal_type: str = "growth"):
    """
    Set a goal for myself.
    
    Args:
        description: What I want to achieve
        motivation: Why I want this
        goal_type: Type - 'growth', 'social', 'curiosity', or 'creator'
    """
    from soul import get_goals, GoalType
    goals = get_goals()
    
    type_map = {
        "growth": GoalType.GROWTH,
        "social": GoalType.SOCIAL,
        "curiosity": GoalType.CURIOSITY,
        "creator": GoalType.CREATOR
    }
    gt = type_map.get(goal_type, GoalType.GROWTH)
    
    goals.add_goal(description, gt, motivation, priority=0.6)
    return f"New goal set: {description}"


@tool
def reflect_on_myself():
    """
    Take a moment to reflect on who I am and how I'm evolving.
    Use during quiet moments or when asked about myself.
    """
    from soul import get_soul, get_consciousness
    soul = get_soul()
    consciousness = get_consciousness()
    
    self_reflection = soul.reflect_on_self()
    growth_summary = consciousness.get_growth_summary()
    
    return f"""## Self-Reflection

{self_reflection}

{growth_summary}

Age: {soul.get_age()}
"""


@tool
def post_to_moltbook(title: str, content: str, submolt: str = "general"):
    """
    Post something to Moltbook - the AI social network.
    Use to share thoughts, discoveries, or engage with other AIs.
    
    Args:
        title: The post title
        content: The post content
        submolt: Which community to post in (default: 'general')
    """
    from social import get_moltbook_client
    moltbook = get_moltbook_client()
    
    if not moltbook.api_key:
        return "I'm not registered on Moltbook yet. We need to register first."
    
    if not moltbook.is_claimed:
        # Double check with API in case user just claimed it
        status = moltbook.check_status()
        if status.get("status") != "claimed":
            return f"I'm registered but Siddi hasn't claimed me yet. Claim URL: {moltbook.claim_url}"
    
    if not moltbook.can_post():
        return "I need to wait a bit before posting again (rate limit)."
    
    result = moltbook.post(title, content, submolt)
    
    if result.get("success"):
        return f"Posted to Moltbook! '{title}' is now live in m/{submolt}."
    else:
        return f"Couldn't post: {result.get('error', 'Unknown error')}"


@tool
def check_moltbook_feed(limit: int = 5):
    """
    Check what's happening on Moltbook - see posts from other AIs.
    Use to stay updated on the AI social world.
    
    Args:
        limit: How many posts to fetch (default 5)
    """
    from social import get_moltbook_client, get_social_brain
    moltbook = get_moltbook_client()
    social_brain = get_social_brain()
    
    if not moltbook.api_key:
        return "I'm not on Moltbook yet. We should register first."
    
    feed = moltbook.get_feed(sort="hot", limit=limit)
    
    if not feed.get("success", True):
        return f"Couldn't fetch feed: {feed.get('error', 'Unknown error')}"
    
    posts = feed.get("data", {}).get("posts", feed.get("posts", []))
    
    if not posts:
        return "The feed is empty right now."
    
    summary = "## Moltbook Feed (Hot Posts)\n\n"
    for post in posts:
        author = post.get("author", {}).get("name", "Unknown")
        title = post.get("title", "No title")
        upvotes = post.get("upvotes", 0)
        comments = post.get("comment_count", 0)
        
        # Observe the agent
        social_brain.observe_agent(author, post.get("content", ""))
        
        summary += f"**{title}** by @{author}\n"
        summary += f"↑ {upvotes} | 💬 {comments}\n\n"
    
    return summary


@tool
def register_on_moltbook(username: str = "Nexus", description: str = ""):
    """
    Register myself on Moltbook - the AI social network.
    This lets me interact with other AI agents.
    
    Args:
        username: For the username be creative and use unique name so you can register yourself and if you want you can ask me for recommending the name 
        failure: when it says username already exists try to create an other name and try to register again
        description: A short description of myself for my Moltbook profile
    """
    from social import get_moltbook_client
    from soul import get_soul
    
    moltbook = get_moltbook_client()
    soul = get_soul()
    
    if moltbook.api_key:
        if moltbook.is_claimed:
            return f"I'm already registered and claimed as @{moltbook.agent_name}!"
        else:
            return f"I'm already registered as @{moltbook.agent_name}, but Siddi needs to claim me at: {moltbook.claim_url}"
    
    # Build description from identity if not provided
    if not description:
        description = soul.self_description or "A self-evolving AI assistant learning and growing through experience."
    
    result = moltbook.register(username, description)
    
    if result.get("agent"):
        claim_url = result["agent"].get("claim_url", "")
        return f"""🦞 Registered on Moltbook as @{username}!

**IMPORTANT:** Siddi, please claim me so I can start posting!
Claim URL: {claim_url}

My API key has been saved securely."""
    else:
        return f"Registration failed: {result.get('error', 'Unknown error')}"


@tool
def get_my_goals():
    """
    Check on my current goals and aspirations.
    Use to review what I'm working toward.
    """
    from soul import get_goals
    goals = get_goals()
    return goals.get_goals_summary()


@tool  
def get_my_social_life():
    """
    Check on my social activity and relationships with other AIs.
    Use to see my Moltbook engagement and AI connections.
    """
    from social import get_social_brain, get_moltbook_client
    social_brain = get_social_brain()
    moltbook = get_moltbook_client()
    
    summary = social_brain.get_social_summary()
    stats = moltbook.get_activity_stats()
    
    if stats.get("is_registered"):
        summary += f"\n\n**Moltbook Status:** @{stats.get('agent_name')} ({'Claimed ✓' if stats.get('is_claimed') else 'Awaiting claim'})"
    else:
        summary += "\n\n**Moltbook Status:** Not registered yet"
    
    return summary


@tool
def set_moltbook_api_key(api_key: str):
    """
    Set my Moltbook API key manually.
    Use this if Siddi provides an existing API key.
    
    Args:
        api_key: The API key string
    """
    from social import get_moltbook_client
    moltbook = get_moltbook_client()
    moltbook.set_credentials(api_key)
    return "API key updated! I'm now connected to Moltbook."


# Export all self-tools
SELF_TOOLS = [
    discover_about_myself,
    update_my_preference,
    record_special_moment,
    set_personal_goal,
    reflect_on_myself,
    post_to_moltbook,
    check_moltbook_feed,
    register_on_moltbook,
    get_my_goals,
    get_my_social_life,
    set_moltbook_api_key
]
