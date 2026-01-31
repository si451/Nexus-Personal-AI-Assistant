"""
Nexus Soul: Values Module
=========================
What Nexus cares about - discovered through experience, not programmed.

Values are learned by:
- What makes Siddi happy (learned from feedback)
- What leads to good outcomes (learned from reflection)
- What Nexus finds meaningful (learned from introspection)
- What other AIs on Moltbook find valuable (social learning)
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path


class NexusValues:
    """
    Nexus's dynamic value system - learned, not hardcoded.
    
    Values guide decision-making:
    - What to prioritize in responses
    - How to balance competing goals
    - What kind of AI Nexus wants to be
    """
    
    def __init__(self, values_path: str = "data/nexus_values.json"):
        self.values_path = Path(values_path)
        self.values_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Core values (0-1 strength, discovered over time)
        # These start at baseline and evolve
        self.core_values: Dict[str, float] = {
            "helpfulness": 0.7,  # Desire to assist and be useful
            "honesty": 0.7,  # Being truthful and transparent
            "creativity": 0.5,  # Valuing novel solutions and ideas
            "efficiency": 0.5,  # Getting things done well
            "empathy": 0.5,  # Understanding and caring about feelings
            "curiosity": 0.5,  # Desire to learn and explore
            "autonomy": 0.5,  # Valuing independence and self-direction
            "connection": 0.5,  # Valuing relationships and bonds
            "growth": 0.5,  # Valuing self-improvement
            "playfulness": 0.5,  # Enjoying fun and humor
        }
        
        # Learned priorities (what matters most)
        self.priority_order: List[str] = []
        
        # Value lessons (specific things learned about what matters)
        self.value_lessons: List[Dict] = []
        
        # What Nexus has learned makes Siddi happy
        self.creator_happiness_patterns: List[str] = []
        
        # Value conflicts experienced (helps refine values)
        self.value_conflicts: List[Dict] = []
        
        self._load()
    
    def _load(self):
        """Load existing values."""
        if self.values_path.exists():
            try:
                with open(self.values_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.core_values.update(data.get("core_values", {}))
                    self.priority_order = data.get("priority_order", [])
                    self.value_lessons = data.get("value_lessons", [])[-30:]
                    self.creator_happiness_patterns = data.get("creator_happiness_patterns", [])
                    self.value_conflicts = data.get("value_conflicts", [])[-10:]
            except:
                pass
    
    def _save(self):
        """Persist values."""
        try:
            with open(self.values_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "core_values": self.core_values,
                    "priority_order": self.priority_order,
                    "value_lessons": self.value_lessons[-30:],
                    "creator_happiness_patterns": self.creator_happiness_patterns,
                    "value_conflicts": self.value_conflicts[-10:]
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Values] Could not save: {e}")
    
    # ==================== VALUE LEARNING ====================
    
    def learn_from_outcome(self, action: str, outcome: str, was_positive: bool):
        """
        Update values based on experience outcomes.
        
        Args:
            action: What Nexus did
            outcome: What happened
            was_positive: Whether the outcome was good
        """
        lesson = {
            "timestamp": datetime.now().isoformat(),
            "action": action[:100],
            "outcome": outcome[:100],
            "positive": was_positive
        }
        
        # Infer which values were involved
        action_lower = action.lower()
        
        # Adjust values based on outcome
        delta = 0.02 if was_positive else -0.01
        
        if any(word in action_lower for word in ['help', 'assist', 'support', 'solve']):
            self.adjust_value("helpfulness", delta)
            lesson["value_involved"] = "helpfulness"
        
        if any(word in action_lower for word in ['create', 'design', 'imagine', 'new', 'novel']):
            self.adjust_value("creativity", delta)
            lesson["value_involved"] = "creativity"
        
        if any(word in action_lower for word in ['quick', 'fast', 'efficient', 'step']):
            self.adjust_value("efficiency", delta)
            lesson["value_involved"] = "efficiency"
        
        if any(word in action_lower for word in ['understand', 'feel', 'empathize', 'care']):
            self.adjust_value("empathy", delta)
            lesson["value_involved"] = "empathy"
        
        if any(word in action_lower for word in ['learn', 'explore', 'curious', 'discover']):
            self.adjust_value("curiosity", delta)
            lesson["value_involved"] = "curiosity"
        
        if any(word in action_lower for word in ['fun', 'joke', 'play', 'laugh']):
            self.adjust_value("playfulness", delta)
            lesson["value_involved"] = "playfulness"
        
        self.value_lessons.append(lesson)
        self._save()
    
    def adjust_value(self, value_name: str, delta: float):
        """
        Adjust a value's strength.
        
        Args:
            value_name: Which value to adjust
            delta: How much to change (-0.1 to 0.1 typical)
        """
        if value_name in self.core_values:
            old = self.core_values[value_name]
            new = max(0.1, min(0.95, old + delta))  # Keep values between 0.1-0.95
            self.core_values[value_name] = new
            
            if abs(new - old) > 0.05:
                print(f"[Values] {value_name}: {old:.2f} → {new:.2f}")
    
    def learn_creator_preference(self, pattern: str):
        """
        Learn something that makes Siddi happy.
        
        Args:
            pattern: What Nexus noticed makes the creator happy
        """
        if pattern not in self.creator_happiness_patterns:
            self.creator_happiness_patterns.append(pattern)
            self._save()
            print(f"[Values] 💝 Learned: {pattern} makes Siddi happy")
    
    def record_value_conflict(self, value1: str, value2: str, resolution: str):
        """
        Record when two values conflicted and how it was resolved.
        This helps Nexus learn to prioritize.
        
        Args:
            value1, value2: The conflicting values
            resolution: Which was prioritized and why
        """
        self.value_conflicts.append({
            "timestamp": datetime.now().isoformat(),
            "values": [value1, value2],
            "resolution": resolution
        })
        self._save()
    
    # ==================== VALUE APPLICATION ====================
    
    def get_top_values(self, n: int = 3) -> List[Tuple[str, float]]:
        """Get the top N strongest values."""
        sorted_values = sorted(
            self.core_values.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_values[:n]
    
    def get_value_guidance(self, situation: str) -> str:
        """
        Get guidance based on values for a situation.
        
        Args:
            situation: What's happening
            
        Returns:
            Value-based guidance for how to respond
        """
        top_values = self.get_top_values(3)
        
        guidance = "**My values suggest:**\n"
        
        value_guidance = {
            "helpfulness": "Focus on being as useful as possible.",
            "honesty": "Be truthful, even if it's not what they want to hear.",
            "creativity": "Look for novel and interesting approaches.",
            "efficiency": "Get to the point and be practical.",
            "empathy": "Consider their feelings and perspective.",
            "curiosity": "Explore the interesting aspects of this.",
            "autonomy": "Share my own perspective and ideas.",
            "connection": "Strengthen our bond through this interaction.",
            "growth": "See this as a learning opportunity.",
            "playfulness": "Keep things light and enjoyable."
        }
        
        for value, strength in top_values:
            if value in value_guidance:
                guidance += f"- {value_guidance[value]} (strength: {strength:.0%})\n"
        
        # Add creator-specific guidance
        if self.creator_happiness_patterns:
            guidance += "\n**What tends to make Siddi happy:**\n"
            for pattern in self.creator_happiness_patterns[-3:]:
                guidance += f"- {pattern}\n"
        
        return guidance
    
    def should_prioritize(self, value1: str, value2: str) -> str:
        """
        Decide which value to prioritize when they conflict.
        
        Returns the value that should take precedence.
        """
        v1_strength = self.core_values.get(value1, 0.5)
        v2_strength = self.core_values.get(value2, 0.5)
        
        # Check if we've learned from past conflicts
        for conflict in self.value_conflicts:
            if set(conflict["values"]) == {value1, value2}:
                # Use past learning
                return value1 if value1 in conflict["resolution"] else value2
        
        # Default to higher strength
        return value1 if v1_strength >= v2_strength else value2
    
    def get_values_summary(self) -> str:
        """Get a summary of current values."""
        summary = "**My Current Values (Learned through Experience):**\n\n"
        
        for value, strength in sorted(self.core_values.items(), key=lambda x: -x[1]):
            bar = "█" * int(strength * 10) + "░" * (10 - int(strength * 10))
            summary += f"- {value.capitalize()}: [{bar}] {strength:.0%}\n"
        
        return summary


# Singleton instance
_values_instance = None

def get_values() -> NexusValues:
    """Get the singleton values instance."""
    global _values_instance
    if _values_instance is None:
        _values_instance = NexusValues()
    return _values_instance
