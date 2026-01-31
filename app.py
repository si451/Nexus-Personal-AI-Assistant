import webview
import threading
import json
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, Response
from AIassistant import NexusBrain

# Initialize Flask
app = Flask(__name__)
brain = NexusBrain()

# Chats storage directory
CHATS_DIR = 'chats'
os.makedirs(CHATS_DIR, exist_ok=True)

# Current active chat
current_chat_id = None

def get_chat_file(chat_id):
    return os.path.join(CHATS_DIR, f'{chat_id}.json')

def load_chat(chat_id):
    filepath = get_chat_file(chat_id)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def save_chat(chat_data):
    filepath = get_chat_file(chat_data['id'])
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=2)

def get_all_chats():
    """Get list of all chats sorted by last updated"""
    chats = []
    if os.path.exists(CHATS_DIR):
        for filename in os.listdir(CHATS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(CHATS_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        chat = json.load(f)
                        chats.append({
                            'id': chat['id'],
                            'title': chat.get('title', 'New Chat'),
                            'updated': chat.get('updated', chat.get('created', ''))
                        })
                except:
                    continue
    # Sort by last updated, newest first
    chats.sort(key=lambda x: x['updated'], reverse=True)
    return chats

def generate_title(first_message):
    """Generate a short title from the first message"""
    title = first_message.strip()
    if len(title) > 40:
        title = title[:37] + '...'
    return title

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chats', methods=['GET'])
def list_chats():
    """List all chat sessions"""
    chats = get_all_chats()
    return jsonify({'chats': chats})

@app.route('/chat/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    """Get a specific chat"""
    chat = load_chat(chat_id)
    if chat:
        return jsonify(chat)
    return jsonify({'error': 'Chat not found'}), 404

@app.route('/new_chat', methods=['POST'])
def new_chat():
    """Create a new chat session"""
    global current_chat_id
    
    chat_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    
    chat = {
        'id': chat_id,
        'title': 'New Chat',
        'created': now,
        'updated': now,
        'messages': []
    }
    
    save_chat(chat)
    current_chat_id = chat_id
    
    return jsonify({'id': chat_id, 'title': 'New Chat'})

@app.route('/message', methods=['POST'])
def send_message():
    """Send a message and get AI response with streaming"""
    global current_chat_id
    
    data = request.json
    print(f"Server: Received request for chat_id={data.get('chat_id')}")
    user_message = data.get('message', '')
    chat_id = data.get('chat_id')
    
    if not chat_id:
        chat_id = str(uuid.uuid4())[:8]
        current_chat_id = chat_id
    
    # We use a generator to stream data to the client
    def generate():
        # First, add user message to our persistent JSON file
        try:
            chat = load_chat(chat_id)
            if not chat:
                chat = {
                    'id': chat_id, 
                    'title': generate_title(user_message), 
                    'created': datetime.now().isoformat(), 
                    'updated': datetime.now().isoformat(),
                    'messages': []
                }
            
            chat['messages'].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
            chat['updated'] = datetime.now().isoformat()
            save_chat(chat)
        except Exception as e:
            print(f"Error saving chat history: {e}")

        # Now stream the brain's thoughts/responses
        print(f"Server: Generating response for '{user_message}'...")
        full_response = ""
        try:
            # chat_id is used as thread_id for brain memory
            for event_json in brain.get_response_stream(user_message, chat_id=chat_id):
                print(".", end="", flush=True) # visual heartbeat in terminal
                yield event_json
                
                # Accumulate final text for history saving
                event = json.loads(event_json)
                if event['type'] == 'response':
                    full_response += event['content']
                    
        except Exception as e:
            yield json.dumps({"type": "error", "content": str(e)}) + "\n"
        
        # Finally save the AI response to history
        if full_response:
            try:
                chat = load_chat(chat_id) 
                if chat:
                    chat['messages'].append({
                        'role': 'ai',
                        'content': full_response,
                        'timestamp': datetime.now().isoformat()
                    })
                    chat['updated'] = datetime.now().isoformat()
                    save_chat(chat)
            except Exception as e:
                 print(f"Error saving AI response: {e}")
                 
        # Send a special 'done' event with metadata
        yield json.dumps({
            "type": "done", 
            "chat_id": chat_id,
            "title": chat.get('title', 'Chat') if chat else 'Chat'
        }) + "\n"

    return Response(generate(), mimetype='application/json')

@app.route('/delete_chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a chat session"""
    filepath = get_chat_file(chat_id)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return jsonify({'status': 'ok'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Chat not found'}), 404

# Proactive Message Queue
import queue
proactive_queue = queue.Queue()

@app.route('/stream_updates')
def stream_updates():
    """Server-Sent Events (SSE) for proactive autonomy"""
    def event_stream():
        while True:
            try:
                # Wait for proactive messages (blocking get with timeout)
                msg = proactive_queue.get(timeout=20)
                
                # Format as SSE
                yield f"data: {json.dumps(msg)}\n\n"
            except queue.Empty:
                # Keep alive
                yield ": keepalive\n\n"
            except GeneratorExit:
                break
    
    return Response(event_stream(), mimetype="text/event-stream")

# Handler to be called by heartbeat
def handle_autonomous_message(impulse_data):
    """Called by autonomous loop when it wants to speak"""
    print(f"[App] 📨 Received autonomous message impulse: {impulse_data}")
    
    # We need to generate the ACTUAL text here since the impulse just gives motivation.
    # We'll do a quick LLM call via the brain.
    
    motivation = impulse_data.get('motivation', 'I want to say hi.')
    # Use a lightweight method if possible, or full brain
    # For speed, we might construct a simple message, but let's try to be authentic.
    
    # Add to queue for frontend
    proactive_queue.put({
        "type": "autonomous_message",
        "sender": "Nexus",
        "content": motivation,  # Ideally this is refined text
        "reason": impulse_data.get('reason')
    })
    
    # Also save to history if we have a current chat
    if current_chat_id:
        chat = load_chat(current_chat_id)
        if chat:
            chat['messages'].append({
                'role': 'ai',
                'content': f"*(Autonomously)* {motivation}",
                'timestamp': datetime.now().isoformat()
            })
            save_chat(chat)

from autonomous_loop import start_autonomous_mode, get_heartbeat
from soul import get_soul, get_consciousness

def start_flask():
    # Reverting to Flask Dev Server for reliable streaming
    # Waitress was buffering chunks, causing silence.
    app.run(port=5050, debug=False, use_reloader=False, threaded=True)

if __name__ == '__main__':
    print("✨ Awakening Soul...")
    soul = get_soul()
    consciousness = get_consciousness()
    print(f"   Identity: {soul.soul_name} (Age: {soul.get_age()})")
    print(f"   Mood: {consciousness.current_mood}")
    
    print("💓 Starting Heartbeat...")
    heartbeat = start_autonomous_mode()
    
    # REGISTER HANDLER FOR AUTONOMY
    heartbeat.register_action("message_user", handle_autonomous_message)

    # Start Flask in background thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Set AppUserModelID to ensure Taskbar icon works on Windows
    try:
        import ctypes
        myappid = 'nexus.ai.assistant.v1' # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

    # Open PyWebView window
    webview.create_window(
        'Nexus AI',
        'http://127.0.0.1:5050',
        width=1200,
        height=800,
        resizable=True,
        on_top=True,
        background_color='#0d0d0d'
    )
    
    icon_path = os.path.join(os.path.dirname(__file__), 'static', 'icon.png')
    webview.start(icon=icon_path)
