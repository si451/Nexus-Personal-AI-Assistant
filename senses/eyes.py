"""
Nexus Vision System v3.0 (The All-Seeing Eye)
==============================================
DESIGN PHILOSOPHY:
- EasyOCR is the PRIMARY vision source (DeepSeek doesn't support images)
- Rich context extraction from OCR text (YouTube titles, code, URLs)
- Window detection for application awareness
- NO dependency on LLM image analysis

Features:
- GPU-accelerated OCR (EasyOCR)
- Smart text parsing (extract URLs, titles, code)
- Complete window listing
- Activity inference from screen content
"""

import threading
import time
import base64
import io
import re
import hashlib
from datetime import datetime
from pathlib import Path

# Screen Capture
import mss
import cv2
import numpy as np
from PIL import Image

# Window Detection
import win32gui
import win32process
import psutil
try:
    import pygetwindow as gw
except ImportError:
    gw = None

# Modern OCR (EasyOCR with GPU)
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# Nexus Integration
from memory.brain_limbic import NexusMemory


class NexusEyes:
    """
    Vision System v3.0 - EasyOCR-Centric Design
    
    This version relies primarily on OCR text extraction to understand
    screen content, since the LLM (DeepSeek) doesn't support image input.
    """
    
    def __init__(self, memory_system: NexusMemory = None, llm=None):
        self.running = False
        self.memory = memory_system if memory_system else NexusMemory()
        self.ocr_lock = threading.Lock()
        
        # Configuration
        self.capture_interval = 15
        
        # Storage
        self.screenshots_dir = Path("memory/visual_cortex")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # LLM reference (kept for future multimodal support)
        self.llm = llm
        
        # EasyOCR Reader (GPU-accelerated)
        self.ocr_reader = None
        if EASYOCR_AVAILABLE:
            print("[Eyes] Initializing EasyOCR with GPU...")
            try:
                self.ocr_reader = easyocr.Reader(['en'], gpu=True, verbose=False)
                print("[Eyes] ✓ EasyOCR Ready (GPU Mode)")
            except Exception as e:
                print(f"[Eyes] GPU failed, trying CPU: {e}")
                try:
                    self.ocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                    print("[Eyes] ✓ EasyOCR Ready (CPU Mode)")
                except Exception as e2:
                    print(f"[Eyes] ✗ EasyOCR failed: {e2}")
        else:
            print("[Eyes] ⚠ EasyOCR not available")
        
        # State tracking
        self.last_screenshot_hash = None
        self.last_analysis_time = 0
        self.last_context = {}

    # ==================== WINDOW DETECTION ====================
    
    def get_active_window(self) -> dict:
        """Get detailed info about the currently focused window."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            app_name = "Unknown"
            try:
                proc = psutil.Process(pid)
                app_name = proc.name()
            except:
                pass
            
            # Infer application type from title/process
            app_type = self._classify_window(title, app_name)
            
            return {
                "title": title,
                "app": app_name,
                "type": app_type,
                "hwnd": hwnd
            }
        except:
            return {"title": "Unknown", "app": "Unknown", "type": "unknown", "hwnd": None}

    def get_all_windows(self) -> list:
        """Get list of all visible windows with classification."""
        windows = []
        
        if gw:
            try:
                all_windows = gw.getAllWindows()
                for w in all_windows:
                    if w.title and w.visible and w.width > 100 and w.height > 100:
                        app_type = self._classify_window(w.title, "")
                        windows.append({
                            "title": w.title[:80],
                            "type": app_type,
                            "size": f"{w.width}x{w.height}"
                        })
            except Exception as e:
                print(f"[Eyes] pygetwindow error: {e}")
        
        # Fallback enumeration
        if not windows:
            def enum_handler(hwnd, ctx):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title and len(title) > 2:
                        windows.append({"title": title[:80], "type": "unknown"})
            try:
                win32gui.EnumWindows(enum_handler, None)
            except:
                pass
        
        return windows[:12]
    
    def _classify_window(self, title: str, app: str) -> str:
        """Classify window type for better context understanding."""
        title_lower = title.lower()
        app_lower = app.lower()
        
        # Media
        if any(x in title_lower for x in ['youtube', 'netflix', 'spotify', 'vlc', 'video']):
            return "media"
        # Browser
        if any(x in app_lower for x in ['chrome', 'firefox', 'edge', 'brave']):
            return "browser"
        # Development
        if any(x in title_lower for x in ['.py', '.js', '.ts', '.html', '.css', 'code', 'visual studio', 'pycharm']):
            return "development"
        # Communication
        if any(x in title_lower for x in ['whatsapp', 'discord', 'telegram', 'slack', 'teams']):
            return "communication"
        # Documents
        if any(x in title_lower for x in ['word', 'excel', 'powerpoint', '.pdf', '.docx']):
            return "documents"
        # Terminal
        if any(x in title_lower for x in ['terminal', 'powershell', 'cmd', 'bash']):
            return "terminal"
        
        return "application"

    # ==================== SCREEN CAPTURE ====================
    
    def capture_screen(self) -> Image.Image:
        """Capture the entire primary screen."""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                return img
        except Exception as e:
            print(f"[Eyes] Capture Error: {e}")
            return None

    # ==================== OCR & TEXT ANALYSIS ====================
    
    def extract_text(self, image) -> str:
        """Extract all text from screen using EasyOCR."""
        if not self.ocr_reader:
            return ""
        
        with self.ocr_lock:
            try:
                if isinstance(image, Image.Image):
                    img_np = np.array(image)
                else:
                    img_np = image
                
                results = self.ocr_reader.readtext(img_np, detail=0, paragraph=True)
                return " ".join(results)
            except Exception as e:
                print(f"[Eyes] OCR Error: {e}")
                return ""
    
    def analyze_text_content(self, text: str, active_window: dict) -> dict:
        """Intelligently analyze OCR text to extract meaningful information."""
        analysis = {
            "urls": [],
            "youtube_video": None,
            "code_detected": False,
            "file_paths": [],
            "keywords": [],
            "summary": ""
        }
        
        if not text:
            return analysis
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, text)
        analysis["urls"] = urls[:3]  # Top 3 URLs
        
        # Detect YouTube content
        if "youtube" in active_window.get('title', '').lower():
            # Try to extract video title from window title
            yt_title = active_window.get('title', '')
            if ' - YouTube' in yt_title:
                video_title = yt_title.replace(' - YouTube', '').strip()
                analysis["youtube_video"] = video_title
        
        # Detect code patterns
        code_patterns = ['def ', 'class ', 'import ', 'function ', 'const ', 'let ', 'var ', '{', '}', '()', '=>']
        if any(pattern in text for pattern in code_patterns):
            analysis["code_detected"] = True
        
        # Extract file paths (Windows)
        path_pattern = r'[A-Za-z]:\\[^\s<>"*?|]+'
        paths = re.findall(path_pattern, text)
        analysis["file_paths"] = paths[:3]
        
        # Key context words
        context_words = []
        important_words = ['error', 'warning', 'success', 'failed', 'loading', 'downloading', 
                          'playing', 'paused', 'search', 'settings', 'login', 'password']
        for word in important_words:
            if word.lower() in text.lower():
                context_words.append(word)
        analysis["keywords"] = context_words
        
        # Generate summary
        analysis["summary"] = self._generate_context_summary(text, active_window)
        
        return analysis
    
    def _generate_context_summary(self, text: str, window: dict) -> str:
        """Generate a human-readable summary of what's on screen."""
        window_type = window.get('type', 'unknown')
        title = window.get('title', 'Unknown')
        
        if window_type == "media":
            if "youtube" in title.lower():
                # Extract first few words that might be video title
                return f"Watching video on YouTube: {title.split(' - ')[0][:50]}"
            return f"Media playing: {title[:40]}"
        
        elif window_type == "development":
            # Look for file being edited
            if '.py' in title:
                return f"Editing Python file: {title.split(' - ')[0]}"
            elif '.js' in title or '.ts' in title:
                return f"Editing JavaScript/TypeScript: {title.split(' - ')[0]}"
            return f"Coding in: {title[:50]}"
        
        elif window_type == "browser":
            # Try to get page title
            parts = title.split(' - ')
            if len(parts) > 1:
                return f"Browsing: {parts[0][:50]}"
            return f"Web browsing: {title[:50]}"
        
        elif window_type == "communication":
            return f"Messaging on: {title.split(' - ')[0]}"
        
        return f"Using: {title[:50]}"

    # ==================== MAIN INTERFACE ====================
    
    def look_once(self) -> str:
        """
        Primary Vision Method - Returns comprehensive screen analysis.
        This is what the see_screen tool calls.
        """
        print("[Eyes] 👁️ Analyzing screen...")
        
        try:
            # 1. Capture screen
            img = self.capture_screen()
            if not img:
                return "Error: Could not capture screen"
            
            # 2. Get window context
            active_window = self.get_active_window()
            all_windows = self.get_all_windows()
            
            # 3. Extract text via EasyOCR
            start_time = time.time()
            ocr_text = self.extract_text(img)
            ocr_time = time.time() - start_time
            print(f"[Eyes] OCR completed in {ocr_time:.2f}s")
            
            # 4. Analyze content
            analysis = self.analyze_text_content(ocr_text, active_window)
            
            # 5. Build comprehensive report
            report = self._build_report(active_window, all_windows, ocr_text, analysis)
            
            # 6. Cache and store
            self.last_context = {
                "active_window": active_window,
                "windows": all_windows,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in memory
            memory_summary = f"User is {analysis['summary']}. Windows: {', '.join([w['title'][:30] for w in all_windows[:5]])}"
            self.memory.add_memory(memory_summary, type="perception", importance=0.7)
            
            return report
            
        except Exception as e:
            return f"Vision Error: {str(e)}"
    
    def _build_report(self, active: dict, windows: list, ocr_text: str, analysis: dict) -> str:
        """Build a formatted report for the LLM."""
        
        # Window list
        window_list = []
        for i, w in enumerate(windows[:8], 1):
            emoji = {"media": "🎬", "browser": "🌐", "development": "💻", 
                     "communication": "💬", "documents": "📄", "terminal": "⌨️"}.get(w.get('type'), "📱")
            window_list.append(f"{i}. {emoji} {w['title']}")
        
        # Activity summary
        activity = analysis.get('summary', 'Unknown activity')
        
        # Build report
        report = f"""## 👁️ NEXUS VISUAL REPORT

### What You Are Doing
**{activity}**

### Active Window
- **Title:** {active['title']}
- **Application:** {active['app']}
- **Type:** {active['type']}

### All Open Windows ({len(windows)})
{chr(10).join(window_list)}

### Screen Content Detected
"""
        
        # Add specific detections
        if analysis.get('youtube_video'):
            report += f"- 🎬 **YouTube Video:** {analysis['youtube_video']}\n"
        
        if analysis.get('code_detected'):
            report += f"- 💻 **Code detected on screen**\n"
        
        if analysis.get('urls'):
            report += f"- 🔗 **URLs:** {', '.join(analysis['urls'][:2])}\n"
        
        if analysis.get('keywords'):
            report += f"- 🏷️ **Context:** {', '.join(analysis['keywords'])}\n"
        
        # Add OCR excerpt
        if ocr_text:
            excerpt = ocr_text[:400].replace('\n', ' ')
            report += f"\n### Visible Text (Sample)\n```\n{excerpt}...\n```\n"
        
        return report

    def quick_glance(self) -> dict:
        """Fast snapshot without OCR - just window info."""
        try:
            active = self.get_active_window()
            windows = self.get_all_windows()
            
            return {
                "active_window": active['title'],
                "active_app": active['app'],
                "activity_type": active['type'],
                "open_windows": [w['title'] for w in windows],
                "window_count": len(windows),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

    # ==================== BACKGROUND MONITORING ====================
    
    def monitor_loop(self):
        """Background loop for passive screen monitoring."""
        print("[Eyes] 👁️ Vision System Online")
        
        # Tracking state
        current_focus = {"title": "", "start_time": 0}
        
        # Audio System
        from senses.ears import get_ears
        ears = get_ears()
        
        while self.running:
            try:
                time.sleep(2)
                
                now = time.time()
                if now - self.last_analysis_time < self.capture_interval:
                    continue
                
                # Light check - just active window
                active = self.get_active_window()
                title = active.get('title', '')
                
                # Focus Tracking
                if title == current_focus["title"]:
                    duration = now - current_focus["start_time"]
                    
                    # PROACTIVE HELP: If stuck on error/same screen for > 5 mins
                    if duration > 300 and "error" in title.lower():
                        print(f"[Eyes] 🚨 User seems stuck on error: {title}")
                        # Impulse trigger would go here (requires Impulse Engine access)
                        # self.memory.add_memory(f"User stuck on {title} for {int(duration/60)} mins", type="observation")
                        
                else:
                    # Focus changed
                    if current_focus["title"]:
                        duration = now - current_focus["start_time"]
                        if duration > 60:
                            print(f"[Eyes] ⏱️ Spent {int(duration)}s on: {current_focus['title'][:40]}")
                    
                    current_focus = {"title": title, "start_time": now}
                
                # PASSIVE MODE: YouTube/Media
                if active.get('type') == 'media':
                    # Ensure volume is audible if it was low? Or just log.
                    # print(f"[Eyes] 🎬 Enjoying media: {title[:40]}")
                    pass
                
                self.last_analysis_time = now
                
            except Exception as e:
                print(f"[Eyes] Background Error: {e}")
                time.sleep(5)

    def start(self):
        """Start background monitoring."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop background monitoring."""
        self.running = False
        if hasattr(self, 'thread'):
            try:
                self.thread.join(timeout=2)
            except:
                pass


# ==================== TEST ====================

if __name__ == "__main__":
    print("=== NexusEyes v3.0 Test ===\n")
    
    eyes = NexusEyes()
    
    print("[1] Quick Glance:")
    glance = eyes.quick_glance()
    print(f"    Active: {glance.get('active_window', 'N/A')}")
    print(f"    Type: {glance.get('activity_type', 'N/A')}")
    print(f"    Windows: {glance.get('window_count', 0)}")
    
    print("\n[2] Full Vision Report:")
    report = eyes.look_once()
    print(report)
    
    print("\n=== Test Complete ===")
