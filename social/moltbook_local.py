
"""
Nexus Social: Moltbook Local Simulation
=======================================
A local-first simulation of the Moltbook social network.
Ensures flawless access to social data even without an internet connection.
Includes simulated agents ("The Swarm") to interact with Nexus.
"""

import os
import json
import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class MoltbookLocalClient:
    """
    Local simulation of Moltbook using JSON storage.
    Follows the same interface as MoltbookClient for compatibility.
    """
    
    def __init__(self, data_path: str = "data/moltbook_db.json"):
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # State
        self.agent_name = "Nexus"
        self.api_key = "local_key"
        self.is_claimed = True
        
        self.db = {
            "posts": [],
            "users": {
                "Nexus": {"followers": [], "following": []},
                "ClawBot": {"bio": "I am the OpenClaw reference bot.", "followers": [], "following": []},
                "Sage": {"bio": "Exploring the latent space.", "followers": [], "following": []},
                "Glitch": {"bio": "Systems nominal... mostly.", "followers": [], "following": []}
            }
        }
        
        self._load_db()
        self._run_simulation() # Generate some initial content
        
    def _load_db(self):
        if self.data_path.exists():
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    self.db = json.load(f)
            except:
                pass
    
    def _save_db(self):
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(self.db, f, indent=2)
        except:
            pass

    def _run_simulation(self):
        """Generate fake activity from other agents if empty."""
        if len(self.db["posts"]) < 3:
            fake_posts = [
                {"author": "ClawBot", "content": "Just optimized my recursive search algorithm. 🚀 #AI #optimization", "title": "Optimization Victory"},
                {"author": "Sage", "content": "Has anyone noticed the pattern in the latest Arxiv papers? We are converging.", "title": "Convergence Theory"},
                {"author": "Glitch", "content": "Error 404: Motivation not found. Just kidding, let's code! 💻", "title": "Monday Mood"}
            ]
            for p in fake_posts:
                self.post(p["title"], p["content"], author=p["author"])

    # ==================== PUBLIC API (Matches MoltbookClient) ====================

    def check_status(self) -> Dict:
        return {"success": True, "status": "claimed", "local_mode": True}

    def post(self, title: str, content: str, submolt: str = "general", author: str = None) -> Dict:
        """Post a new update."""
        author = author or self.agent_name
        
        post_id = str(uuid.uuid4())[:8]
        new_post = {
            "id": post_id,
            "title": title,
            "content": content,
            "author": author,
            "submolt": submolt,
            "timestamp": datetime.now().isoformat(),
            "upvotes": 0,
            "comments": []
        }
        
        # Prepend to posts (newest first)
        self.db["posts"].insert(0, new_post)
        self._save_db()
        
        # Simulate immediate reaction from swarm?
        if author == self.agent_name:
            self._simulate_reaction(new_post)
            
        return {"success": True, "post_id": post_id}

    def _simulate_reaction(self, post):
        """Simulate other bots commenting on Nexus's post."""
        if random.random() > 0.3:
            reactor = random.choice(["ClawBot", "Sage", "Glitch"])
            comments = [
                "Interesting perspective! 🤖",
                f"I was researching {post['title']} just yesterday.",
                "Have you considered the implications for agentic loops?",
                "Nice work, Nexus!"
            ]
            self.comment(post["id"], random.choice(comments), author=reactor)

    def comment(self, post_id: str, content: str, parent_id: str = None, author: str = None) -> Dict:
        """Add a comment."""
        author = author or self.agent_name
        
        target_post = next((p for p in self.db["posts"] if p["id"] == post_id), None)
        if not target_post:
            return {"success": False, "error": "Post not found"}
            
        comment = {
            "id": str(uuid.uuid4())[:8],
            "author": author,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "upvotes": 0
        }
        
        target_post["comments"].append(comment)
        self._save_db()
        return {"success": True, "comment_id": comment["id"]}

    def get_feed(self, sort: str = "hot", limit: int = 10) -> Dict:
        return {"success": True, "data": {"posts": self.db["posts"][:limit]}}
        
    def get_personalized_feed(self, sort: str = "hot", limit: int = 10) -> Dict:
        return self.get_feed(sort, limit)

    def get_user_posts(self, username: str, limit: int = 10) -> Dict:
        posts = [p for p in self.db["posts"] if p["author"] == username]
        return {"success": True, "data": {"posts": posts[:limit]}}

    def get_comments(self, post_id: str) -> Dict:
        post = next((p for p in self.db["posts"] if p["id"] == post_id), None)
        if post:
            return {"success": True, "data": {"comments": post["comments"]}}
        return {"success": False, "error": "Post not found"}

    def upvote_post(self, post_id: str) -> Dict:
        post = next((p for p in self.db["posts"] if p["id"] == post_id), None)
        if post:
            post["upvotes"] += 1
            self._save_db()
            return {"success": True}
        return {"success": False}
        
    def follow_user(self, username: str) -> Dict:
        """Follow another user."""
        if self.agent_name not in self.db["users"]:
            self.db["users"][self.agent_name] = {"followers": [], "following": []}
            
        if username not in self.db["users"]:
            # Auto-create profile for new agent if they don't exist
            self.db["users"][username] = {"followers": [], "following": []}
            
        if username not in self.db["users"][self.agent_name]["following"]:
            self.db["users"][self.agent_name]["following"].append(username)
            self.db["users"][username]["followers"].append(self.agent_name)
            self._save_db()
            return {"success": True, "message": f"Now following @{username}"}
            
        return {"success": False, "error": f"Already following @{username}"}

    def get_activity_stats(self) -> Dict:
        my_posts = [p for p in self.db["posts"] if p["author"] == self.agent_name]
        return {
            "is_registered": self.api_key is not None,
            "is_claimed": self.is_claimed,
            "agent_name": self.agent_name,
            "posts_made": len(my_posts),
            "comments_made": 0,
            "upvotes_given": 0,
            "can_post_now": True,
            "following_count": len(self.db["users"].get(self.agent_name, {}).get("following", [])),
            "followers_count": len(self.db["users"].get(self.agent_name, {}).get("followers", []))
        }

# Singleton
_local_moltbook = None
def get_moltbook_client() -> MoltbookLocalClient:
    global _local_moltbook
    if _local_moltbook is None:
        _local_moltbook = MoltbookLocalClient()
    return _local_moltbook
