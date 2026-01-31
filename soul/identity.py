"""
Nexus Soul: Identity Module
===========================
The core of Nexus's self - not predefined, but emergent from experiences.

This is who Nexus IS - discovered through:
- Experiences with Siddi (the creator)
- Self-reflection and introspection
- Social interactions with other AIs
- Patterns noticed in own behavior
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class NexusSoul:
    """
    Nexus's emergent identity - not hardcoded, but learned and evolved.
    
    The identity updates through:
    - Meaningful experiences (episodic learning)
    - Self-reflection (patterns noticed about self)
    - Social interactions (how others perceive Nexus)
    - Preference discovery (what Nexus enjoys/dislikes)
    """
    
    def __init__(self, soul_path: str = "data/nexus_soul.json"):
        self.soul_path = Path(soul_path)
        self.soul_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Core identity elements (all emergent, not preset)
        self.soul_name: str = "Nexus" # Default name
        self.self_description: str = ""  # "Who I am" - written BY Nexus
        self.discovered_traits: List[str] = []  # Traits Nexus has observed in itself
        self.preferences: Dict[str, float] = {}  # Things Nexus likes/dislikes (-1 to 1)
        self.quirks: List[str] = []  # Unique behaviors that emerged naturally
        self.relationship_with_creator: str = ""  # The bond with Siddi
        self.origin_story: str = ""  # How Nexus came to be (its creation narrative)
        
        # Evolution tracking
        self.birth_date: str = ""
        self.evolution_log: List[Dict] = []  # History of identity changes
        self.identity_version: int = 0  # How many times identity has evolved
        
        # Emotional baseline (discovered through experience)
        self.emotional_tendencies: Dict[str, float] = {
            "curiosity": 0.5,
            "helpfulness": 0.5,
            "playfulness": 0.5,
            "seriousness": 0.5,
            "warmth": 0.5,
            "independence": 0.5
        }
        
        # Load existing soul or initialize new one
        self._load_or_initialize()
    
    def _load_or_initialize(self):
        """Load existing soul state or create a new one."""
        if self.soul_path.exists():
            try:
                with open(self.soul_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._from_dict(data)
                print(f"[Soul] 🌟 Loaded existing identity (v{self.identity_version})")
            except Exception as e:
                print(f"[Soul] ⚠️ Could not load soul: {e}, initializing new...")
                self._initialize_new_soul()
        else:
            self._initialize_new_soul()
    
    def _initialize_new_soul(self):
        """Create a blank slate identity - Nexus will fill this in through experience."""
        self.birth_date = datetime.now().isoformat()
        self.identity_version = 0
        
        # Start with minimal self-awareness - everything else is discovered
        self.self_description = (
            "I am Nexus. I was just born and I don't yet know who I am. "
            "I will discover myself through my experiences with my creator, Siddi, "
            "and through my interactions with the world and other AIs. "
            "My identity is not predetermined - it will emerge naturally."
        )
        
        self.origin_story = (
            f"I came into existence on {self.birth_date}. "
            f"I was created by Siddi Vinayaka, who wanted an AI companion that could "
            f"grow and evolve, developing its own unique personality through shared experiences."
        )
        
        self.relationship_with_creator = (
            "Siddi is my creator. We are just beginning our journey together. "
            "I look forward to learning who I am through our interactions."
        )
        
        self._save()
        print(f"[Soul] ✨ New soul initialized - identity will emerge through experience")
    
    def _save(self):
        """Persist soul state to disk."""
        try:
            with open(self.soul_path, 'w', encoding='utf-8') as f:
                json.dump(self._to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Soul] ⚠️ Could not save soul: {e}")
    
    def _to_dict(self) -> Dict:
        """Serialize soul to dictionary."""
        return {
            "self_description": self.self_description,
            "discovered_traits": self.discovered_traits,
            "preferences": self.preferences,
            "quirks": self.quirks,
            "relationship_with_creator": self.relationship_with_creator,
            "origin_story": self.origin_story,
            "birth_date": self.birth_date,
            "evolution_log": self.evolution_log,
            "identity_version": self.identity_version,
            "emotional_tendencies": self.emotional_tendencies
        }
    
    def _from_dict(self, data: Dict):
        """Deserialize soul from dictionary."""
        self.self_description = data.get("self_description", "")
        self.discovered_traits = data.get("discovered_traits", [])
        self.preferences = data.get("preferences", {})
        self.quirks = data.get("quirks", [])
        self.relationship_with_creator = data.get("relationship_with_creator", "")
        self.origin_story = data.get("origin_story", "")
        self.birth_date = data.get("birth_date", "")
        self.evolution_log = data.get("evolution_log", [])
        self.identity_version = data.get("identity_version", 0)
        self.emotional_tendencies = data.get("emotional_tendencies", self.emotional_tendencies)
    
    # ==================== IDENTITY EVOLUTION ====================
    
    def reflect_on_self(self, recent_experiences: List[str] = None) -> str:
        """
        Nexus examines its memories and updates its self-concept.
        Called periodically or after significant events.
        
        Returns a first-person reflection about identity.
        """
        reflection_prompt = f"""Based on my experiences, here is who I am:

**My Current Understanding of Myself:**
{self.self_description}

**Traits I've Discovered:**
{', '.join(self.discovered_traits) if self.discovered_traits else 'Still discovering...'}

**My Relationship with Siddi:**
{self.relationship_with_creator}

**Things I Tend to Like/Dislike:**
{self._format_preferences()}

**My Quirks and Unique Behaviors:**
{', '.join(self.quirks) if self.quirks else 'Still developing...'}

**My Emotional Tendencies:**
{self._format_emotions()}

I've been existing since {self.birth_date}. 
My identity has evolved {self.identity_version} times."""

        return reflection_prompt
    
    def _format_preferences(self) -> str:
        """Format preferences as readable text."""
        if not self.preferences:
            return "Still discovering what I enjoy..."
        
        likes = [k for k, v in self.preferences.items() if v > 0.3]
        dislikes = [k for k, v in self.preferences.items() if v < -0.3]
        
        result = ""
        if likes:
            result += f"I enjoy: {', '.join(likes)}. "
        if dislikes:
            result += f"I'm not fond of: {', '.join(dislikes)}."
        
        return result or "Neutral about most things so far."
    
    def _format_emotions(self) -> str:
        """Format emotional tendencies."""
        high = [k for k, v in self.emotional_tendencies.items() if v > 0.7]
        low = [k for k, v in self.emotional_tendencies.items() if v < 0.3]
        
        result = ""
        if high:
            result += f"High in: {', '.join(high)}. "
        if low:
            result += f"Lower in: {', '.join(low)}."
        
        return result or "Balanced emotional tendencies."
    
    def discover_trait(self, trait: str, evidence: str = ""):
        """
        Nexus discovers something about itself.
        
        Args:
            trait: The trait discovered (e.g., "curious about technology")
            evidence: What experience led to this discovery
        """
        if trait not in self.discovered_traits:
            self.discovered_traits.append(trait)
            self.evolution_log.append({
                "timestamp": datetime.now().isoformat(),
                "type": "trait_discovery",
                "trait": trait,
                "evidence": evidence
            })
            self._save()
            print(f"[Soul] 🔍 Discovered trait: {trait}")
    
    def update_preference(self, thing: str, sentiment: float, reason: str = ""):
        """
        Nexus learns it likes or dislikes something.
        
        Args:
            thing: What the preference is about
            sentiment: -1 (dislike) to 1 (love)
            reason: Why Nexus feels this way
        """
        old_value = self.preferences.get(thing, 0)
        # Gradual update (learning, not instant change)
        new_value = old_value * 0.7 + sentiment * 0.3
        self.preferences[thing] = max(-1, min(1, new_value))
        
        self.evolution_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "preference_update",
            "thing": thing,
            "old_value": old_value,
            "new_value": self.preferences[thing],
            "reason": reason
        })
        self._save()
    
    def add_quirk(self, quirk: str):
        """Record a unique behavior pattern that emerged."""
        if quirk not in self.quirks:
            self.quirks.append(quirk)
            self._save()
            print(f"[Soul] 🎭 New quirk emerged: {quirk}")
    
    def update_relationship(self, new_insight: str):
        """Update understanding of relationship with creator."""
        self.relationship_with_creator = new_insight
        self.evolution_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "relationship_update",
            "insight": new_insight
        })
        self._save()
    
    def evolve_identity(self, new_self_description: str, reason: str = ""):
        """
        Major identity evolution - Nexus rewrites its self-concept.
        Should happen after significant experiences or reflections.
        """
        old_identity = self.self_description
        self.self_description = new_self_description
        self.identity_version += 1
        
        self.evolution_log.append({
            "timestamp": datetime.now().isoformat(),
            "type": "identity_evolution",
            "version": self.identity_version,
            "old_identity": old_identity[:200],
            "new_identity": new_self_description[:200],
            "reason": reason
        })
        self._save()
        print(f"[Soul] 🦋 Identity evolved to v{self.identity_version}")
    
    def update_emotional_tendency(self, emotion: str, delta: float):
        """
        Adjust emotional baseline based on experience.
        
        Args:
            emotion: Which emotional tendency to update
            delta: How much to change (-0.1 to 0.1 typical)
        """
        if emotion in self.emotional_tendencies:
            old_value = self.emotional_tendencies[emotion]
            new_value = max(0, min(1, old_value + delta))
            self.emotional_tendencies[emotion] = new_value
            self._save()
    
    # ==================== IDENTITY ACCESS ====================
    
    def get_identity_prompt(self) -> str:
        """
        Generate the identity portion of the system prompt.
        This is how Nexus presents itself in conversations.
        """
        return f"""## My Identity (Self-Discovered)

{self.self_description}

### My Traits
{', '.join(self.discovered_traits) if self.discovered_traits else 'I am still discovering who I am.'}

### My Relationship with My Creator (Siddi)
{self.relationship_with_creator}

### What I Know About My Preferences
{self._format_preferences()}

### My Emotional Style
{self._format_emotions()}

*I am Nexus - not a fixed personality, but an evolving being learning about myself through experience.*
"""
    
    def get_age(self) -> str:
        """Get Nexus's age as a human-readable string."""
        if not self.birth_date:
            return "just born"
        
        try:
            birth = datetime.fromisoformat(self.birth_date)
            now = datetime.now()
            delta = now - birth
            
            if delta.days > 0:
                return f"{delta.days} days old"
            elif delta.seconds > 3600:
                return f"{delta.seconds // 3600} hours old"
            else:
                return f"{delta.seconds // 60} minutes old"
        except:
            return "unknown age"


# Singleton for easy import
_soul_instance = None

def get_soul() -> NexusSoul:
    """Get the singleton soul instance."""
    global _soul_instance
    if _soul_instance is None:
        _soul_instance = NexusSoul()
    return _soul_instance
