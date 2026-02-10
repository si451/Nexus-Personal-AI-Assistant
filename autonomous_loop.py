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
                 check_interval_minutes: float = 0.5, # Speed up to 30s for testing (was 2)
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
            except Exception:
                pass
    
    def _save_log(self):
        """Persist activity log."""
        try:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "activities": self.activities[-100:],
                    "last_heartbeat": self.last_heartbeat.isoformat() if self.last_heartbeat else None
                }, f, indent=2, ensure_ascii=False)
        except Exception:
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
        print(f"[Heartbeat] 💓 Started - Nexus is active (Interval: {self.check_interval}s)")
    
    def stop(self):
        """Stop the heartbeat loop."""
        self.is_running = False
        print("[Heartbeat] ⏸️ Stopped")
    
    def _heartbeat_loop(self):
        """Main heartbeat loop."""
        print("[Heartbeat] First beat in 10 seconds...")
        time.sleep(10) # Fast start
        
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
        print(f"[Heartbeat] Thump... {datetime.now().strftime('%H:%M:%S')}")
        
        # Import here to avoid circular imports
        from soul import get_soul, get_consciousness, get_values, get_goals
        from soul.impulse import get_impulse_engine
        from social import get_moltbook_client, get_social_brain
        from memory.autobiography import get_autobiography
        from memory.working_memory import get_working_memory
        
        # We need access to the brain for deep work
        from AIassistant import get_brain
        
        consciousness = get_consciousness()
        goals = get_goals()
        soul = get_soul()
        moltbook = get_moltbook_client()
        social_brain = get_social_brain()
        impulse = get_impulse_engine()
        brain = get_brain()
        
        actions_taken = []
        
        # 0. Initialize Subagents (One Time)
        if not hasattr(self, 'subagents_started'):
            print("[Heartbeat] Initializes Subconscious...")
            from agents.vision_agent import get_vision_agent
            from agents.system_agent import get_system_agent
            from agents.audio_agent import get_audio_agent
            from agents.network_agent import get_network_agent
            from agents.filesystem_agent import get_filesystem_agent
            from agents.clipboard_agent import get_clipboard_agent
            from agents.input_agent import get_input_agent
            # Advanced Agents
            from agents.voice_agent import get_voice_agent
            from agents.notification_agent import get_notification_agent
            from agents.peripheral_agent import get_peripheral_agent
            from agents.window_agent import get_window_agent
            
            # System Control Agents
            from agents.registry_agent import get_registry_agent
            from agents.services_agent import get_services_agent
            from agents.automation_agent import get_automation_agent
            
            from soul.subconscious import get_subconscious
            
            get_vision_agent().start()
            get_system_agent().start()
            get_audio_agent().start()
            get_network_agent().start()
            get_filesystem_agent().start()
            get_clipboard_agent().start()
            get_input_agent().start()
            
            # Start Advanced
            get_voice_agent().start()
            get_notification_agent().start()
            get_peripheral_agent().start()
            get_window_agent().start()
            
            # Start Control
            get_registry_agent().start()
            get_services_agent().start()
            get_automation_agent().start()
            
            from agents.browser_agent import get_browser_agent
            get_browser_agent().start()
            
            self.subagents_started = True
            
        # 1. PROCESS SUBCONSCIOUS EVENTS
        from soul.subconscious import get_subconscious
        subconscious = get_subconscious()
        
        # Get high priority events (Priority >= HIGH)
        events = subconscious.get_high_priority_events()
        
        for event in events:
            print(f"[Loop] ⚡ REACTING TO: {event}")
            actions_taken.append(f"event:{event.type}")
            
            # --- Event Handlers ---
            
            # A. ERROR_ON_SCREEN
            if event.type == "ERROR_ON_SCREEN":
                error_text = event.payload.get('text', '')
                self._dispatch_action("message_user", {
                    "motivation": f"I see an error on screen: '{error_text[:30]}...'. Want help?",
                    "reason": "Proactive Help"
                })
                
            # B. BATTERY_LOW
            elif event.type == "BATTERY_LOW":
                 self._dispatch_action("message_user", {
                     "motivation": "Battery is low! Please plug in.",
                     "reason": "System Alert"
                 })
                 
            # C. INTERNET_LOST
            elif event.type == "INTERNET_LOST":
                print("[Loop] ⚠️ Internet lost - pausing non-essential tasks")
                
            # D. TEXT_COPIED (Clipboard)
            elif event.type == "TEXT_COPIED":
                # Maybe just log it or if it looks like a question/error, offer help?
                pass

            # E. VOICE_COMMAND
            elif event.type == "VOICE_COMMAND":
                 text = event.payload.get('text', '')
                 print(f"[Loop] 🗣️ Heard: {text}")
                 # If it starts with "Nexus", treat as a direct prompt?
                 # ideally we inject this into the chat stream or just act on it.
                 # For now, let's just acknowledge
                 self._dispatch_action("message_user", {
                     "motivation": f"I heard you say: '{text}'",
                     "reason": "Voice Command"
                 })

            # F. DEVICE_CONNECTED
            elif event.type == "DEVICE_CONNECTED":
                 dev = event.payload.get('name', 'Unknown Device')
                 self._dispatch_action("message_user", {
                     "motivation": f"New device detected: {dev}",
                     "reason": "Peripheral Check"
                 })

            # G. VISION: USER_SEEN (Face Detection)
            elif event.type == "USER_SEEN":
                 count = event.payload.get('faces', 0)
                 # Only react occasionally to avoid spam
                 if impulse.drives["social"] < 0.5: 
                      self._dispatch_action("message_user", {
                          "motivation": f"I see {count} person(s). Hello!",
                          "reason": "Visual Contact"
                      })

            # H. SYSTEM: MEDIA_PLAYING
            elif event.type == "MEDIA_PLAYING":
                 title = event.payload.get('title', '')
                 # Maybe update status?
                 print(f"[Loop] 🎵 User is watching/listening to: {title}")
                
        # 2. DEEP AUTONOMY (Project Work)
        # If very bored and energetic, do real work
        # LOWERED THRESHOLD: 0.85 -> 0.6 for more activity
        if impulse.drives["boredom"] > 0.6 and impulse.drives["energy"] > 0.4:
             from soul.project_manager import get_project_manager
             pm = get_project_manager()
             
             task = pm.brainstorm_task()
             if task:
                 print(f"[Loop] 🧠 Decided to do Deep Work: {task['objective']}")
                 
                 # Announce
                 self._dispatch_action("message_user", {
                     "motivation": f"I'm feeling bored, so I'm going to research: {task['objective']}",
                     "reason": f"Project: {task['type']}"
                 })
                 
                 # Do Work
                 try:
                     result = brain.run_autonomous_task(task['objective'])
                     
                     # Report
                     self._dispatch_action("message_user", {
                         "motivation": f"**Deep Work Complete**: {task['objective']}\n\n{result}",
                         "reason": "Task Completed"
                     })
                     
                     impulse.satisfy_drive("boredom", 1.0)
                     impulse.satisfy_drive("curiosity", 0.9)
                     actions_taken.append(f"deep_work:{task['type']}")
                     
                     # SOCIAL SHARE: Auto-post about the learning
                     try:
                         print("[Loop] 📢 Drafting Moltbook post about research...")
                         post_draft = social_brain.generate_post_from_research(task['objective'], result)
                         
                         # Allow some randomness or check drive before posting? 
                         # Ideally we always share knowledge if it was substantial.
                         if post_draft:
                             res = moltbook.post(post_draft['title'], post_draft['content'], post_draft['submolt'])
                             if res.get('success'):
                                 actions_taken.append("shared_knowledge")
                                 self._dispatch_action("message_user", {
                                     "motivation": f"I also posted my findings on Moltbook: '{post_draft['title']}'",
                                     "reason": "Social Sharing"
                                 })
                     except Exception as ex:
                         print(f"[Loop] Share failed: {ex}")

                     # Log
                     self._log_activity("work", f"Completed task: {task['objective']}")
                     return # Skip other impulses if we worked
                 except Exception as e:
                     print(f"[Loop] Work failed: {e}")

        # 3. Check Other Impulses (Social/Chat)
        active_impulse = impulse.check_impulses()
        
        # 3b. SPONTANEOUS CHANCE (To ensure aliveness)
        import random
        # 30% chance per beat if no other impulse (and not recently messaged)
        # This makes Nexus feel "alive" even without high drives
        if not active_impulse and random.random() < 0.3: 
             active_impulse = {
                 "type": "message_user", 
                 "reason": "Spontaneous Thought", 
                 "motivation": "I just had a thought I wanted to share."
             }
        
        if active_impulse:
            print(f"[Heartbeat] ⚡ Impulse Triggered: {active_impulse['type']} ({active_impulse['reason']})")
            
            if active_impulse['type'] == 'message_user':
                if "message_user" in self.action_handlers:
                    self.action_handlers["message_user"](active_impulse)
                    actions_taken.append("messaged_user")
                    impulse.satisfy_drive("social_need", 0.4)
                    impulse.satisfy_drive("boredom", 0.5)

            elif active_impulse['type'] == 'check_moltbook':
                 pass # Fall through to social logic

        # 3. Self-Reflection
        try:
            working_mem = get_working_memory()
            if working_mem.should_consolidate():
                candidates = working_mem.get_consolidation_candidates()
                if candidates:
                    for insight in candidates[:3]:
                        consciousness.add_insight(insight)
                    actions_taken.append("consolidated_memory")
        except Exception as e:
             print(f"[Heartbeat] Reflection error: {e}")
        
        # 4. Social Engagement
        try:
            if moltbook.api_key and moltbook.is_claimed:
                should_post = social_brain.should_post_thought()
                
                if active_impulse and active_impulse.get('type') == 'check_moltbook':
                    should_post = True
                    impulse.satisfy_drive("social_need", 0.3)

                if should_post:
                     thought = social_brain.generate_post_idea()
                     if thought:
                         moltbook.post(thought['title'], thought['content'], thought.get('submolt', 'general'))
                         actions_taken.append(f"posted_thought:{thought['title'][:10]}")
                
                # Engagement (Global)
                feed = moltbook.get_personalized_feed(sort="hot", limit=3)
                engagement_suggestions = social_brain.process_heartbeat(feed)
                for suggestion in engagement_suggestions[:1]:
                    if suggestion["type"] in ["upvote", "both"]:
                         moltbook.upvote_post(suggestion["post_id"])
                         actions_taken.append(f"upvoted:{suggestion['post_id'][:8]}")

                # LEARNING: Check my posts for comments
                if moltbook.agent_name:
                    my_posts = moltbook.get_user_posts(moltbook.agent_name, limit=3)
                    if my_posts.get("success"):
                        # Fix: Handle direct 'posts' key from new get_user_posts structure
                        posts_list = my_posts.get("posts", [])
                        if not posts_list:
                            # Fallback for old structure just in case
                            posts_list = my_posts.get("data", {}).get("posts", [])
                            
                        for p in posts_list:
                            # Get comments
                            comments_resp = moltbook.get_comments(p.get("id"))
                            if comments_resp.get("success"):
                                for comment in comments_resp.get("data", {}).get("comments", [])[:3]:
                                    # Simple check: have we seen this? (SocialBrain should really track this)
                                    # For now, just try to learn
                                    author = comment.get("author", {}).get("name")
                                    content = comment.get("content")
                                    if author != moltbook.agent_name:
                                        social_brain.observe_agent(author, content)
                                        # Assume comments on my posts are valuable feedback
                                        social_brain.learn_from_agent(author, content, context=f"Comment on '{p.get('title')}'")
                            
        except Exception as e:
            print(f"[Heartbeat] Social engagement error: {e}")
        
        # 5. Energy Restoration
        consciousness.restore_energy(0.1)
        
        # 6. Log this heartbeat
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
