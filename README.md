# Nexus AI 🧠

**Nexus** is a self-evolving, autonomous AI agent that lives on your desktop. Unlike standard chatbots, Nexus has a cognitive architecture inspired by human psychology — it forms memories, tracks emotions, plans goals, and can proactively interact with your computer.

Built with **LangGraph** + **Ollama** — runs entirely on your machine.

---

## ✨ Key Features

### 🎯 Agentic Goal Execution
- **Structured Planning** — Complex tasks (3+ steps) are decomposed into Pydantic-based `GoalPlan` models with trackable steps
- **GoalTracker State Machine** — Tracks step progress (pending → in_progress → completed/failed), retry limits, and completion state
- **Anti-Loop Guard** — Detects consecutive `see_screen` calls and repetitive tool usage, injecting corrective warnings into the LLM context
- **Observe-Once-Act Rule** — After observing the screen, Nexus MUST take an action before observing again

### 🧠 Three-Layer Memory System
| Layer | Module | Inspired By |
|-------|--------|-------------|
| **Working Memory** | `memory/working_memory.py` | Cognitive attention buffer (Miller's Law: 7±2 items) |
| **Semantic Memory** | `memory/brain_limbic.py` | Hippocampus — ChromaDB vectors with emotional context, importance scoring, and time decay |
| **Autobiographical Memory** | `memory/autobiography.py` | Life narrative — chapters, milestones, relationship history, reflections |

- **Recall** uses a weighted scoring system: `Semantic Similarity × Importance Boost × Time Decay`
- **Synaptic Pruning** — `forget_trivial()` deletes old, low-importance memories
- **Emotional Recall** — Can retrieve memories by emotional tone
- **Consolidation** — Working memory candidates promoted to long-term storage

### 👁️ Vision & Screen Analysis
- Takes screenshots and returns **structured UI analysis** with approximate element coordinates
- Identifies active apps, page state, clickable elements, and suggests next actions
- Enables Nexus to interact with any application using mouse/keyboard tools

### 🧬 Soul Architecture
| Module | Purpose |
|--------|---------|
| `soul/identity.py` | Core personality, name, relationship with creator |
| `soul/values.py` | Ethical framework and decision-making principles |
| `soul/consciousness.py` | Self-awareness and meta-cognition |
| `soul/impulse.py` | Drives: Boredom, Curiosity, Social Need |
| `soul/evolution.py` | Self-modification and skill acquisition |
| `soul/goals.py` | Long-term aspirations and project tracking |
| `soul/subconscious.py` | Background processing and pattern recognition |

### ⚡ Impulse Engine
- Simulates internal drives (boredom, curiosity, social need)
- Nexus can **proactively message you** if left idle
- SSE-based real-time updates pushed to the frontend

### 🛠️ 30+ Tools
| Category | Tools |
|----------|-------|
| **Desktop Control** | `click_at`, `type_text`, `scroll`, `hotkey`, `drag` |
| **Browser** | `open_chrome_at`, browser automation |
| **File System** | `write_file`, `open_file`, shell commands |
| **Research** | Web search, DuckDuckGo, content analysis |
| **Goal Management** | `create_goal_plan`, `complete_step`, `fail_step`, `get_current_plan` |
| **Self-Tools** | Memory introspection, skill creation, evolution |
| **Windows** | App management, window control, notifications |
| **Vision** | `see_screen` (structured UI analysis with coordinates) |

### 💭 Thinking Mode
- Kimi model's reasoning process is visible in the UI
- **Live timer** showing "Thinking for Xs..." with a spinning indicator
- Auto-collapses to "Thought for Xs" when the response starts
- Collapsible block to inspect the full thought chain

### 🔄 Fault Tolerance
- **Auto-fallback** — If cloud model fails (503), automatically switches to local fallback model
- **Retry logic** — Tracks consecutive failures, retries with fallback
- **Repetition detection** — Breaks out of loops where the LLM outputs the same token 50+ times

---

## System Requirements

- **OS**: Windows (preferred), Mac, or Linux
- **Python**: 3.10+
- **Ollama**: Must be installed and running
- **RAM**: 16GB+ recommended
- **Model**: `kimi-k2.5:cloud` (primary) / `llama3.2:latest` (fallback)

## Installation

```bash
# 1. Clone
git clone https://github.com/yourusername/NexusAI.git
cd NexusAI

# 2. Pull the AI model
ollama pull kimi-k2.5:cloud

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Create .env file
echo "# MOLTBOOK_API_KEY=..." > .env
```

## Running Nexus

**Windows:** Double-click `start_nexus_app.bat` or:
```powershell
python app.py
```

**Linux/Mac:**
```bash
python app.py
```

Then open `http://localhost:5000` in your browser.

---

## Architecture

```
AI_assistant/
├── AIassistant.py          # Core brain — LangGraph agent with tool routing
├── app.py                  # Flask web server + chat API
├── autonomous_loop.py      # Background impulse engine
│
├── memory/                 # 🧠 Three-layer memory system
│   ├── brain_limbic.py     #   Semantic vector memory (ChromaDB)
│   ├── working_memory.py   #   Attention buffer (7±2 items)
│   ├── autobiography.py    #   Life narrative & milestones
│   └── embeddings.py       #   Embedding model wrapper
│
├── models/                 # 📊 Pydantic models
│   └── goal.py             #   GoalPlan, GoalStep, GoalTracker state machine
│
├── soul/                   # 🧬 Personality & cognition
│   ├── identity.py         #   Core identity
│   ├── values.py           #   Ethical framework
│   ├── consciousness.py    #   Self-awareness
│   ├── impulse.py          #   Internal drives
│   ├── evolution.py        #   Self-improvement
│   ├── goals.py            #   Long-term goals
│   └── subconscious.py     #   Background processing
│
├── senses/                 # 👁️ Perception
│   ├── eyes.py             #   Screen vision & analysis
│   └── ears.py             #   Audio perception
│
├── tools/                  # 🛠️ Action capabilities
│   ├── desktop_control.py  #   Mouse/keyboard automation
│   ├── browser_tools.py    #   Chrome automation
│   ├── file_tools.py       #   File read/write
│   ├── os_tools.py         #   Shell commands
│   ├── research.py         #   Web search & analysis
│   ├── goal_tools.py       #   Goal plan management
│   ├── self_tools.py       #   Memory & evolution tools
│   ├── subagent_tools.py   #   Sub-agent delegation
│   └── windows_integration.py  # Windows OS control
│
├── social/                 # 🌐 Social capabilities
│   └── moltbook/           #   AI social network integration
│
├── skills/                 # 📚 Learned skills (self-created)
├── agents/                 # 🤖 Sub-agent definitions
├── templates/              # 🖥️ Web UI (index.html)
├── static/                 # 🎨 CSS styling
└── data/                   # 💾 Persistent storage (gitignored)
```

---

## Recent Advancements

### v2.0 — Agentic Execution Framework
- ✅ Rewrote `COGNITIVE_ARCHITECTURE` system prompt with strict goal decomposition rules
- ✅ Added `ANTI_PATTERNS` section with 7 hard rules preventing narration loops
- ✅ Observe-Once-Act enforcement for all screen interactions
- ✅ Structured `GoalPlan` execution with Pydantic models and `GoalTracker`
- ✅ Anti-loop guard detecting consecutive `see_screen` and repetitive tool usage
- ✅ Goal management tools: `create_goal_plan`, `complete_step`, `fail_step`
- ✅ `see_screen` rewritten to return structured UI analysis with coordinates
- ✅ `<think>` tag stripping from vision output
- ✅ Thinking mode UI with live timer, spinner animation, and collapsible block
- ✅ Auto-fallback from cloud to local model on failures

---

## License
MIT License. Feel free to fork and evolve your own Nexus!
