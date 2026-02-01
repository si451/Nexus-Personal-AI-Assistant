
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    print("Imports success")
    
    devices = AudioUtilities.GetSpeakers()
    print(f"Devices type: {type(devices)}")
    print(f"Devices dir: {dir(devices)}")
    
    # Try different access if available
    try:
        interface = devices.Activate(IAudioEndpointVolume._iid_, 7, None) # 7 is CLSCTX_ALL
        print("Activate success")
    except Exception as e:
        print(f"Activate failed: {e}")

except Exception as e:
    print(f"General Error: {e}")
