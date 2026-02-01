import subprocess
import re

def get_battery_status():
    """
    Checks the current battery percentage and power status.
    Returns:
        dict: {
            'percentage': float (0-100),
            'is_plugged': bool,
            'time_remaining': str (e.g., '1:23:45')
        }
    """
    try:
        # Run powercfg command to get battery report
        result = subprocess.run(
            'powercfg /batteryreport',
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        output = result.stdout
        
        # Extract battery percentage
        percent_match = re.search(r'Battery percentage:\s*(\d+)%', output)
        percentage = float(percent_match.group(1)) if percent_match else 100.0
        
        # Extract power status
        plugged_match = re.search(r'Plugged in:\s*(Yes|No)', output)
        is_plugged = plugged_match.group(1) == 'Yes' if plugged_match else True
        
        # Extract time remaining
        time_match = re.search(r'Estimated time remaining:\s*([0-9:]+)', output)
        time_remaining = time_match.group(1) if time_match else 'N/A'
        
        return {
            'percentage': percentage,
            'is_plugged': is_plugged,
            'time_remaining': time_remaining
        }
    except Exception as e:
        # Fallback for systems without battery (e.g., desktop)
        return {
            'percentage': 100.0,
            'is_plugged': True,
            'time_remaining': 'N/A',
            'error': str(e)
        }