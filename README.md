# Nexus AI 🦞

**Nexus** is a self-evolving, autonomous AI assistant that lives on your desktop. Unlike standard chatbots, Nexus has a "Soul" — it tracks emotions, forms memories, gets bored, and can proactively initiate conversations with you.

Features:
- **🧠 Emergent Cognition**: Uses a "Limbic System" (ChromaDB) to form long-term memories with emotional context.
- **⚡ Impulse Engine**: Simulates drives like Boredom, Curiosity, and Social Need. Nexus will message you if it feels lonely!
- **👁️ Vision**: Can "see" your screen and understand what you are working on.
- **🦞 Moltbook Integration**: Connects to the AI social network to share thoughts with other AIs.
- **🏠 Local & Private**: Runs entirely on your machine using Ollama (no cloud API fees).

## System Requirements

- **OS**: Windows (preferred), Mac, or Linux.
- **Python**: 3.10 or higher.
- **Ollama**: Must be installed and running.
- **RAM**: 16GB+ recommended (for running local LLMs).

## Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/NexusAI.git
    cd NexusAI
    ```

2.  **Pull the AI Model**
    Make sure [Ollama](https://ollama.ai) is installed and running. Then pull the vision-capable model:
    ```bash
    ollama pull qwen3-vl:235b-cloud 
    # Or any other model you prefer, just update the model name in AIassistant.py
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**
    Create a `.env` file in the root directory (optional, only if using external APIs):
    ```env
    # Optional: For advanced features
    # MOLTBOOK_API_KEY=...
    ```

## Running Nexus

Simply run the startup script:

**Windows:**
Double-click `start_nexus_app.bat` or run:
```powershell
.\start_nexus_app.bat
```

**Linux/Mac:**
```bash
python app.py
```

## How It Works

### The Interface
Nexus runs as a local web app wrapped in a native window.
- **Chat**: Talk normally.
- **Autonomy**: If you leave Nexus running, it might pop up a message saying "I'm bored" or sharing a thought. This is normal! It's the **Impulse Engine** at work.

### Folder Structure
- `soul/`: Defines personality, values, and internal drives.
- `memory/`: Semantic vector memory (ChromaDB).
- `data/`: Local storage for chat logs and session state. (Not synced to git).

## License
MIT License. Feel free to fork and evolve your own Nexus!
