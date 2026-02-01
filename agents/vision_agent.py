"""
Vision Subagent
===============
Wraps the NexusEyes system to run continuously and publish events.
"""
import time
import threading
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    
from senses.eyes import NexusEyes
from soul.subconscious import get_subconscious, EventPriority

class VisionAgent:
    def __init__(self):
        self.eyes = NexusEyes()
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None
        self.last_hash = ""
        self.webcam = None
        
        # Face detection
        if CV2_AVAILABLE:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[VisionAgent] Started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
            
    def _check_webcam(self):
        if not CV2_AVAILABLE: return
        
        try:
            # Lazy init
            if self.webcam is None:
                self.webcam = cv2.VideoCapture(0)
                
            ret, frame = self.webcam.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                
                if len(faces) > 0:
                     self.output_bus.publish("vision", "USER_SEEN", {
                         "faces": len(faces)
                     }, EventPriority.NORMAL)
        except Exception:
            pass # Webcam might be busy or unavailable
            
    def _loop(self):
        print(f"[VisionAgent] 👀 Loop active. Watching screen & webcam...")
        while self.running:
            try:
                # 1. Screen Glance
                glance = self.eyes.quick_glance()
                if "error" in glance:
                     time.sleep(5)
                     continue
                
                app = glance.get('active_app', '')
                current_window = glance.get('active_window', '')
                
                # Publish state
                # self.output_bus.publish("vision", "ACTIVE_WINDOW", glance, EventPriority.LOW)
                
                # Event Detection
                if "error" in current_window.lower() or "exception" in current_window.lower():
                     self.output_bus.publish("vision", "ERROR_ON_SCREEN", {
                         "text": current_window,
                         "app": app
                     }, EventPriority.HIGH)
                
                if glance.get('activity_type') == 'media':
                     self.output_bus.publish("vision", "MEDIA_PLAYING", {
                         "title": current_window
                     }, EventPriority.NORMAL)
                     
                # 2. Webcam Check
                self._check_webcam()
                     
                time.sleep(3) 
                
            except Exception as e:
                print(f"[VisionAgent] Error: {e}")
                time.sleep(5)

# Singleton
_vision_agent = None
def get_vision_agent():
    global _vision_agent
    if _vision_agent is None:
        _vision_agent = VisionAgent()
    return _vision_agent
