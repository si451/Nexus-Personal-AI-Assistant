
# Nexus Skills System 🧠

This directory functions as a **Dynamic Plugin Registry** for Nexus.
Any Python file you drop here will be automatically loaded as a tool for the AI.

## How to add a new skill

1.  Create a new file, e.g., `my_skill.py`.
2.  Import the decorator: `from skills.loader import skill`.
3.  Write your function and decorate it.

### Example: `weather.py`

```python
from skills.loader import skill
import requests

@skill
def check_weather(city: str):
    """
    Checks the weather for a specific city.
    """
    # ... implementation ...
    return "It is sunny in " + city
```

## Existing Skills
- **`system_control.py`**: Battery, Volume, Screen Lock.
- **`web_research.py`**: Deep Research mode.
- **`productivity.py`**: Timers and Notifications.

## How it works
On startup, `AIassistant.py` scans this folder, imports every module, and registers any function marked with `@skill` into the LLM's toolset.
