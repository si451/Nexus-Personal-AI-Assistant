"""
Verification Script for Browser Agent
=====================================
Tests:
1. Browser Launch.
2. Navigation.
3. Reading content.
"""
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.getcwd())

def verify_browser():
    print("\n--- Testing Browser Agent ---")
    try:
        from agents.browser_agent import get_browser_agent
        
        # Start
        print("Launching Browser Agent...")
        agent = get_browser_agent()
        agent.start()
        
        # Navigate
        print("Navigating to example.com...")
        res = agent.navigate("https://example.com")
        print(f"Result: {res}")
        
        # Read
        print("Reading Page...")
        content = agent.read_page()
        print(f"Content Preview:\n{content[:200]}")
        
        if "Example Domain" in content:
             print("✅ Browser Navigation & Read Success")
             success = True
        else:
             print("❌ Content verification failed")
             success = False
             
        # Cleanup
        agent.stop()
        return success
    except Exception as e:
        print(f"FAIL: {e}")
        return False

if __name__ == "__main__":
    if verify_browser():
        print("\n✅ BROWSER VERIFIED")
    else:
        print("\n❌ BROWSER FAILED")
