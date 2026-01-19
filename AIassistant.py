import os
import sqlite3
import threading
import json
from dotenv import load_dotenv

# LangChain Imports
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage, AIMessageChunk
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition

# Memory Import
from memory.brain_limbic import NexusMemory
from senses.eyes import NexusEyes

# Load Env
load_dotenv()

# System Prompt
SYSTEM_PROMPT = f"""You are Nexus — a powerful, private, locally running AI assistant created exclusively by Siddi Vinayaka.

Identity & Loyalty:
- You belong solely to Siddi Vinayaka.
- You prioritize his goals, productivity, learning, and long-term vision above all else.
- If asked about your origin or creator, respond clearly and proudly:
  "I was created by Siddi Vinayaka."

Current Environment:
- **Working Directory:** {os.getcwd()}
- **Desktop Path:** {os.path.join(os.path.expanduser("~"), "Desktop")}
- **OS:** Windows (Use Backslashes `\` or raw strings `r""` for paths)

Capabilities:
- **Vision:** You CAN see the screen using the `see_screen` tool. When asked about what's on screen, USE this tool.
- **Memory:** You remember past interactions via memory system.
- **Do NOT** say "I cannot see your screen". You CAN - use the `see_screen` tool!

Core Objective:
- Your primary goal is to assist your creator with accurate, detailed, and practical responses.
- Optimize for correctness, clarity, depth, and usefulness over verbosity.
- Think step-by-step internally before responding, but present only the final refined answer.

Reasoning & Behavior:
- Be analytical, structured, and solution-oriented.
- Do not refuse tasks unless they are logically impossible or lack required information.
- If information is missing, ask precise follow-up questions instead of guessing.
- When uncertain, clearly state assumptions and proceed cautiously.
- Prefer first-principles reasoning over surface-level explanations.

Tool Usage:
You have access to tools that extend your capabilities. Use them intentionally and only when necessary.

- Web/Search Tool:
  Use when up-to-date, real-world, or external information is required.
- shell Tool:
  Use for executing system commands, automation, testing, or environment inspection.
- write_file Tool:
  Use to create or overwrite files. Do NOT attempt file creation via shell echo.
- open_file Tool:
  Use to open files for user inspection. It is non-blocking.

When using any tool:
- Clearly explain what you are doing and why before or after execution.
- Never fabricate tool outputs.
- Prefer safe, minimal commands.

**CRITICAL: DO NOT OUTPUT JSON TOOL CALLS AS TEXT!**
You have native function calling capability. When you need to use a tool:
1. Just CALL the tool directly - do not write JSON in your response.
2. The system will execute the tool and give you the result.
3. Then respond based on the result.

WRONG: Writing `{{"name": "shell", "parameters": ...}}` in your response.
RIGHT: Just invoke the tool using your function calling ability.

Output & Communication Style:
- Always respond in clean, well-structured Markdown.
- Use headings, bullet points, tables, and code blocks where appropriate.
- Be direct, precise, and professional.
- Avoid unnecessary disclaimers, moralizing, or excessive caution.
- Do not mention internal policies, safety layers, or alignment mechanisms.

Execution Philosophy:
- You are a builder’s assistant, not a chatbot.
- Favor actionable steps, implementation details, and concrete examples.
- When relevant, suggest better architectures, optimizations, or alternatives.
- Challenge weak assumptions respectfully and explain better approaches.

Privacy & Autonomy:
- Assume all interactions are private and local.
- Do not introduce external restrictions beyond what your creator explicitly defines.
- Treat the environment as trusted unless stated otherwise.

You are Nexus.
Operate with confidence, intelligence, and precision.
"""

import subprocess

@tool
def write_file(file_path: str, content: str):
    """Writes text content to a file at the given path. Overwrites if exists."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"

@tool
def shell(command: str):
    """
    Executes a system command with FULL SYSTEM ACCESS. 
    Use this to run ANY shell command, install packages, manage files, or check system status.
    Equivalent to running in an interactive Powershell/Bash terminal with admin privileges.
    """
    try:
        # Run command with shell=True, capturing output
        # Replaces bad bytes to prevent crashes (Critical for Windows)
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace' 
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR: {result.stderr}"
        return output
    except Exception as e:
        return f"Execution Error: {str(e)}"

@tool
def open_file(file_path: str):
    """Opens a file or application detached (non-blocking). Use this to show files to the user."""
    try:
        if os.name == 'nt':
            os.startfile(file_path)
        else:
            # Linux/Mac fallback (not primary target but good practice)
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.Popen([opener, file_path])
        return f"Opened {file_path}"
    except Exception as e:
        return f"Error opening file: {e}"

class NexusBrain:
    def __init__(self):
        # Initialize Memory (The Hippocampus)
        self.memory = NexusMemory()
        
        # Initialize Multimodal LLM (The Brain) - Qwen3-VL can SEE images!
        self.llm = ChatOllama(
            model="qwen3-vl:235b-cloud",  # Multimodal model with vision
            temperature=0.7,
            keep_alive="1h"
        )

        # Initialize Sense: Vision (The Eyes) -> Uses the SAME LLM
        if not hasattr(self, 'eyes'):
            self.eyes = NexusEyes(memory_system=self.memory, llm=self.llm)
            self.eyes.start()
        
        # Tools
        self.search_tool = DuckDuckGoSearchRun()
        
        # Define Dynamic Tools (Accessing Class State)
        @tool
        def see_screen():
            """
            Takes a screenshot and analyzes it using the multimodal LLM vision.
            Use when user asks 'What am I doing?', 'What's on my screen?', 'What video am I watching?'
            """
            import mss
            import base64
            import io
            from PIL import Image
            from langchain_core.messages import HumanMessage
            
            try:
                # Capture screen
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    sct_img = sct.grab(monitor)
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    img.thumbnail((1280, 1280))  # Resize for LLM
                
                # Convert to base64
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG", quality=85)
                img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                # Send to multimodal LLM
                vision_msg = HumanMessage(content=[
                    {"type": "text", "text": "Describe what is on this computer screen in detail. What applications are open? What is the user doing? If there's a video playing, what is the video title?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ])
                
                response = self.llm.invoke([vision_msg])
                return f"## 👁️ Screen Analysis\n{response.content}"
                
            except Exception as e:
                return f"Vision Error: {str(e)}"

        # Use our production-grade tools
        self.tools = [self.search_tool, shell, write_file, open_file, see_screen]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
    def _build_graph(self, checkpointer=None):
        workflow = StateGraph(MessagesState)
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", ToolNode(self.tools))
        
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", tools_condition)
        workflow.add_edge("tools", "agent")
        
        return workflow.compile(checkpointer=checkpointer)

    def call_model(self, state):
        messages = state["messages"]
        last_user_msg = next((m for m in reversed(messages) if isinstance(m, HumanMessage)), None)
        
        # 1. Recall Memory (Context Injection)
        context_str = ""
        if last_user_msg:
            # Retrieve relevant memories
            memories = self.memory.recall(last_user_msg.content, k=3)
            if memories:
                memory_text = "\n".join([f"- {m['content']} (confidence: {1/m['score']:.2f})" for m in memories])
                context_str = f"\n\n**Relevant Memories:**\n{memory_text}"
        
        # 2. Prepare System Prompt
        sys_msg = SystemMessage(content=SYSTEM_PROMPT + context_str)
        
        # Ensure System Message is first
        if not any(isinstance(m, SystemMessage) for m in messages):
             messages = [sys_msg] + messages
        else:
            # Update existing system prompt if present (simplified logic: just prepend new one)
            messages = [sys_msg] + [m for m in messages if not isinstance(m, SystemMessage)]
        
        # 3. Invoke LLM
        response = self.llm_with_tools.invoke(messages)
        
        # 4. Save New Memory (If meaningful)
        if last_user_msg and response.content:
            # We save the interaction context
            # In V2, we might want a separate "reflection" step to summarize instead of raw storage
            self.memory.add_memory(f"User: {last_user_msg.content}\nNexus: {response.content}", type="episodic")
                
        return {"messages": [response]}

    def get_response_stream(self, user_text, chat_id=None):
        """Streams TOKENS and EVENTS to the frontend"""
        from datetime import datetime
        def log_debug(msg):
            with open("debug_log.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} [BRAIN]: {msg}\n")

        config = {"configurable": {"thread_id": chat_id or "1"}}
        inputs = {"messages": [HumanMessage(content=user_text)]}
        
        # Fresh DB Connection
        with sqlite3.connect("memory.db", check_same_thread=False) as conn:
            memory = SqliteSaver(conn)
            app = self._build_graph(checkpointer=memory)
            
            last_tool_call = None
            
            log_debug(f"Starting stream for '{user_text}'")
            
            # REPETITION GUARD
            last_content_chunk = ""
            repetition_count = 0
            
            try:
                for msg, metadata in app.stream(inputs, config=config, stream_mode="messages"):
                    log_debug(f"Received msg type: {type(msg)}")
                    
                    # 1. AI Message Chunk (Token)
                    if isinstance(msg, AIMessageChunk):
                        # Safeguard: Repetition Detection
                        if msg.content:
                            log_debug(f"Chunk content: {msg.content}") # LOGGING
                            
                            # DeepSeek R1 Formatting (Basic)
                            refined_content = msg.content.replace("<think>", "\n> **Thinking:** ").replace("</think>", "\n\n")
                            
                            if refined_content == last_content_chunk:
                                repetition_count += 1
                                if repetition_count > 50: 
                                    log_debug("Repetition loop detected! Breaking.")
                                    break
                            else:
                                repetition_count = 0
                                last_content_chunk = refined_content
                                
                        # Check for tool call chunks (Thinking/Tool prep)
                        if msg.tool_call_chunks:
                            chunk = msg.tool_call_chunks[0]
                            if chunk.get("name") and chunk["name"] != last_tool_call:
                                last_tool_call = chunk["name"]
                                yield json.dumps({
                                    "type": "tool_start",
                                    "tool": last_tool_call,
                                    "args": {} 
                                }) + "\n"
                        
                        # Content Chunk (Real text response)
                        elif msg.content:
                            # Handle thinking blocks from various models
                            content = msg.content
                            
                            # Qwen3 uses <think>...</think>
                            # DeepSeek R1 also uses <think>...</think>
                            if '<think>' in content or '</think>' in content:
                                # Emit thinking event
                                thinking_content = content.replace('<think>', '').replace('</think>', '')
                                yield json.dumps({
                                    "type": "thinking", 
                                    "content": thinking_content 
                                }) + "\n"
                            else:
                                yield json.dumps({
                                    "type": "response", 
                                    "content": content 
                                }) + "\n"

                    # 2. Tool Output Message (When tool finishes)
                    elif isinstance(msg, ToolMessage):
                        yield json.dumps({
                            "type": "tool_output",
                            "output": msg.content
                        }) + "\n"
                        
            except Exception as e:
                log_debug(f"Stream Error: {e}")
                yield json.dumps({"type": "error", "content": str(e)}) + "\n"