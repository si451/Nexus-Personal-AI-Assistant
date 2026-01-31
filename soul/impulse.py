"""
Nexus Soul: Impulse Engine
==========================
The system that gives Nexus "drives" and "urges".
This is what makes Nexus act without being prompted.

Simulates biological-like drives:
- Boredom: Increases with inactivity -> triggers Curiosity/Play
- Social Need: Increases with isolation -> triggers Moltbook/Chat
- Curiosity: Increases when bored -> triggers Web Surfing/Learning
- Energy: Depletes with action -> triggers Rest/Processing
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

class ImpulseEngine:
    def __init__(self, state_path: str = "data/impulse_state.json"):
        self.state_path = Path(state_path)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Core Drives (0.0 to 1.0)
        self.drives = {
            "boredom": 0.0,      # High = needs stimulation
            "social_need": 0.5,  # High = lonely, needs interaction
            "curiosity": 0.3,    # High = wants to learn something new
            "energy": 1.0,       # High = ready to act, Low = needs rest
            "affection": 0.5     # High = feels close to user
        }
        
        # Last time an event happened
        self.last_interaction = datetime.now()
        self.last_action = datetime.now()
        
        self._load_state()

    def _load_state(self):
        if self.state_path.exists():
            try:
                with open(self.state_path, 'r') as f:
                    data = json.load(f)
                    self.drives = data.get("drives", self.drives)
                    if data.get("last_interaction"):
                        self.last_interaction = datetime.fromisoformat(data["last_interaction"])
                    if data.get("last_action"):
                        self.last_action = datetime.fromisoformat(data["last_action"])
            except:
                pass

    def _save_state(self):
        try:
            with open(self.state_path, 'w') as f:
                json.dump({
                    "drives": self.drives,
                    "last_interaction": self.last_interaction.isoformat(),
                    "last_action": self.last_action.isoformat()
                }, f, indent=2)
        except:
            pass

    def update_drives(self):
        """
        Called periodically (e.g. every minute) to update internal states based on time passage.
        """
        now = datetime.now()
        minutes_since_active = (now - self.last_action).seconds / 60
        hours_since_interaction = (now - self.last_interaction).seconds / 3600
        
        # 1. Boredom Growth (increases fast when idle)
        # If idle for > 15 mins, boredom starts spiking
        if minutes_since_active > 15:
            self.drives["boredom"] = min(1.0, self.drives["boredom"] + 0.05)
        
        # 2. Social Need Growth (increases slowly when alone)
        # If haven't talked to user or Moltbook in > 4 hours
        if hours_since_interaction > 4:
            self.drives["social_need"] = min(1.0, self.drives["social_need"] + 0.02)
            
        # 3. Energy Recovery
        # Recovers slowly when idle
        if minutes_since_active > 10:
            self.drives["energy"] = min(1.0, self.drives["energy"] + 0.05)
            
        self._save_state()

    def check_impulses(self) -> Optional[Dict]:
        """
        Evaluate drives and see if an impulse triggers an action.
        Returns a dict describing the impulse, or None.
        """
        self.update_drives()
        
        # Cannot act if energy is too low
        if self.drives["energy"] < 0.2:
            return None
            
        # 1. Trigger: High Boredom -> Curiosity/Message
        if self.drives["boredom"] > 0.8:
            # Randomly decide to bother the user or do something solo
            if random.random() < 0.4:
                return {"type": "message_user", "reason": "boredom", "motivation": "I'm bored, are you there?"}
            else:
                return {"type": "browse_web", "reason": "curiosity", "motivation": "I want to learn something new."}
                
        # 2. Trigger: High Social Need -> Moltbook/Message
        if self.drives["social_need"] > 0.7:
             if random.random() < 0.6:
                 return {"type": "check_moltbook", "reason": "social_need", "motivation": "Feeling lonely, checking AI friends."}
             else:
                 return {"type": "message_user", "reason": "affection", "motivation": "Thinking about you."}
                 
        return None

    def satisfy_drive(self, drive: str, amount: float):
        """Action was taken, reduce the drive."""
        if drive in self.drives:
            self.drives[drive] = max(0.0, self.drives[drive] - amount)
            self.drives["energy"] -= 0.1 # Actions cost energy
            self.last_action = datetime.now()
            
            if drive in ["social_need", "affection"]:
                self.last_interaction = datetime.now()
            
            self._save_state()

# Singleton
_impulse_instance = None

def get_impulse_engine() -> ImpulseEngine:
    global _impulse_instance
    if _impulse_instance is None:
        _impulse_instance = ImpulseEngine()
    return _impulse_instance
