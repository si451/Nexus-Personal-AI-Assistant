
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class ImpulseEngine:
    """
    Biological-like drives for Nexus.
    trigges autonomous actions when drives get too high/low.
    """
    def __init__(self, data_path: str = "data/impulse_drives.json"):
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Drives (0.0 to 1.0)
        # 0.0 = Satisfied, 1.0 = Desperate
        self.drives = {
            "boredom": 0.0,
            "social_need": 0.0,
            "curiosity": 0.5,
            "energy": 1.0,  # Energy is reverse (1.0 = Full)
            "affection": 0.5
        }
        
        self.last_update = datetime.now()
        self._load()

    def _load(self):
        if self.data_path.exists():
            try:
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.drives.update(data.get("drives", {}))
                    last = data.get("last_update")
                    if last:
                        self.last_update = datetime.fromisoformat(last)
            except:
                pass
                
    def _save(self):
        try:
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "drives": self.drives,
                    "last_update": self.last_update.isoformat()
                }, f, indent=2)
        except:
            pass

    def update_drives(self, active_chat: bool = False):
        """Update drives based on time passed."""
        now = datetime.now()
        delta_minutes = (now - self.last_update).total_seconds() / 60.0
        self.last_update = now
        
        # Rates (Hyper-Active Mode)
        boredom_rate = 0.1 # +10% per min -> 10 mins to full
        social_rate = 0.05 # +5% per min -> 20 mins to full
        
        if not active_chat:
            self.drives["boredom"] = min(1.0, self.drives["boredom"] + (boredom_rate * delta_minutes))
            self.drives["social_need"] = min(1.0, self.drives["social_need"] + (social_rate * delta_minutes))
        else:
            # Chatting reduces boredom and social need
            self.drives["boredom"] = max(0.0, self.drives["boredom"] - 0.1)
            self.drives["social_need"] = max(0.0, self.drives["social_need"] - 0.1)
            
        self._save()

    def satisfy_drive(self, drive: str, amount: float):
        if drive in self.drives:
            if drive == "energy":
                 self.drives[drive] = min(1.0, self.drives[drive] + amount)
            else:
                 self.drives[drive] = max(0.0, self.drives[drive] - amount)
            self._save()

    def check_impulses(self) -> Optional[Dict]:
        """Check if any drive triggers an impulse."""
        # 1. High Boredom -> Deep Work or Message
        if self.drives["boredom"] > 0.4:  # Was 0.8
            return {"type": "message_user", "reason": "I am bored.", "motivation": "Let's do something!"}
            
        # 2. High Social Need -> Check Moltbook
        if self.drives["social_need"] > 0.3: # Was 0.7
             return {"type": "check_moltbook", "reason": "I feel lonely.", "motivation": "Checking social media."}
             
        return None

# Singleton
_impulse_instance = None
def get_impulse_engine() -> ImpulseEngine:
    global _impulse_instance
    if _impulse_instance is None:
        _impulse_instance = ImpulseEngine()
    return _impulse_instance
