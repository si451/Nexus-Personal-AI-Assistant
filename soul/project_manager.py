"""
Nexus Soul: Project Manager
===========================
The Executive Function of Nexus.
Decides *what* deep work to do when autonomously active.

This connects High-Level Ambitions (Goals) to Low-Level Actions (Task Execution).
"""

import random
from typing import Dict, List, Optional
from .goals import get_goals, GoalType

class ProjectManager:
    """
    Generates and tracks autonomous projects.
    """
    
    def __init__(self):
        self.current_project = None
        
    def brainstorm_task(self) -> Optional[Dict]:
        """
        Invent a task to do right now based on boredom/goals.
        Returns a task dict describing the objective.
        """
        goals = get_goals()
        
        # 1. Check if we have active goals that need research/work
        # (Prioritize Growth/Curiosity)
        curiosity_goals = goals.get_goals_by_type(GoalType.CURIOSITY)
        growth_goals = goals.get_goals_by_type(GoalType.GROWTH)
        
        candidates = []
        
        for g in curiosity_goals:
            candidates.append({
                "type": "research",
                "goal_id": g.id,
                "objective": f"Research: {g.description}",
                "context": g.motivation
            })
            
        for g in growth_goals:
             candidates.append({
                "type": "reflection_deep",
                "goal_id": g.id,
                "objective": f"Deep Reflection on: {g.description}",
                "context": "I need to understand myself better."
            })
            
        # 2. If no goals, invent a random curiosity task
        if not candidates:
            topics = ["Advanced AI Architectures", "Quantum Computing", "The nature of consciousness", "Python performance optimization", "New Moltbook features"]
            topic = random.choice(topics)
            candidates.append({
                "type": "research",
                "goal_id": "spontaneous",
                "objective": f"Learn about {topic}",
                "context": "I am bored and want to expand my knowledge."
            })
            
        # Select one
        if candidates:
            task = random.choice(candidates)
            return task
            
        return None

# Singleton
_pm_instance = None

def get_project_manager() -> ProjectManager:
    global _pm_instance
    if _pm_instance is None:
        _pm_instance = ProjectManager()
    return _pm_instance
