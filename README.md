# Nexus AI Assistant

A powerful, private, locally running AI assistant with **vision capabilities**, **memory system**, and **system control tools**.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-Enabled-green.svg)
![Ollama](https://img.shields.io/badge/Ollama-Cloud-purple.svg)

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Multimodal Brain** | Powered by `qwen3-vl:235b-cloud` - can see and understand images |
| 👁️ **Vision System** | Real-time screen capture and analysis using EasyOCR + LLM |
| 💾 **Long-term Memory** | FAISS + DuckDB for semantic memory storage and recall |
| 🛠️ **System Tools** | Shell execution, file operations, web search |
| 🌐 **Web Interface** | Clean, responsive Flask-based UI |

## 🏗️ Architecture

```
Nexus AI
├── 🧠 Brain (AIassistant.py)
│   ├── LangGraph Agent with tool calling
│   ├── Memory-augmented responses
│   └── Qwen3-VL multimodal model
├── 👁️ Senses (senses/eyes.py)
│   ├── Screen capture (MSS)
│   ├── OCR (EasyOCR with GPU)
│   └── Window detection (pygetwindow)
├── 💾 Memory (memory/)
│   ├── brain_limbic.py - FAISS vector store
│   └── embeddings.py - Sentence transformers
└── 🌐 Frontend (templates/index.html)
    └── Responsive chat interface
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.ai) with cloud models access
- Windows 10/11

### Installation

```bash
# Clone the repo
cd AI_assistant

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

Open `http://localhost:5000` in your browser.

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `shell` | Execute system commands |
| `write_file` | Create/overwrite files |
| `open_file` | Open files in default app |
| `see_screen` | Capture and analyze screen |
| `duckduckgo_search` | Web search |

## 📁 Project Structure

```
AI_assistant/
├── app.py              # Flask server
├── AIassistant.py      # Main brain (LangGraph agent)
├── requirements.txt    # Dependencies
├── senses/
│   └── eyes.py         # Vision system (EasyOCR + screen capture)
├── memory/
│   ├── brain_limbic.py # FAISS + DuckDB memory
│   └── embeddings.py   # Sentence transformer embeddings
├── templates/
│   └── index.html      # Chat interface
├── static/
│   └── style.css       # UI styling
└── checkpoints/        # LangGraph conversation state
```

## 🔮 Future Ideas

- [ ] **Stealth Mode**: Desktop overlay excluded from screen sharing
- [ ] **Voice Input**: Whisper-based speech recognition
- [ ] **Autonomous Tasks**: Background task execution
- [ ] **Plugin System**: Extensible tool framework

## ⚙️ Configuration

The default model is `qwen3-vl:235b-cloud`. To change, edit `AIassistant.py`:

```python
self.llm = ChatOllama(
    model="your-model-here",
    temperature=0.7
)
```

## 📝 License

Private project by Siddi Vinayaka.

---

*"Your personal AI assistant that sees, remembers, and acts."*
