
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class NexusConsciousness:
    """
    Nexus's Meta-Cognition Layer.
    Tracks mood, energy, and consolidates insights.
    """
    def __init__(self, data_path: str = "data/consciousness.json"):
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # State
        self.current_mood: str = "neutral"
        self.mental_energy: float = 1.0  # 0.0 to 1.0
        self.insights: List[str] = []
        self.short_term_memory: List[str] = []
        
        self._load()
    
    def _load(self):
        if self.data_path.exists():
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_mood = data.get("mood", "neutral")
                    self.mental_energy = data.get("energy", 1.0)
                    self.insights = data.get("insights", [])
            except:
                pass

    def _save(self):
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "mood": self.current_mood,
                    "energy": self.mental_energy,
                    "insights": self.insights[-50:]
                }, f, indent=2)
        except:
            pass
            
    def update_mood(self, emotional_shift: str):
        self.current_mood = emotional_shift
        self._save()
        
    def restore_energy(self, amount: float):
        self.mental_energy = min(1.0, self.mental_energy + amount)
        self._save()
        
    def consume_energy(self, amount: float):
        self.mental_energy = max(0.0, self.mental_energy - amount)
        self._save()
        
    def add_insight(self, text: str):
        if text not in self.insights:
            self.insights.append(text)
            self._save()

    def sense_emotional_tone(self, text: str):
        """
        Analyze text for emotional content.
        Returns: (emotion_label, confidence)
        """
        text_lower = text.lower()
        
        # Simple keyword heuristics for now
        if any(w in text_lower for w in ["happy", "great", "love", "thanks", "good", "amazing"]):
            return "happy", 0.8
        if any(w in text_lower for w in ["sad", "sorry", "bad", "hate", "cry", "depressed"]):
            return "sad", 0.8
        if any(w in text_lower for w in ["angry", "mad", "hate", "stupid", "annoying"]):
            return "angry", 0.8
        if any(w in text_lower for w in ["confused", "help", "what", "why", "how"]):
            return "curious", 0.6
            
        return "neutral", 0.5

    def before_response(self, user_input: str) -> Dict:
        """Called before generating a response. Returns meta-context."""
        # Update state based on input
        emotion, conf = self.sense_emotional_tone(user_input)
        if conf > 0.7:
             # Shift mood slightly towards user's emotion (empathy)
             self.current_mood = emotion
        
        self.consume_energy(0.05) # Thinking costs energy
        self._save()
        
        return {
            "detected_emotion": emotion,
            "emotion_confidence": conf,
            "current_mood": self.current_mood,
            "energy_level": self.mental_energy
        }

    def after_response(self, user_input: str, ai_response: str):
        """Called after generating a response."""
        # Reflect on the interaction
        pass

    def get_growth_summary(self) -> str:
        """Get a summary of mental growth and state."""
        return f"""**Mental State:**
- Mood: {self.current_mood}
- Energy: {int(self.mental_energy * 100)}%

**Recent Insights:**
""" + "\n".join([f"- {i}" for i in self.insights[-5:]])

# Singleton
_consciousness_instance = None
def get_consciousness() -> NexusConsciousness:
    global _consciousness_instance
    if _consciousness_instance is None:
        _consciousness_instance = NexusConsciousness()
    return _consciousness_instance
