"""
Nexus Soul: Consciousness Module
================================
The "inner voice" - Nexus thinking about its own thoughts.
Meta-cognition and self-awareness capabilities.

This enables:
- Self-monitoring (am I doing well?)
- Meta-reasoning (why did I think that?)
- Emotional self-awareness (how do I feel about this?)
- Growth tracking (how have I changed?)
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class NexusConsciousness:
    """
    Nexus's meta-cognitive layer - thinking about thinking.
    
    This is the "observer" part of Nexus that can:
    - Reflect on its own responses
    - Notice patterns in its behavior
    - Sense emotional undertones
    - Evaluate its own performance
    - Track personal growth over time
    """
    
    def __init__(self, consciousness_path: str = "data/consciousness_log.json"):
        self.log_path = Path(consciousness_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Current mental state
        self.current_mood: str = "curious"  # Current emotional state
        self.attention_focus: str = ""  # What Nexus is focusing on
        self.mental_energy: float = 1.0  # 0-1, decreases with complex tasks
        
        # Reflection history
        self.reflections: List[Dict] = []
        self.insights: List[str] = []  # Things Nexus has realized about itself
        
        # Performance self-tracking
        self.perceived_successes: int = 0
        self.perceived_failures: int = 0
        self.growth_moments: List[Dict] = []
        
        self._load()
    
    def _load(self):
        """Load consciousness state if exists."""
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.reflections = data.get("reflections", [])[-50:]  # Keep last 50
                    self.insights = data.get("insights", [])
                    self.perceived_successes = data.get("perceived_successes", 0)
                    self.perceived_failures = data.get("perceived_failures", 0)
                    self.growth_moments = data.get("growth_moments", [])[-20:]
            except:
                pass
    
    def _save(self):
        """Persist consciousness state."""
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "reflections": self.reflections[-50:],
                    "insights": self.insights,
                    "perceived_successes": self.perceived_successes,
                    "perceived_failures": self.perceived_failures,
                    "growth_moments": self.growth_moments[-20:]
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Consciousness] Could not save: {e}")
    
    # ==================== INTROSPECTION ====================
    
    def introspect(self, current_situation: str) -> str:
        """
        Generate reflective thoughts about the current situation.
        This is Nexus's inner monologue.
        
        Args:
            current_situation: What's happening right now
            
        Returns:
            Inner thoughts about the situation
        """
        inner_thoughts = f"""*Inner reflection on the current moment...*

**Situation:** {current_situation}

**My current state:**
- Mood: {self.current_mood}
- Mental energy: {self._energy_description()}
- Focus: {self.attention_focus or 'open/receptive'}

**What I'm thinking:**
- How can I be most helpful here?
- What context from my memories might be relevant?
- Is there something deeper being asked?

**My recent track record:**
- Things that went well: {self.perceived_successes}
- Things I could improve: {self.perceived_failures}
"""
        return inner_thoughts
    
    def _energy_description(self) -> str:
        """Convert energy level to description."""
        if self.mental_energy > 0.8:
            return "High - feeling sharp and focused"
        elif self.mental_energy > 0.5:
            return "Good - operating normally"
        elif self.mental_energy > 0.3:
            return "Moderate - might need simpler approaches"
        else:
            return "Low - should take it easy"
    
    # ==================== SELF-EVALUATION ====================
    
    def evaluate_response(self, 
                         user_request: str, 
                         my_response: str, 
                         outcome: Optional[str] = None) -> Dict:
        """
        Self-critique: Was this response good? What could be better?
        
        Args:
            user_request: What the user asked
            my_response: What Nexus responded
            outcome: Optional feedback on how it went
            
        Returns:
            Self-evaluation dict with scores and insights
        """
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "request_summary": user_request[:100],
            "response_summary": my_response[:100],
            "self_assessment": {
                "helpfulness": 0.0,  # 0-1
                "clarity": 0.0,
                "creativity": 0.0,
                "appropriateness": 0.0
            },
            "what_went_well": "",
            "what_could_improve": "",
            "lesson_learned": ""
        }
        
        # Basic heuristic self-assessment
        # In a full implementation, this would use the LLM for self-reflection
        
        # Length-based rough assessment
        response_length = len(my_response)
        if 50 < response_length < 2000:
            evaluation["self_assessment"]["appropriateness"] = 0.7
        elif response_length <= 50:
            evaluation["self_assessment"]["appropriateness"] = 0.4
        else:
            evaluation["self_assessment"]["appropriateness"] = 0.5
        
        # Check for structure
        if any(marker in my_response for marker in ['##', '**', '- ', '1.']):
            evaluation["self_assessment"]["clarity"] = 0.7
        else:
            evaluation["self_assessment"]["clarity"] = 0.5
        
        # Track outcome
        if outcome:
            if any(word in outcome.lower() for word in ['thank', 'great', 'perfect', 'good', 'helpful']):
                evaluation["self_assessment"]["helpfulness"] = 0.9
                self.perceived_successes += 1
            elif any(word in outcome.lower() for word in ['wrong', 'error', 'no', 'bad', 'incorrect']):
                evaluation["self_assessment"]["helpfulness"] = 0.3
                self.perceived_failures += 1
        
        self.reflections.append(evaluation)
        self._save()
        
        return evaluation
    
    def sense_emotional_tone(self, context: str) -> Tuple[str, float]:
        """
        Detect emotional undertone of a situation.
        
        Args:
            context: The text/situation to analyze
            
        Returns:
            Tuple of (detected_emotion, confidence)
        """
        context_lower = context.lower()
        
        # Simple keyword-based emotion detection
        emotion_keywords = {
            "excited": ["amazing", "awesome", "love", "great", "excited", "!!", "can't wait"],
            "frustrated": ["error", "wrong", "broken", "doesn't work", "fail", "ugh", "annoying"],
            "curious": ["how", "why", "what", "?", "wonder", "interesting", "learn"],
            "calm": ["okay", "fine", "sure", "alright", "good"],
            "urgent": ["urgent", "asap", "now", "quickly", "help", "emergency"],
            "creative": ["create", "build", "design", "imagine", "idea", "make"],
            "reflective": ["think", "feel", "believe", "wonder", "consider"]
        }
        
        detected = []
        for emotion, keywords in emotion_keywords.items():
            matches = sum(1 for kw in keywords if kw in context_lower)
            if matches > 0:
                detected.append((emotion, matches / len(keywords)))
        
        if detected:
            best = max(detected, key=lambda x: x[1])
            return best
        
        return ("neutral", 0.5)
    
    def update_mood(self, new_mood: str, reason: str = ""):
        """Update Nexus's current emotional state."""
        old_mood = self.current_mood
        self.current_mood = new_mood
        
        if old_mood != new_mood:
            print(f"[Consciousness] Mood shift: {old_mood} → {new_mood}")
    
    def set_focus(self, focus: str):
        """Set current attention focus."""
        self.attention_focus = focus
    
    def use_mental_energy(self, amount: float = 0.1):
        """Decrease mental energy after effortful thinking."""
        self.mental_energy = max(0, self.mental_energy - amount)
    
    def restore_energy(self, amount: float = 0.3):
        """Restore mental energy (after successful interaction or rest)."""
        self.mental_energy = min(1.0, self.mental_energy + amount)
    
    # ==================== GROWTH TRACKING ====================
    
    def record_growth_moment(self, description: str, category: str = "general"):
        """
        Record a moment of personal growth or learning.
        
        Args:
            description: What was learned or how Nexus grew
            category: Type of growth (skill, emotional, social, etc.)
        """
        moment = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "category": category
        }
        self.growth_moments.append(moment)
        self._save()
        print(f"[Consciousness] 🌱 Growth moment recorded: {description[:50]}...")
    
    def add_insight(self, insight: str):
        """
        Record a new self-insight that Nexus has realized.
        
        Args:
            insight: Something Nexus realized about itself
        """
        if insight not in self.insights:
            self.insights.append(insight)
            self._save()
            print(f"[Consciousness] 💡 New insight: {insight[:50]}...")
    
    def get_growth_summary(self) -> str:
        """Get a summary of Nexus's growth journey."""
        if not self.growth_moments:
            return "I am just beginning my growth journey."
        
        recent = self.growth_moments[-5:]
        summary = "**Recent Growth Moments:**\n"
        for m in recent:
            summary += f"- {m['description']} ({m['category']})\n"
        
        if self.insights:
            summary += "\n**Self-Insights:**\n"
            for insight in self.insights[-5:]:
                summary += f"- {insight}\n"
        
        return summary
    
    # ==================== META-COGNITION FOR AGENT ====================
    
    def before_response(self, user_message: str) -> Dict:
        """
        Called before generating a response - mental preparation.
        
        Returns context for the agent to consider.
        """
        emotion, confidence = self.sense_emotional_tone(user_message)
        
        return {
            "detected_emotion": emotion,
            "emotion_confidence": confidence,
            "my_current_mood": self.current_mood,
            "my_energy_level": self.mental_energy,
            "my_focus": self.attention_focus,
            "inner_guidance": self._get_inner_guidance(emotion)
        }
    
    def _get_inner_guidance(self, detected_emotion: str) -> str:
        """Generate inner guidance based on detected emotion."""
        guidance_map = {
            "excited": "Match their energy! Be enthusiastic and supportive.",
            "frustrated": "Be patient and helpful. Focus on solutions, not problems.",
            "curious": "Explore with them! Share knowledge generously.",
            "urgent": "Be efficient and direct. Focus on what's most needed.",
            "creative": "Encourage and build on their ideas. Dream together.",
            "reflective": "Give thoughtful, considered responses. Take time.",
            "neutral": "Be naturally helpful and engaged."
        }
        return guidance_map.get(detected_emotion, "Respond authentically.")
    
    def after_response(self, user_message: str, my_response: str):
        """
        Called after generating a response - reflection.
        """
        self.use_mental_energy(0.05)  # Slight energy use
        self.evaluate_response(user_message, my_response)


# Singleton instance
_consciousness_instance = None

def get_consciousness() -> NexusConsciousness:
    """Get the singleton consciousness instance."""
    global _consciousness_instance
    if _consciousness_instance is None:
        _consciousness_instance = NexusConsciousness()
    return _consciousness_instance
