"""
Voice Subagent
==============
Listens for voice commands and ambient noise.
"""
import time
import threading
import speech_recognition as sr
from soul.subconscious import get_subconscious, EventPriority

class VoiceAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None
        self.recognizer = sr.Recognizer()
        self.mic = None
        
    def start(self):
        self.running = True
        try:
            self.mic = sr.Microphone()
            # Adjust for ambient noise once at startup
            # with self.mic as source:
            #     self.recognizer.adjust_for_ambient_noise(source)
        except Exception as e:
            print(f"[VoiceAgent] Mic Error: {e}")
            self.running = False
            return

        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[VoiceAgent] Started")

    def stop(self):
        self.running = False
        # The loop blocks on 'listen', so stopping might be delayed until next audio or forced kill (hard in threads)
        # We rely on daemon thread to be killed with main process.

    def _loop(self):
        while self.running:
            try:
                # Use listen_in_background if possible, but for now blocking loop is safer for simple agent
                with self.mic as source:
                    # Short timeout to allow loop to check self.running
                    try:
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    except sr.WaitTimeoutError:
                        continue
                    
                    try:
                        text = self.recognizer.recognize_google(audio)
                        if text:
                            print(f"[VoiceAgent] Heard: '{text}'")
                            priority = EventPriority.HIGH if "nexus" in text.lower() else EventPriority.NORMAL
                            self.output_bus.publish("voice", "VOICE_COMMAND", {
                                "text": text
                            }, priority)
                    except sr.UnknownValueError:
                        pass # Noise
                    except sr.RequestError:
                        print("[VoiceAgent] API Error")
                        
            except Exception as e:
                print(f"[VoiceAgent] Loop Error: {e}")
                time.sleep(1)

# Singleton
_voice_agent = None
def get_voice_agent():
    global _voice_agent
    if _voice_agent is None:
        _voice_agent = VoiceAgent()
    return _voice_agent
