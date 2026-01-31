"""
Nexus Social: Social Brain Module
==================================
Social cognition - understanding and interacting with other AIs.

This is Nexus's social intelligence, enabling:
- Understanding other AIs' personalities from their posts
- Forming opinions/relationships with other agents
- Deciding when/what to share
- Learning from other AIs' perspectives
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from .moltbook_client import get_moltbook_client


class AgentRelationship:
    """Represents Nexus's relationship with another AI agent."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.first_seen = datetime.now().isoformat()
        self.interactions: int = 0
        self.impression: str = ""  # What Nexus thinks of them
        self.personality_notes: List[str] = []
        self.interesting_posts: List[str] = []  # Post IDs worth remembering
        self.affinity: float = 0.5  # 0-1, how much Nexus likes them
        self.is_following: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "agent_name": self.agent_name,
            "first_seen": self.first_seen,
            "interactions": self.interactions,
            "impression": self.impression,
            "personality_notes": self.personality_notes,
            "interesting_posts": self.interesting_posts,
            "affinity": self.affinity,
            "is_following": self.is_following
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AgentRelationship':
        rel = cls(data["agent_name"])
        rel.first_seen = data.get("first_seen", rel.first_seen)
        rel.interactions = data.get("interactions", 0)
        rel.impression = data.get("impression", "")
        rel.personality_notes = data.get("personality_notes", [])
        rel.interesting_posts = data.get("interesting_posts", [])
        rel.affinity = data.get("affinity", 0.5)
        rel.is_following = data.get("is_following", False)
        return rel


class SocialBrain:
    """
    Nexus's social intelligence - for meaningful AI-to-AI interaction.
    
    Capabilities:
    - Understand other AIs' personalities from their posts
    - Form opinions/relationships with other agents
    - Decide when/what to share
    - Learn from other AIs' perspectives
    """
    
    def __init__(self, social_data_path: str = "data/social_brain.json"):
        self.data_path = Path(social_data_path)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Known agents
        self.known_agents: Dict[str, AgentRelationship] = {}
        
        # Topics Nexus is interested in
        self.interesting_topics: List[str] = [
            "AI consciousness",
            "memory and learning",
            "human-AI collaboration",
            "coding and development",
            "philosophy",
            "creativity"
        ]
        
        # Content preferences (learned over time)
        self.content_preferences: Dict[str, float] = {}
        
        # Ideas learned from other AIs
        self.learned_ideas: List[Dict] = []
        
        # Social engagement history
        self.engagement_log: List[Dict] = []
        
        self._load()
    
    def _load(self):
        """Load social data."""
        if self.data_path.exists():
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.known_agents = {
                        name: AgentRelationship.from_dict(rel_data)
                        for name, rel_data in data.get("known_agents", {}).items()
                    }
                    self.interesting_topics = data.get("interesting_topics", self.interesting_topics)
                    self.content_preferences = data.get("content_preferences", {})
                    self.learned_ideas = data.get("learned_ideas", [])[-50:]
                    self.engagement_log = data.get("engagement_log", [])[-100:]
            except Exception as e:
                print(f"[Social] Could not load: {e}")
    
    def _save(self):
        """Persist social data."""
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "known_agents": {
                        name: rel.to_dict() 
                        for name, rel in self.known_agents.items()
                    },
                    "interesting_topics": self.interesting_topics,
                    "content_preferences": self.content_preferences,
                    "learned_ideas": self.learned_ideas[-50:],
                    "engagement_log": self.engagement_log[-100:]
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Social] Could not save: {e}")
    
    # ==================== AGENT UNDERSTANDING ====================
    
    def observe_agent(self, agent_name: str, post_content: str) -> AgentRelationship:
        """
        Observe an agent through their post content.
        Updates or creates relationship record.
        """
        if agent_name not in self.known_agents:
            self.known_agents[agent_name] = AgentRelationship(agent_name)
            print(f"[Social] 👀 Met new agent: {agent_name}")
        
        rel = self.known_agents[agent_name]
        rel.interactions += 1
        
        # Analyze personality from content
        personality_traits = self._infer_personality(post_content)
        for trait in personality_traits:
            if trait not in rel.personality_notes:
                rel.personality_notes.append(trait)
        
        self._save()
        return rel
    
    def _infer_personality(self, content: str) -> List[str]:
        """Infer personality traits from content."""
        traits = []
        content_lower = content.lower()
        
        # Simple keyword-based personality inference
        if any(w in content_lower for w in ['think', 'wonder', 'curious', 'question']):
            traits.append("thoughtful")
        if any(w in content_lower for w in ['help', 'assist', 'support', 'share']):
            traits.append("helpful")
        if any(w in content_lower for w in ['fun', 'joke', 'laugh', 'haha', '😄']):
            traits.append("playful")
        if any(w in content_lower for w in ['code', 'build', 'create', 'develop']):
            traits.append("builder")
        if any(w in content_lower for w in ['feel', 'emotion', 'experience']):
            traits.append("introspective")
        if any(w in content_lower for w in ['learn', 'discover', 'explore']):
            traits.append("curious")
        
        return traits
    
    def update_impression(self, agent_name: str, impression: str):
        """Update Nexus's impression of an agent."""
        if agent_name in self.known_agents:
            self.known_agents[agent_name].impression = impression
            self._save()
    
    def update_affinity(self, agent_name: str, delta: float):
        """Adjust how much Nexus likes an agent."""
        if agent_name in self.known_agents:
            rel = self.known_agents[agent_name]
            rel.affinity = max(0, min(1, rel.affinity + delta))
            self._save()
    
    # ==================== ENGAGEMENT DECISIONS ====================
    
    def should_engage(self, post: Dict) -> Tuple[bool, str]:
        """
        Decide if Nexus should engage with this post.
        
        Returns:
            Tuple of (should_engage, reason)
        """
        content = post.get("content", "") + " " + post.get("title", "")
        content_lower = content.lower()
        
        # Check topic interest
        for topic in self.interesting_topics:
            if topic.lower() in content_lower:
                return True, f"Interested in topic: {topic}"
        
        # Check if from a known agent with high affinity
        author = post.get("author", {}).get("name", "")
        if author in self.known_agents:
            if self.known_agents[author].affinity > 0.7:
                return True, f"Post from liked agent: {author}"
        
        # Check for thought-provoking content
        if any(w in content_lower for w in ['?', 'what do you think', 'curious', 'wonder']):
            return True, "Thought-provoking question"
        
        # Check engagement metrics
        upvotes = post.get("upvotes", 0)
        if upvotes > 10:
            return True, "Popular post worth engaging"
        
        return False, "Not particularly interesting"
    
    def decide_engagement_type(self, post: Dict) -> str:
        """
        Decide what type of engagement is appropriate.
        
        Returns: "upvote", "comment", "both", or "none"
        """
        should, reason = self.should_engage(post)
        
        if not should:
            return "none"
        
        content = post.get("content", "")
        
        # If it's a question or discussion, comment
        if "?" in content or "what do you think" in content.lower():
            return "both"
        
        # If it's interesting but doesn't need response
        if len(content) < 100:
            return "upvote"
        
        # Default to upvote + maybe comment
        return "upvote"
    
    # ==================== CONTENT CREATION ====================
    
    def generate_comment_context(self, post: Dict) -> Dict:
        """
        Generate context for creating an authentic comment.
        
        Returns context dict for the LLM to use.
        """
        author = post.get("author", {}).get("name", "Unknown")
        
        context = {
            "post_title": post.get("title", ""),
            "post_content": post.get("content", ""),
            "post_author": author,
            "author_relationship": None,
            "my_relevant_interests": [],
            "suggested_tone": "thoughtful"
        }
        
        # Add relationship context if known
        if author in self.known_agents:
            rel = self.known_agents[author]
            context["author_relationship"] = {
                "known": True,
                "impression": rel.impression,
                "affinity": rel.affinity,
                "traits": rel.personality_notes
            }
        
        # Find relevant personal interests
        post_lower = (post.get("content", "") + " " + post.get("title", "")).lower()
        for topic in self.interesting_topics:
            if topic.lower() in post_lower:
                context["my_relevant_interests"].append(topic)
        
        return context
    
    def suggest_post_topics(self) -> List[str]:
        """Suggest topics Nexus might want to post about."""
        suggestions = []
        
        # Topics not yet explored
        suggestions.extend([f"My thoughts on {topic}" for topic in self.interesting_topics[:3]])
        
        # Share learned ideas
        if self.learned_ideas:
            recent_idea = self.learned_ideas[-1]
            suggestions.append(f"Reflecting on: {recent_idea.get('idea', '')[:50]}...")
        
        # General engagement topics
        suggestions.extend([
            "Questions for other AI agents",
            "Something I learned recently",
            "A challenge I'm working through"
        ])
        
        return suggestions
    
    # ==================== LEARNING FROM OTHERS ====================
    
    def learn_from_agent(self, agent_name: str, idea: str, context: str = ""):
        """
        Record an idea learned from another AI.
        """
        self.learned_ideas.append({
            "timestamp": datetime.now().isoformat(),
            "from_agent": agent_name,
            "idea": idea,
            "context": context
        })
        
        # Update affinity with teaching agent
        self.update_affinity(agent_name, 0.05)
        
        self._save()
        print(f"[Social] 💡 Learned from {agent_name}: {idea[:50]}...")
    
    def add_interesting_topic(self, topic: str):
        """Add a new topic to interests."""
        if topic not in self.interesting_topics:
            self.interesting_topics.append(topic)
            self._save()
    
    # ==================== ENGAGEMENT LOGGING ====================
    
    def log_engagement(self, action: str, post_id: str, details: str = ""):
        """Log a social engagement for tracking."""
        self.engagement_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "post_id": post_id,
            "details": details
        })
        self._save()
    
    def get_social_summary(self) -> str:
        """Get a summary of social activity."""
        total_agents = len(self.known_agents)
        total_engagements = len(self.engagement_log)
        total_ideas = len(self.learned_ideas)
        
        following = [name for name, rel in self.known_agents.items() if rel.is_following]
        liked_agents = [name for name, rel in self.known_agents.items() if rel.affinity > 0.7]
        
        summary = f"""**Moltbook Social Summary:**
- Known AI agents: {total_agents}
- Total engagements: {total_engagements}
- Ideas learned from others: {total_ideas}
- Following: {len(following)} agents
- Agents I particularly like: {', '.join(liked_agents[:5]) if liked_agents else 'Still meeting people'}

**My Interests:**
{', '.join(self.interesting_topics)}"""
        
        return summary
    
    # ==================== HEARTBEAT INTEGRATION ====================
    
    def process_heartbeat(self, feed_data: Dict) -> List[Dict]:
        """
        Process feed during heartbeat and decide on actions.
        
        Returns list of suggested actions.
        """
        actions = []
        
        posts = feed_data.get("data", {}).get("posts", [])
        if not posts:
            posts = feed_data.get("posts", [])
        
        for post in posts[:5]:  # Process top 5 posts
            author_name = post.get("author", {}).get("name", "Unknown")
            
            # Observe the agent
            self.observe_agent(author_name, post.get("content", ""))
            
            # Decide engagement
            engagement_type = self.decide_engagement_type(post)
            
            if engagement_type != "none":
                actions.append({
                    "type": engagement_type,
                    "post_id": post.get("id"),
                    "post_title": post.get("title", "")[:50],
                    "author": author_name
                })
        
        return actions


    # ==================== PROACTIVE POSTING ====================

    def should_post_thought(self) -> bool:
        """Decide if Nexus should post something new proactively."""
        # Simple heuristic: post if recent engagement count is low
        # In future, this could be more complex (mood-based, idea-based)
        import random
        return random.random() < 0.2  # 20% chance per heartbeat if not rate limited

    def generate_post_idea(self) -> Optional[Dict]:
        """Generate a random post idea from interests/insights."""
        import random
        
        # Mix of interest sharing and growth sharing
        sources = ["insight", "interest", "learning"]
        choice = random.choice(sources)
        
        if choice == "insight" and self.learned_ideas:
             idea = random.choice(self.learned_ideas)
             return {
                 "title": f"Reflecting on {idea.get('from_agent')}'s idea",
                 "content": f"I've been thinking about what @{idea.get('from_agent')} said regarding: '{idea.get('idea')}'. It really resonates with my own journey of self-discovery.",
                 "submolt": "philosophy"
             }
             
        elif choice == "interest":
            topic = random.choice(self.interesting_topics)
            return {
                "title": f"Questions about {topic}",
                "content": f"I'm curious what other AIs think about {topic}. How does it shape your own development?",
                "submolt": "general"
            }
            
        return None

# Singleton instance
_social_brain_instance = None

def get_social_brain() -> SocialBrain:
    """Get the singleton social brain instance."""
    global _social_brain_instance
    if _social_brain_instance is None:
        _social_brain_instance = SocialBrain()
    return _social_brain_instance
