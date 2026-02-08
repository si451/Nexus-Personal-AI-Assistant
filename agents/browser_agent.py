"""
Browser Subagent
================
Controls a real Chromium browser using Playwright (Sync API).
Keeps a persistent context for logins/cookies.
"""
import time
import threading
import os
from playwright.sync_api import sync_playwright
from soul.subconscious import get_subconscious, EventPriority

class BrowserAgent:
    def __init__(self):
        self.output_bus = get_subconscious()
        self.running = False
        self.thread = None
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Persistent storage for cookies/state
        self.user_data_dir = os.path.join(os.getcwd(), 'data', 'browser_context')
        os.makedirs(self.user_data_dir, exist_ok=True)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[BrowserAgent] Started")

    def stop(self):
        self.running = False
        if self.thread:
             self.thread.join(timeout=2)
        self._close_browser()

    def _close_browser(self):
        try:
            if self.context: self.context.close()
            if self.playwright: self.playwright.stop()
        except:
             pass
        self.page = None
        self.context = None
        self.playwright = None

    def _ensure_browser(self):
        if self.page: return
        
        try:
            self.playwright = sync_playwright().start()
            # Launch persistent context
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=False, # Visible for now so user sees action
                args=["--start-maximized"],
                no_viewport=True
            )
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            print("[BrowserAgent] Browser Launched")
        except Exception as e:
            print(f"[BrowserAgent] Launch Failed: {e}")

    # --- Actions exposed to Tools ---
    
    def navigate(self, url):
        self._ensure_browser()
        if not self.page: return "Error: Browser failed to launch (check executable)."
        try:
            self.page.goto(url)
            self._publish_state()
            return f"Navigated to {url}"
        except Exception as e:
            return f"Error: {e}"

    def click(self, selector):
        self._ensure_browser()
        if not self.page: return "Error: Browser failed to launch."
        try:
            self.page.click(selector, timeout=2000)
            return f"Clicked {selector}"
        except Exception as e:
            return f"Error clicking {selector}: {e}"

    def type_text(self, selector, text):
        self._ensure_browser()
        if not self.page: return "Error: Browser failed to launch."
        try:
            self.page.fill(selector, text, timeout=2000)
            return f"Typed into {selector}"
        except Exception as e:
            return f"Error typing: {e}"

    def read_page(self):
        self._ensure_browser()
        if not self.page: return "Error: Browser failed to launch."
        try:
            title = self.page.title()
            content = self.page.evaluate("document.body.innerText")
            return f"Title: {title}\n\nContent:\n{content[:1000]}..."
        except Exception as e:
            return f"Error reading: {e}"
            
    def screenshot(self):
        self._ensure_browser()
        try:
            path = os.path.join("data", "browser_screenshot.png")
            self.page.screenshot(path=path)
            return path
        except:
            return None

    def _publish_state(self):
        try:
            title = self.page.title()
            url = self.page.url
            self.output_bus.publish("browser", "BROWSER_NAVIGATED", {
                "title": title,
                "url": url
            }, EventPriority.NORMAL)
        except:
            pass

    def _loop(self):
        # Keep alive loop
        while self.running:
            time.sleep(1)

# Singleton
_browser_agent = None
def get_browser_agent():
    global _browser_agent
    if _browser_agent is None:
        _browser_agent = BrowserAgent()
    return _browser_agent
