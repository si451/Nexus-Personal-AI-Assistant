"""
Verification Script for Control Agents
======================================
Tests:
1. Initialization of Registry, Services, Automation agents.
2. Checking 'list_active_agents' output.
"""
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.getcwd())

def verify_system_control():
    print("\n--- Testing System Control Agents ---")
    try:
        from tools.subagent_tools import list_active_agents
        from agents.registry_agent import get_registry_agent
        from agents.services_agent import get_services_agent
        from agents.automation_agent import get_automation_agent
        
        # Start Agents
        print("Initializing Registry Agent...")
        r = get_registry_agent()
        r.start()
        
        print("Initializing Services Agent...")
        s = get_services_agent()
        s.start()
        
        print("Initializing Automation Agent...")
        a = get_automation_agent()
        a.start()
        
        # Test List
        time.sleep(2)
        print("\nListing agents...")
        status = list_active_agents.invoke({})
        print(f"Status Output:\n{status}")
        
        success = True
        if "REGISTRY: 🟢 RUNNING" not in status: success = False
        if "SERVICES: 🟢 RUNNING" not in status: success = False
        if "AUTOMATION: 🟢 RUNNING" not in status: success = False
        
        if success:
            print("✅ All Control Agents Running")
        else:
            print("❌ Agent Status Mismatch")
            
        # Clean shutdown
        r.stop()
        s.stop()
        a.stop()
        
        return success
    except Exception as e:
        print(f"FAIL: {e}")
        return False

if __name__ == "__main__":
    ok = verify_system_control()
    if ok:
        print("\n✅ SYSTEM CONTROL VERIFIED")
    else:
        print("\n❌ VERIFICATION FAILED")
