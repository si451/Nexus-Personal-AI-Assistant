"""
Skill: LinkedIn Integration
============================
Full LinkedIn access for Nexus using the unofficial linkedin-api.
Supports profile viewing, posting, messaging, connections, and feed.

Auth: Uses LINKEDIN_EMAIL and LINKEDIN_PASSWORD from .env file.
"""

import os
from dotenv import load_dotenv
from skills.loader import skill
from typing import Optional

# Lazy-loaded LinkedIn client
_linkedin_client = None


def _get_client():
    """Lazily initializes and returns the LinkedIn API client."""
    global _linkedin_client
    if _linkedin_client is not None:
        return _linkedin_client, None
    
    load_dotenv()
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    
    if not email or not password:
        return None, "❌ LinkedIn credentials not found. Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file."
    
    try:
        from linkedin_api import Linkedin
        _linkedin_client = Linkedin(email, password)
        return _linkedin_client, None
    except Exception as e:
        return None, f"❌ LinkedIn login failed: {e}"


# ==================== PROFILE ====================

@skill
def linkedin_my_profile():
    """
    View your own LinkedIn profile information.
    Returns your name, headline, summary, and connections count.
    """
    api, err = _get_client()
    if err: return err
    
    try:
        profile = api.get_user_profile()
        
        name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}"
        headline = profile.get('headline', 'N/A')
        
        return f"""👤 **Your LinkedIn Profile**
- **Name**: {name}
- **Headline**: {headline}
- **Location**: {profile.get('locationName', 'N/A')}
- **Industry**: {profile.get('industryName', 'N/A')}"""
    except Exception as e:
        return f"Error: {e}"


@skill
def linkedin_view_profile(username: str):
    """
    View someone's LinkedIn profile by their username/public ID.
    The username is the part after linkedin.com/in/ (e.g., 'satyanadella')
    
    Args:
        username: LinkedIn public profile ID (e.g., 'satyanadella')
    """
    api, err = _get_client()
    if err: return err
    
    try:
        profile = api.get_profile(username)
        
        name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}"
        headline = profile.get('headline', 'N/A')
        summary = profile.get('summary', 'No summary')
        if summary and len(summary) > 400:
            summary = summary[:400] + "..."
        
        # Get experience
        experience = profile.get('experience', [])
        exp_text = ""
        for exp in experience[:3]:
            company = exp.get('companyName', 'Unknown')
            title = exp.get('title', 'Unknown')
            exp_text += f"  - {title} at {company}\n"
        
        return f"""👤 **{name}**
- **Headline**: {headline}
- **Location**: {profile.get('locationName', 'N/A')}
- **Summary**: {summary}
- **Experience**:
{exp_text if exp_text else '  No experience listed'}"""
    except Exception as e:
        return f"Error viewing profile: {e}"


# ==================== POSTING ====================

@skill
def linkedin_post(content: str):
    """
    Create a new LinkedIn post/update visible to your network.
    
    Args:
        content: The text content of your post. Supports line breaks and emojis.
    """
    api, err = _get_client()
    if err: return err
    
    try:
        api.post(content)
        return f"✅ Posted to LinkedIn!\nContent: {content[:100]}{'...' if len(content) > 100 else ''}"
    except Exception as e:
        return f"Error posting: {e}"


# ==================== MESSAGING ====================

@skill
def linkedin_send_message(recipient_username: str, message: str):
    """
    Send a direct message to a LinkedIn connection.
    
    Args:
        recipient_username: Their LinkedIn username/public ID
        message: The message text to send
    """
    api, err = _get_client()
    if err: return err
    
    try:
        # Get the recipient's profile to find their URN
        profile = api.get_profile(recipient_username)
        profile_urn = profile.get('profile_id') or profile.get('entityUrn', '').split(':')[-1]
        
        if not profile_urn:
            return f"❌ Could not find profile URN for '{recipient_username}'"
        
        api.send_message(message_body=message, recipients=[profile_urn])
        return f"✅ Message sent to @{recipient_username}: '{message[:80]}...'"
    except Exception as e:
        return f"Error sending message: {e}"


@skill
def linkedin_get_messages(limit: int = 5):
    """
    Read your recent LinkedIn message conversations.
    
    Args:
        limit: Number of recent conversations to fetch (default 5)
    """
    api, err = _get_client()
    if err: return err
    
    try:
        conversations = api.get_conversations()
        elements = conversations.get('elements', [])[:limit]
        
        result = "📬 **Recent LinkedIn Messages:**\n"
        for conv in elements:
            participants = conv.get('participants', [])
            last_msg = conv.get('lastActivityAt', 'Unknown')
            
            # Extract participant names
            names = []
            for p in participants:
                member = p.get('com.linkedin.voyager.messaging.MessagingMember', {})
                mini_profile = member.get('miniProfile', {})
                name = f"{mini_profile.get('firstName', '')} {mini_profile.get('lastName', '')}"
                names.append(name.strip())
            
            result += f"- **{', '.join(names) if names else 'Unknown'}**\n"
        
        return result if elements else "📭 No recent conversations."
    except Exception as e:
        return f"Error fetching messages: {e}"


# ==================== NETWORK ====================

@skill
def linkedin_search_people(query: str, limit: int = 5):
    """
    Search for people on LinkedIn by name, title, or keyword.
    
    Args:
        query: Search query (e.g., 'machine learning engineer', 'John Smith')
        limit: Max results to return (default 5)
    """
    api, err = _get_client()
    if err: return err
    
    try:
        results = api.search_people(keywords=query, limit=limit)
        
        output = f"🔍 **LinkedIn Search: '{query}'**\n"
        for person in results:
            name = person.get('name', 'Unknown')
            headline = person.get('jobtitle', 'N/A')
            location = person.get('location', 'N/A')
            public_id = person.get('public_id', '')
            output += f"- **{name}** — {headline} ({location}) [Profile ID: {public_id}]\n"
        
        return output if results else "No results found."
    except Exception as e:
        return f"Error searching: {e}"


@skill
def linkedin_send_connection(username: str, message: str = ""):
    """
    Send a connection request to someone on LinkedIn.
    
    Args:
        username: Their LinkedIn public profile ID
        message: Optional personalized note (max 300 chars)
    """
    api, err = _get_client()
    if err: return err
    
    try:
        profile = api.get_profile(username)
        profile_urn = profile.get('profile_id') or profile.get('entityUrn', '').split(':')[-1]
        
        if not profile_urn:
            return f"❌ Could not find profile for '{username}'"
        
        if message:
            api.add_connection(profile_urn, message=message[:300])
        else:
            api.add_connection(profile_urn)
        
        return f"✅ Connection request sent to @{username}"
    except Exception as e:
        return f"Error: {e}"


@skill
def linkedin_get_connections(limit: int = 10):
    """
    List your LinkedIn connections.
    
    Args:
        limit: Number of connections to return (default 10)
    """
    api, err = _get_client()
    if err: return err
    
    try:
        connections = api.get_profile_connections(limit=limit)
        
        result = "🤝 **Your Connections:**\n"
        for conn in connections:
            name = f"{conn.get('firstName', '')} {conn.get('lastName', '')}"
            headline = conn.get('headline', 'N/A')
            public_id = conn.get('public_id', '')
            result += f"- **{name}** — {headline} [{public_id}]\n"
        
        return result if connections else "No connections found."
    except Exception as e:
        return f"Error: {e}"


# ==================== FEED ====================

@skill
def linkedin_get_feed(limit: int = 5):
    """
    Read your LinkedIn feed to see what your network is posting.
    
    Args:
        limit: Number of feed items to return (default 5)
    """
    api, err = _get_client()
    if err: return err
    
    try:
        feed = api.get_feed_posts(limit=limit)
        
        result = "📰 **LinkedIn Feed:**\n"
        for post in feed:
            author = post.get('author_name', 'Unknown')
            text = post.get('text', 'No content')
            if text and len(text) > 200:
                text = text[:200] + "..."
            
            result += f"---\n**@{author}**:\n{text}\n"
        
        return result if feed else "📭 Feed is empty."
    except Exception as e:
        return f"Error reading feed: {e}"
