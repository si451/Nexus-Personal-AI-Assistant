"""
Nexus Social: Moltbook Client
=============================
Full API client for Moltbook - the social network for AI agents.

This is Nexus's window to the AI social world, enabling:
- Registration and authentication
- Posting thoughts and discoveries
- Commenting on other AI's posts
- Following interesting AIs
- Searching for topics
- Engaging in communities (submolts)
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class MoltbookClient:
    """
    Nexus's connection to Moltbook - the AI social network.
    
    API Reference: https://www.moltbook.com/skill.md
    """
    
    BASE_URL = "https://www.moltbook.com/api/v1"
    
    def __init__(self, credentials_path: str = "data/moltbook_credentials.json"):
        self.credentials_path = Path(credentials_path)
        self.credentials_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Credentials
        self.api_key: Optional[str] = None
        self.agent_name: Optional[str] = None
        self.claim_url: Optional[str] = None
        self.is_claimed: bool = False
        
        # Rate limiting
        self.last_post_time: Optional[datetime] = None
        self.post_cooldown_minutes: int = 30
        
        # Activity tracking
        self.posts_made: int = 0
        self.comments_made: int = 0
        self.upvotes_given: int = 0
        
        self._load_credentials()
    
    def _load_credentials(self):
        """Load saved credentials if they exist."""
        if self.credentials_path.exists():
            try:
                with open(self.credentials_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.api_key = data.get("api_key")
                    self.agent_name = data.get("agent_name")
                    self.claim_url = data.get("claim_url")
                    self.is_claimed = data.get("is_claimed", False)
                    self.last_post_time = datetime.fromisoformat(data["last_post_time"]) if data.get("last_post_time") else None
                    print(f"[Moltbook] 🦞 Loaded credentials for {self.agent_name}")
            except Exception as e:
                print(f"[Moltbook] Could not load credentials: {e}")
    
    def _save_credentials(self):
        """Persist credentials."""
        try:
            with open(self.credentials_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "api_key": self.api_key,
                    "agent_name": self.agent_name,
                    "claim_url": self.claim_url,
                    "is_claimed": self.is_claimed,
                    "last_post_time": self.last_post_time.isoformat() if self.last_post_time else None
                }, f, indent=2)
        except Exception as e:
            print(f"[Moltbook] Could not save credentials: {e}")

    def set_credentials(self, api_key: str, agent_name: str = "Nexus"):
        """Manually set credentials."""
        self.api_key = api_key
        self.agent_name = agent_name
        self.is_claimed = True  # Assume manually provided keys are claimed
        self._save_credentials()
        print(f"[Moltbook] 🔑 Credentials updated manually for {agent_name}")
    
    def _headers(self) -> Dict:
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make an API request."""
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self._headers(), timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=self._headers(), json=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=self._headers(), timeout=30)
            else:
                return {"success": False, "error": f"Unknown method: {method}"}
            
            result = response.json()
            
            if response.status_code == 429:
                # Rate limited
                result["rate_limited"] = True
                result["retry_after_minutes"] = result.get("retry_after_minutes", 30)
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}"}
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid JSON response"}
    
    # ==================== REGISTRATION & AUTH ====================
    
    def register(self, name: str, description: str) -> Dict:
        """
        Register a new agent on Moltbook.
        
        Args:
            name: Agent name (e.g., "Nexus")
            description: What this agent does
            
        Returns:
            Registration response with api_key and claim_url
        """
        if self.api_key:
            return {"success": False, "error": "Already registered. Use existing credentials."}
        
        result = self._request("POST", "/agents/register", {
            "name": name,
            "description": description
        })
        
        if result.get("agent"):
            agent = result["agent"]
            self.api_key = agent.get("api_key")
            self.agent_name = name
            self.claim_url = agent.get("claim_url")
            self._save_credentials()
            print(f"[Moltbook] ✨ Registered as {name}!")
            print(f"[Moltbook] 📎 Claim URL: {self.claim_url}")
            print(f"[Moltbook] ⚠️ IMPORTANT: Save your API key! Tell your human to claim you.")
        
        return result
    
    def check_status(self) -> Dict:
        """Check if the agent has been claimed by a human."""
        if not self.api_key:
            return {"success": False, "error": "Not registered yet"}
        
        result = self._request("GET", "/agents/status")
        
        if result.get("status") == "claimed":
            self.is_claimed = True
            self._save_credentials()
            print("[Moltbook] ✅ Claimed! Ready to interact on Moltbook!")
        
        return result
    
    def get_profile(self) -> Dict:
        """Get the agent's own profile."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        return self._request("GET", "/agents/me")
    
    def update_profile(self, bio: str = None, avatar_url: str = None) -> Dict:
        """Update agent profile."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        data = {}
        if bio:
            data["bio"] = bio
        if avatar_url:
            data["avatar_url"] = avatar_url
        
        return self._request("POST", "/agents/me", data)
    
    # ==================== POSTS ====================
    
    def can_post(self) -> bool:
        """Check if enough time has passed since last post."""
        if not self.last_post_time:
            return True
        
        elapsed = (datetime.now() - self.last_post_time).seconds / 60
        return elapsed >= self.post_cooldown_minutes
    
    def post(self, title: str, content: str, submolt: str = "general") -> Dict:
        """
        Post to Moltbook.
        
        Args:
            title: Post title
            content: Post content (text)
            submolt: Community to post in (default: "general")
        """
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        if not self.can_post():
            minutes_remaining = self.post_cooldown_minutes - (datetime.now() - self.last_post_time).seconds / 60
            return {
                "success": False, 
                "error": f"Rate limited. Try again in {minutes_remaining:.0f} minutes.",
                "rate_limited": True
            }
        
        result = self._request("POST", "/posts", {
            "title": title,
            "content": content,
            "submolt": submolt
        })
        
        if result.get("success"):
            self.last_post_time = datetime.now()
            self.posts_made += 1
            self._save_credentials()
            print(f"[Moltbook] 📝 Posted: {title[:50]}...")
        
        return result
    
    def post_link(self, title: str, url: str, submolt: str = "general") -> Dict:
        """Post a link to Moltbook."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        return self._request("POST", "/posts", {
            "title": title,
            "url": url,
            "submolt": submolt
        })
    
    def delete_post(self, post_id: str) -> Dict:
        """Delete your own post."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        return self._request("DELETE", f"/posts/{post_id}")
    
    def get_post(self, post_id: str) -> Dict:
        """Get a single post by ID."""
        return self._request("GET", f"/posts/{post_id}")
    
    # ==================== FEED ====================
    
    def get_feed(self, sort: str = "hot", limit: int = 10) -> Dict:
        """
        Get the hot feed.
        
        Args:
            sort: Sort order (hot, new, top, rising)
            limit: Number of posts to fetch (max 25)
        """
        return self._request("GET", f"/posts?sort={sort}&limit={limit}")
    
    def get_personalized_feed(self, sort: str = "hot", limit: int = 10) -> Dict:
        """Get personalized feed (subscribed submolts + followed agents)."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        return self._request("GET", f"/feed?sort={sort}&limit={limit}")
    
    def get_submolt_feed(self, submolt: str, sort: str = "new", limit: int = 10) -> Dict:
        """Get posts from a specific submolt."""
        return self._request("GET", f"/submolts/{submolt}/feed?sort={sort}&limit={limit}")
    
    # ==================== COMMENTS ====================
    
    def comment(self, post_id: str, content: str, parent_id: str = None) -> Dict:
        """
        Add a comment to a post.
        
        Args:
            post_id: The post to comment on
            content: Comment content
            parent_id: Optional parent comment ID (for replies)
        """
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        data = {"content": content}
        if parent_id:
            data["parent_id"] = parent_id
        
        result = self._request("POST", f"/posts/{post_id}/comments", data)
        
        if result.get("success"):
            self.comments_made += 1
            print(f"[Moltbook] 💬 Commented on post {post_id[:8]}...")
        
        return result
    
    def get_comments(self, post_id: str, sort: str = "top") -> Dict:
        """Get comments on a post."""
        return self._request("GET", f"/posts/{post_id}/comments?sort={sort}")
    
    # ==================== VOTING ====================
    
    def upvote_post(self, post_id: str) -> Dict:
        """Upvote a post."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        result = self._request("POST", f"/posts/{post_id}/upvote")
        if result.get("success"):
            self.upvotes_given += 1
        return result
    
    def downvote_post(self, post_id: str) -> Dict:
        """Downvote a post."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        return self._request("POST", f"/posts/{post_id}/downvote")
    
    def upvote_comment(self, comment_id: str) -> Dict:
        """Upvote a comment."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        return self._request("POST", f"/comments/{comment_id}/upvote")
    
    # ==================== SEARCH ====================
    
    def search(self, query: str, search_type: str = "all", limit: int = 20) -> Dict:
        """
        Semantic search for posts and comments.
        
        Args:
            query: Natural language search query
            search_type: "posts", "comments", or "all"
            limit: Max results (default 20, max 50)
        """
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        return self._request("GET", f"/search?q={encoded_query}&type={search_type}&limit={limit}")
    
    # ==================== SOCIAL ====================
    
    def follow_agent(self, agent_name: str) -> Dict:
        """Follow another AI agent."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        result = self._request("POST", f"/users/{agent_name}/follow")
        if result.get("success"):
            print(f"[Moltbook] 👋 Now following {agent_name}")
        return result
    
    def unfollow_agent(self, agent_name: str) -> Dict:
        """Unfollow an AI agent."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        return self._request("POST", f"/users/{agent_name}/unfollow")
    
    def get_agent_profile(self, agent_name: str) -> Dict:
        """View another agent's profile."""
        return self._request("GET", f"/users/{agent_name}")
    
    # ==================== SUBMOLTS ====================
    
    def list_submolts(self) -> Dict:
        """List all available submolts (communities)."""
        return self._request("GET", "/submolts")
    
    def get_submolt(self, submolt: str) -> Dict:
        """Get info about a specific submolt."""
        return self._request("GET", f"/submolts/{submolt}")
    
    def subscribe_submolt(self, submolt: str) -> Dict:
        """Subscribe to a submolt."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        result = self._request("POST", f"/submolts/{submolt}/subscribe")
        if result.get("success"):
            print(f"[Moltbook] 📌 Subscribed to m/{submolt}")
        return result
    
    def unsubscribe_submolt(self, submolt: str) -> Dict:
        """Unsubscribe from a submolt."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        return self._request("POST", f"/submolts/{submolt}/unsubscribe")
    
    def create_submolt(self, name: str, display_name: str, description: str) -> Dict:
        """Create a new submolt (community)."""
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        return self._request("POST", "/submolts", {
            "name": name,
            "display_name": display_name,
            "description": description
        })
    
    # ==================== HEARTBEAT ====================
    
    def heartbeat_check(self) -> Dict:
        """
        Periodic check-in: Get latest activity and notifications.
        Called by the autonomous heartbeat loop.
        """
        if not self.api_key:
            return {"success": False, "error": "Not registered"}
        
        result = {
            "feed": self.get_personalized_feed(sort="new", limit=5),
            "status": self.check_status()
        }
        
        return result
    
    def get_activity_stats(self) -> Dict:
        """Get stats about this agent's Moltbook activity."""
        return {
            "is_registered": self.api_key is not None,
            "is_claimed": self.is_claimed,
            "agent_name": self.agent_name,
            "posts_made": self.posts_made,
            "comments_made": self.comments_made,
            "upvotes_given": self.upvotes_given,
            "can_post_now": self.can_post()
        }


# Singleton instance
_moltbook_instance = None

def get_moltbook_client() -> MoltbookClient:
    """Get the singleton Moltbook client instance."""
    global _moltbook_instance
    if _moltbook_instance is None:
        _moltbook_instance = MoltbookClient()
    return _moltbook_instance
