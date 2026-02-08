"""
Verification Script for Autonomous Subagents
============================================
Checks if all 7 subagents can initialize and publish to the Subconscious.
"""
import sys
import os
import time
import threading

# Add parent directory to path
sys.path.append(os.getcwd())

from soul.subconscious import get_subconscious, EventPriority

def dummy_listener(event):
    print(f"✅ EVENT RECEIVED: {event}")

def verify_all():
    print("--- Nexus Subagent Verification ---\n")
    bus = get_subconscious()
    bus.subscribe("all", dummy_listener)
    
    agents = []
    
    # 1. Vision
    try:
        from agents.vision_agent import get_vision_agent
        print("Starting Vision Agent...")
        v = get_vision_agent()
        v.start()
        agents.append(v)
    except Exception as e:
        print(f"❌ Vision Agent Failed: {e}")

    # 2. System
    try:
        from agents.system_agent import get_system_agent
        print("Starting System Agent...")
        s = get_system_agent()
        s.start()
        agents.append(s)
    except Exception as e:
        print(f"❌ System Agent Failed: {e}")

    # 3. Audio
    try:
        from agents.audio_agent import get_audio_agent
        print("Starting Audio Agent...")
        a = get_audio_agent()
        a.start()
        agents.append(a)
    except Exception as e:
        print(f"❌ Audio Agent Failed: {e}")

    # 4. Network
    try:
        from agents.network_agent import get_network_agent
        print("Starting Network Agent...")
        n = get_network_agent()
        n.start()
        agents.append(n)
    except Exception as e:
        print(f"❌ Network Agent Failed: {e}")

    # 5. FileSystem
    try:
        from agents.filesystem_agent import get_filesystem_agent
        print("Starting FileSystem Agent...")
        f = get_filesystem_agent()
        f.start()
        agents.append(f)
    except Exception as e:
        print(f"❌ FileSystem Agent Failed: {e}")

    # 6. Clipboard
    try:
        from agents.clipboard_agent import get_clipboard_agent
        print("Starting Clipboard Agent...")
        c = get_clipboard_agent()
        c.start()
        agents.append(c)
    except Exception as e:
        print(f"❌ Clipboard Agent Failed: {e}")

    # 7. Input
    try:
        from agents.input_agent import get_input_agent
        print("Starting Input Agent...")
        i = get_input_agent()
        i.start()
        agents.append(i)
    except Exception as e:
        print(f"❌ Input Agent Failed: {e}")
        
    print("\n⏳ Listening for events for 10 seconds...")
    time.sleep(10)
    
    print("\n--- Stopping Agents ---")
    for a in agents:
        try:
            a.stop()
        except:
            pass
            
    # Check history
    history = bus.get_recent_history()
    print(f"\nTotal Events Captured: {len(history)}")
    for h in history:
        print(f"  - {h}")

if __name__ == "__main__":
    verify_all()
