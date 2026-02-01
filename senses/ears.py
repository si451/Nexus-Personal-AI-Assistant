"""
Nexus Audio System (Ears)
=========================
Allows Nexus to control system volume and listen to audio context.
Uses pycaw for Windows Core Audio Windows API.
"""

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import math

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False
    print("[Ears] ⚠️ pycaw not installed. Audio control disabled.")

class NexusEars:
    def __init__(self):
        self.volume_interface = None
        if PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                # New pycaw wrapper seems to expose EndpointVolume directly?
                # Or we need to use 'devices' which is an AudioDevice object
                # Let's try checking if it has Activate, if not, check EndpointVolume
                if hasattr(devices, 'Activate'):
                     interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                     self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
                elif hasattr(devices, 'EndpointVolume'):
                     self.volume_interface = devices.EndpointVolume
                else:
                     print("[Ears] Could not find volume interface on AudioDevice")
            except Exception as e:
                print(f"[Ears] Error initializing audio: {e}")

    def set_volume(self, level: float) -> str:
        """
        Set master volume level (0.0 to 1.0).
        """
        if not self.volume_interface:
            return "Audio control unavailable."
        
        try:
            # Clamp between 0.0 and 1.0
            level = max(0.0, min(1.0, level))
            self.volume_interface.SetMasterVolumeLevelScalar(level, None)
            return f"Volume set to {int(level * 100)}%"
        except Exception as e:
            return f"Error setting volume: {e}"

    def get_volume(self) -> float:
        """
        Get current master volume (0.0 to 1.0).
        """
        if not self.volume_interface:
            return 0.0
        
        try:
            return self.volume_interface.GetMasterVolumeLevelScalar()
        except Exception as e:
            print(f"[Ears] Error getting volume: {e}")
            return 0.0

    def mute(self):
        """Mute system audio."""
        if self.volume_interface:
            self.volume_interface.SetMute(1, None)
            return "Audio muted."
        return "Audio control unavailable."

    def unmute(self):
        """Unmute system audio."""
        if self.volume_interface:
            self.volume_interface.SetMute(0, None)
            return "Audio unmuted."
        return "Audio control unavailable."

# Singleton
_ears_instance = None

def get_ears() -> NexusEars:
    global _ears_instance
    if _ears_instance is None:
        _ears_instance = NexusEars()
    return _ears_instance
