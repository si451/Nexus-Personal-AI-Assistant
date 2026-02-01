"""
Verification Script for Nexus Improvements
==========================================
Tests:
1. Audio (Ears)
2. Windows Integration (App State)
3. Evolution (Sandbox)
"""
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.getcwd())

def test_ears():
    print("\n--- Testing Ears (Audio) ---")
    try:
        from senses.ears import get_ears
        ears = get_ears()
        vol = ears.get_volume()
        print(f"Current Volume: {vol:.2f}")
        
        # Test mute/unmute
        print(ears.mute())
        time.sleep(1)
        print(ears.unmute())
        
        return True
    except ImportError:
        print("FAIL: pycaw not installed or ImportError")
        return False
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_windows():
    print("\n--- Testing Windows Integration ---")
    try:
        from tools.windows_integration import get_app_state
        # Tools need .invoke or direct function call if not wrapped? 
        # Since it's a StructuredTool, we should use .invoke({"app_name": ...})
        print(get_app_state.invoke({"app_name": "explorer.exe"}))
        print(get_app_state.invoke({"app_name": "non_existent_app_123.exe"}))
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False

def test_evolution():
    print("\n--- Testing Evolution (Sandbox) ---")
    try:
        from soul.evolution import get_sandbox
        sandbox = get_sandbox()
        
        # Create dummy file
        dummy_file = "temp/dummy_evolution_test.py"
        os.makedirs("temp", exist_ok=True)
        with open(dummy_file, "w") as f:
            f.write("print('Original Code')")
            
        # 1. Create Sandbox
        sbox_path = sandbox.create_sandbox(dummy_file)
        print(f"Sandbox created: {sbox_path}")
        
        # 2. Modify Sandbox
        with open(sbox_path, "w") as f:
            f.write("print('Evolved Code')")
            
        # 3. Run Simulation
        success, output = sandbox.run_simulation(sbox_path)
        print(f"Simulation Success: {success}")
        print(f"Output: {output.strip()}")
        
        if not success or "Evolved" not in output:
            print("FAIL: Simulation didn't produce expected output")
            return False
            
        # 4. Apply Evolution
        res = sandbox.apply_evolution(sbox_path)
        print(res)
        
        # Verify Original is changed
        with open(dummy_file, "r") as f:
            content = f.read()
            if "Evolved" in content:
                print("SUCCESS: Evolution applied correctly!")
                return True
            else:
                print("FAIL: Original file not updated")
                return False
                
    except Exception as e:
        print(f"FAIL: {e}")
        return False

if __name__ == "__main__":
    ears_ok = test_ears()
    win_ok = test_windows()
    evo_ok = test_evolution()
    
    if ears_ok and win_ok and evo_ok:
        print("\n✅ ALL SYSTEMS GO")
    else:
        print("\n❌ SOME TESTS FAILED")
