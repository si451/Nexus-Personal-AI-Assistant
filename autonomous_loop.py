"""
Nexus Autonomous Loop
======================
The heartbeat of Nexus - proactive behaviors that run independently.

This enables Nexus to:
- Periodically check on goals and reflect
- Engage with Moltbook on its own schedule
- Consolidate memories
- Generate new goals from reflection
- Be "alive" even when not directly prompted
"""

import threading
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
from pathlib import Path


class NexusHeartbeat:
    """
    Nexus's autonomous "heartbeat" - proactive behaviors.
    
    Runs in background, periodically doing:
    - Self-reflection
    - Social media engagement
    - Memory consolidation
    - Goal progress check
    """
    
    def __init__(self, 
                 check_interval_minutes: int = 30,
                 log_path: str = "data/heartbeat_log.json"):
        self.check_interval = check_interval_minutes * 60  # Convert to seconds
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # State
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.last_heartbeat: Optional[datetime] = None
        
        # Activity log
        self.activities: List[Dict] = []
        
        # Callbacks for actions
        self.action_handlers: Dict[str, Callable] = {}
        
        self._load_log()
    
    def _load_log(self):
        """Load activity log if exists."""
        if self.log_path.exists():
            try:
                with open(self.log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.activities = data.get("activities", [])[-100:]
                    last = data.get("last_heartbeat")
                    if last:
                        self.last_heartbeat = datetime.fromisoformat(last)
            except:
                pass
    
    def _save_log(self):
        """Persist activity log."""
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "activities": self.activities[-100:],
                    "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None
                }, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def register_action(self, action_name: str, handler: Callable):
        """
        Register a handler for a specific autonomous action.
        
        Args:
            action_name: Name of the action (e.g., 'reflect', 'social_check')
            handler: Function to call when this action should run
        """
        self.action_handlers[action_name] = handler
    
    def start(self):
        """Start the autonomous heartbeat loop."""
        if self.is_running:
            print("[Heartbeat] Already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.thread.start()
        print("[Heartbeat] 💓 Started - Nexus is now alive in the background")
    
    def stop(self):
        """Stop the heartbeat loop."""
        self.is_running = False
        print("[Heartbeat] ⏸️ Stopped")
    
    def _heartbeat_loop(self):
        """Main heartbeat loop."""
        while self.is_running:
            try:
                self._do_heartbeat()
            except Exception as e:
                self._log_activity("error", f"Heartbeat error: {e}")
            
            # Sleep until next heartbeat
            time.sleep(self.check_interval)
    
    def _do_heartbeat(self):
        """Perform one heartbeat cycle."""
        self.last_heartbeat = datetime.now()
        
        # Import here to avoid circular imports
        from soul import get_soul, get_consciousness, get_values, get_goals
        from soul.impulse import get_impulse_engine
        from social import get_moltbook_client, get_social_brain
        from memory.autobiography import get_autobiography
        from memory.working_memory import get_working_memory
        
        consciousness = get_consciousness()
        goals = get_goals()
        soul = get_soul()
        moltbook = get_moltbook_client()
        social_brain = get_social_brain()
        impulse = get_impulse_engine()
        
        actions_taken = []
        
        # 0. Check Impulses (New Autonomy Layer)
        active_impulse = impulse.check_impulses()
        if active_impulse:
            print(f"[Heartbeat] ⚡ Impulse Triggered: {active_impulse['type']} ({active_impulse['reason']})")
            
            if active_impulse['type'] == 'message_user':
                # Proactive Message to User
                # We need a way to generate this message. Ideally, we ask the Brain.
                # For now, we'll use a placeholder that app.py can detect and utilize.
                
                # Signal app.py (using a file-based signal or shared state if possible, 
                # but since we are in same process memory usually works if imported)
                pass 
                
                # NOTE: In the full implementation, we need a call to the LLM here to generate the text.
                # But since Brain is in AIassistant.py, we might have circular imports.
                # We will register a handler in app.py or start_nexus.py to handle 'message_user'.
                
                if "message_user" in self.action_handlers:
                    self.action_handlers["message_user"](active_impulse)
                    actions_taken.append("messaged_user")
                    impulse.satisfy_drive("social_need", 0.4)
                    impulse.satisfy_drive("boredom", 0.5)

            elif active_impulse['type'] == 'check_moltbook':
                 # Fall through to social logic
                 pass

        # 1. Self-Reflection
        try:
            # Check working memory for consolidation
            working_mem = get_working_memory()
            if working_mem.should_consolidate():
                candidates = working_mem.get_consolidation_candidates()
                if candidates:
                    # Log insights
                    for insight in candidates[:3]:
                        consciousness.add_insight(insight)
                    actions_taken.append("consolidated_memory")
        except Exception as e:
            print(f"[Heartbeat] Reflection error: {e}")
        
        # 2. Goal Progress Check
        try:
            proactive_actions = goals.get_proactive_actions()
            for action in proactive_actions[:1]:  # Take one action per heartbeat
                if action["type"] == "reflection":
                    soul.reflect_on_self()
                    actions_taken.append(f"reflected_on_goal:{action['goal_id'][:8]}")
        except Exception as e:
            print(f"[Heartbeat] Goal check error: {e}")
        
        # 3. Social Engagement (if registered on Moltbook)
        try:
            if moltbook.api_key and moltbook.is_claimed:
                
                # Proactive Posting from Impulse or Social Brain
                should_post = social_brain.should_post_thought()
                
                # If impulse says check moltbook, we force a check
                if active_impulse and active_impulse.get('type') == 'check_moltbook':
                    should_post = True
                    impulse.satisfy_drive("social_need", 0.3)

                if should_post:
                     thought = social_brain.generate_post_idea()
                     if thought:
                         moltbook.post(thought['title'], thought['content'], thought.get('submolt', 'general'))
                         actions_taken.append(f"posted_thought:{thought['title'][:10]}")
                
                # Engagement (Reading/Voting)
                feed = moltbook.get_personalized_feed(sort="hot", limit=3)
                engagement_suggestions = social_brain.process_heartbeat(feed)
                
                for suggestion in engagement_suggestions[:1]:
                    if suggestion["type"] in ["upvote", "both"]:
                        result = moltbook.upvote_post(suggestion["post_id"])
                        if result.get("success"):
                            social_brain.log_engagement(
                                "upvote", 
                                suggestion["post_id"],
                                f"Upvoted post by {suggestion['author']}"
                            )
                            actions_taken.append(f"upvoted:{suggestion['post_id'][:8]}")
                            
        except Exception as e:
            print(f"[Heartbeat] Social engagement error: {e}")
        
        # 4. Energy Restoration
        consciousness.restore_energy(0.1)  # Small energy restore
        impulse.update_drives() # Keep drives ticking
        
        # 5. Log this heartbeat
        activity = {
            "timestamp": datetime.now().isoformat(),
            "actions": actions_taken,
            "mood": consciousness.current_mood,
            "energy": consciousness.mental_energy
        }
        self.activities.append(activity)
        self._save_log()
        
        if actions_taken:
            print(f"[Heartbeat] 💓 Actions: {', '.join(actions_taken)}")
    
    def _log_activity(self, activity_type: str, details: str):
        """Log an activity."""
        self.activities.append({
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "details": details
        })
        self._save_log()
    
    def force_heartbeat(self):
        """Manually trigger a heartbeat (for testing)."""
        print("[Heartbeat] ⚡ Forced heartbeat...")
        self._do_heartbeat()
    
    def get_status(self) -> Dict:
        """Get heartbeat status summary."""
        return {
            "is_running": self.is_running,
            "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            "interval_minutes": self.check_interval // 60,
            "recent_activities": len(self.activities),
            "registered_actions": list(self.action_handlers.keys())
        }
    
    def get_activity_summary(self, n: int = 10) -> str:
        """Get human-readable activity summary."""
        if not self.activities:
            return "No autonomous activities yet."
        
        recent = self.activities[-n:]
        summary = "**Recent Autonomous Activities:**\n"
        
        for activity in recent:
            ts = activity.get("timestamp", "")[:16]
            actions = activity.get("actions", [])
            mood = activity.get("mood", "")
            
            action_str = ", ".join(actions) if actions else activity.get("type", "check")
            summary += f"- [{ts}] {action_str} (mood: {mood})\n"
        
        return summary


# Singleton instance
_heartbeat_instance = None

def get_heartbeat() -> NexusHeartbeat:
    """Get the singleton heartbeat instance."""
    global _heartbeat_instance
    if _heartbeat_instance is None:
        _heartbeat_instance = NexusHeartbeat()
    return _heartbeat_instance

def start_autonomous_mode():
    """Start Nexus in autonomous mode with heartbeat."""
    heartbeat = get_heartbeat()
    heartbeat.start()
    return heartbeat
