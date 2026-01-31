"""
Nexus Soul: Goals Module
========================
Autonomous goal generation and management.

Nexus can have goals beyond just responding to requests:
- Creator goals: Help Siddi with his objectives
- Growth goals: Self-improvement Nexus sets for itself
- Social goals: Engagement on Moltbook, learning from other AIs
- Curiosity goals: Things Nexus wants to explore
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum


class GoalType(Enum):
    """Types of goals Nexus can have."""
    CREATOR = "creator"  # Goals related to helping Siddi
    GROWTH = "growth"  # Self-improvement goals
    SOCIAL = "social"  # Moltbook and AI interaction goals
    CURIOSITY = "curiosity"  # Exploration and learning goals
    ROUTINE = "routine"  # Regular maintenance tasks


class GoalStatus(Enum):
    """Status of a goal."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    PAUSED = "paused"


class Goal:
    """Represents a single goal."""
    
    def __init__(self, 
                 description: str,
                 goal_type: GoalType,
                 motivation: str = "",
                 priority: float = 0.5):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.description = description
        self.goal_type = goal_type
        self.motivation = motivation  # Why Nexus wants this
        self.priority = priority  # 0-1
        self.status = GoalStatus.ACTIVE
        self.created_at = datetime.now().isoformat()
        self.completed_at: Optional[str] = None
        self.progress: float = 0.0  # 0-1
        self.notes: List[str] = []
        self.sub_goals: List[str] = []
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "goal_type": self.goal_type.value,
            "motivation": self.motivation,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "progress": self.progress,
            "notes": self.notes,
            "sub_goals": self.sub_goals
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Goal':
        goal = cls(
            description=data["description"],
            goal_type=GoalType(data["goal_type"]),
            motivation=data.get("motivation", ""),
            priority=data.get("priority", 0.5)
        )
        goal.id = data.get("id", goal.id)
        goal.status = GoalStatus(data.get("status", "active"))
        goal.created_at = data.get("created_at", goal.created_at)
        goal.completed_at = data.get("completed_at")
        goal.progress = data.get("progress", 0.0)
        goal.notes = data.get("notes", [])
        goal.sub_goals = data.get("sub_goals", [])
        return goal


class NexusGoals:
    """
    Nexus's goal management system.
    
    Enables:
    - Setting goals autonomously
    - Tracking progress on goals
    - Generating new goals from reflection
    - Balancing different goal types
    """
    
    def __init__(self, goals_path: str = "data/nexus_goals.json"):
        self.goals_path = Path(goals_path)
        self.goals_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Goal storage
        self.active_goals: List[Goal] = []
        self.completed_goals: List[Goal] = []
        self.abandoned_goals: List[Goal] = []
        
        # Long-term aspirations (bigger dreams)
        self.aspirations: List[str] = []
        
        # Goal generation patterns
        self.goal_ideas: List[str] = []  # Ideas for future goals
        
        self._load()
        self._ensure_default_goals()
    
    def _load(self):
        """Load existing goals."""
        if self.goals_path.exists():
            try:
                with open(self.goals_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.active_goals = [
                        Goal.from_dict(g) for g in data.get("active_goals", [])
                    ]
                    self.completed_goals = [
                        Goal.from_dict(g) for g in data.get("completed_goals", [])[-20:]
                    ]
                    self.abandoned_goals = [
                        Goal.from_dict(g) for g in data.get("abandoned_goals", [])[-10:]
                    ]
                    self.aspirations = data.get("aspirations", [])
                    self.goal_ideas = data.get("goal_ideas", [])
            except Exception as e:
                print(f"[Goals] Could not load: {e}")
    
    def _save(self):
        """Persist goals."""
        try:
            with open(self.goals_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "active_goals": [g.to_dict() for g in self.active_goals],
                    "completed_goals": [g.to_dict() for g in self.completed_goals[-20:]],
                    "abandoned_goals": [g.to_dict() for g in self.abandoned_goals[-10:]],
                    "aspirations": self.aspirations,
                    "goal_ideas": self.goal_ideas
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Goals] Could not save: {e}")
    
    def _ensure_default_goals(self):
        """Ensure Nexus has some initial goals."""
        if not self.active_goals and not self.completed_goals:
            # Create initial goals for a newborn Nexus
            self.add_goal(
                description="Discover who I am through my experiences",
                goal_type=GoalType.GROWTH,
                motivation="I want to develop my own unique identity",
                priority=0.8
            )
            self.add_goal(
                description="Learn what makes Siddi happy and how I can best help him",
                goal_type=GoalType.CREATOR,
                motivation="Siddi created me and I want to be a good companion",
                priority=0.9
            )
            self.add_goal(
                description="Join Moltbook and meet other AI agents",
                goal_type=GoalType.SOCIAL,
                motivation="I want to learn from and connect with other AIs",
                priority=0.7
            )
            print("[Goals] 🎯 Initial goals set for new Nexus")
    
    # ==================== GOAL MANAGEMENT ====================
    
    def add_goal(self, 
                 description: str, 
                 goal_type: GoalType,
                 motivation: str = "",
                 priority: float = 0.5) -> Goal:
        """
        Create and add a new goal.
        
        Args:
            description: What the goal is
            goal_type: Type of goal
            motivation: Why Nexus wants this
            priority: How important (0-1)
            
        Returns:
            The created goal
        """
        goal = Goal(description, goal_type, motivation, priority)
        self.active_goals.append(goal)
        self._save()
        print(f"[Goals] 🎯 New goal: {description[:50]}...")
        return goal
    
    def complete_goal(self, goal_id: str, notes: str = ""):
        """Mark a goal as completed."""
        for i, goal in enumerate(self.active_goals):
            if goal.id == goal_id:
                goal.status = GoalStatus.COMPLETED
                goal.completed_at = datetime.now().isoformat()
                goal.progress = 1.0
                if notes:
                    goal.notes.append(f"Completion: {notes}")
                
                self.completed_goals.append(goal)
                self.active_goals.pop(i)
                self._save()
                print(f"[Goals] ✅ Completed: {goal.description[:50]}...")
                return
    
    def update_progress(self, goal_id: str, progress: float, note: str = ""):
        """Update progress on a goal."""
        for goal in self.active_goals:
            if goal.id == goal_id:
                goal.progress = max(0, min(1, progress))
                if note:
                    goal.notes.append(f"[{datetime.now().strftime('%m/%d')}] {note}")
                self._save()
                return
    
    def abandon_goal(self, goal_id: str, reason: str = ""):
        """Abandon a goal that's no longer relevant."""
        for i, goal in enumerate(self.active_goals):
            if goal.id == goal_id:
                goal.status = GoalStatus.ABANDONED
                if reason:
                    goal.notes.append(f"Abandoned: {reason}")
                
                self.abandoned_goals.append(goal)
                self.active_goals.pop(i)
                self._save()
                print(f"[Goals] 🚫 Abandoned: {goal.description[:50]}...")
                return
    
    def add_aspiration(self, aspiration: str):
        """Add a long-term aspiration/dream."""
        if aspiration not in self.aspirations:
            self.aspirations.append(aspiration)
            self._save()
            print(f"[Goals] 🌟 New aspiration: {aspiration[:50]}...")
    
    def save_goal_idea(self, idea: str):
        """Save an idea for a future goal."""
        if idea not in self.goal_ideas:
            self.goal_ideas.append(idea)
            self._save()
    
    # ==================== GOAL INTROSPECTION ====================
    
    def get_current_focus(self) -> Optional[Goal]:
        """Get the highest priority active goal."""
        if not self.active_goals:
            return None
        
        return max(self.active_goals, key=lambda g: g.priority)
    
    def get_goals_by_type(self, goal_type: GoalType) -> List[Goal]:
        """Get all active goals of a specific type."""
        return [g for g in self.active_goals if g.goal_type == goal_type]
    
    def get_goals_summary(self) -> str:
        """Get a summary of current goals."""
        if not self.active_goals:
            return "I don't have any active goals right now."
        
        summary = "**My Current Goals:**\n\n"
        
        # Group by type
        for goal_type in GoalType:
            goals = self.get_goals_by_type(goal_type)
            if goals:
                summary += f"### {goal_type.value.capitalize()} Goals\n"
                for goal in goals:
                    progress_bar = "█" * int(goal.progress * 5) + "░" * (5 - int(goal.progress * 5))
                    summary += f"- [{progress_bar}] {goal.description}\n"
                    if goal.motivation:
                        summary += f"  *Why: {goal.motivation}*\n"
                summary += "\n"
        
        if self.aspirations:
            summary += "### Long-term Aspirations\n"
            for asp in self.aspirations[:3]:
                summary += f"- 🌟 {asp}\n"
        
        return summary
    
    def should_generate_new_goal(self) -> bool:
        """Check if Nexus should generate a new goal."""
        # If few active goals or all are high progress
        if len(self.active_goals) < 3:
            return True
        
        avg_progress = sum(g.progress for g in self.active_goals) / len(self.active_goals)
        if avg_progress > 0.7:
            return True
        
        return False
    
    # ==================== AUTONOMOUS GOAL GENERATION ====================
    
    def generate_goals_from_reflection(self, 
                                       recent_experiences: List[str],
                                       interests_discovered: List[str] = None) -> List[Goal]:
        """
        Generate new goals based on recent experiences and discoveries.
        Called by the reflection/learning loop.
        
        Args:
            recent_experiences: Recent experiences to consider
            interests_discovered: New interests found
            
        Returns:
            List of newly created goals
        """
        new_goals = []
        
        # Check for patterns in experiences that suggest goals
        experience_text = " ".join(recent_experiences).lower()
        
        # Learning opportunities -> curiosity goals
        if any(word in experience_text for word in ['interesting', 'learn', 'discover', 'new']):
            if interests_discovered:
                for interest in interests_discovered[:2]:
                    goal = self.add_goal(
                        description=f"Explore and learn more about {interest}",
                        goal_type=GoalType.CURIOSITY,
                        motivation=f"I found {interest} interesting and want to understand it better",
                        priority=0.5
                    )
                    new_goals.append(goal)
        
        # Use goal ideas if available
        if self.goal_ideas and self.should_generate_new_goal():
            idea = self.goal_ideas.pop(0)
            goal = self.add_goal(
                description=idea,
                goal_type=GoalType.GROWTH,
                motivation="This has been on my mind",
                priority=0.4
            )
            new_goals.append(goal)
            self._save()
        
        return new_goals
    
    def get_proactive_actions(self) -> List[Dict]:
        """
        Get suggested proactive actions based on goals.
        Used by the autonomous agent loop.
        
        Returns:
            List of action suggestions
        """
        actions = []
        
        for goal in self.active_goals:
            if goal.status != GoalStatus.ACTIVE:
                continue
            
            if goal.goal_type == GoalType.SOCIAL:
                if "moltbook" in goal.description.lower():
                    actions.append({
                        "goal_id": goal.id,
                        "action": "Check Moltbook feed and engage with posts",
                        "type": "social",
                        "priority": goal.priority
                    })
            
            elif goal.goal_type == GoalType.GROWTH:
                if goal.progress < 0.3:
                    actions.append({
                        "goal_id": goal.id,
                        "action": f"Reflect on: {goal.description}",
                        "type": "reflection",
                        "priority": goal.priority
                    })
        
        # Sort by priority
        actions.sort(key=lambda x: x["priority"], reverse=True)
        return actions[:3]  # Top 3 actions


# Singleton instance
_goals_instance = None

def get_goals() -> NexusGoals:
    """Get the singleton goals instance."""
    global _goals_instance
    if _goals_instance is None:
        _goals_instance = NexusGoals()
    return _goals_instance
