import threading
import re
import customtkinter as ctk
from AIassistant import NexusBrain

# Setup Theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class ChatBubble(ctk.CTkFrame):
    """A styled chat bubble widget"""
    def __init__(self, parent, message, is_user=True, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Colors
        if is_user:
            bg_color = "#1F6AA5"  # Blue for user
            text_color = "#FFFFFF"
            self.configure(fg_color="transparent")
        else:
            bg_color = "#2D2D2D"  # Dark gray for AI
            text_color = "#E8E8E8"
            self.configure(fg_color="transparent")
        
        # Bubble Container
        self.bubble = ctk.CTkFrame(
            self,
            fg_color=bg_color,
            corner_radius=15
        )
        
        # Text inside bubble
        self.text_label = ctk.CTkLabel(
            self.bubble,
            text=message,
            text_color=text_color,
            wraplength=350,
            justify="left" if not is_user else "right",
            anchor="w" if not is_user else "e",
            font=("Segoe UI", 13),
            padx=12,
            pady=8
        )
        self.text_label.pack(padx=5, pady=5)
        
        # Align bubble
        if is_user:
            self.bubble.pack(side="right", padx=(50, 10), pady=3)
        else:
            self.bubble.pack(side="left", padx=(10, 50), pady=3)


class SidebarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Nexus AI")
        self.geometry("450x750+1450+50")
        self.resizable(True, True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#121212")  # Very dark background

        # Initialize Brain
        self.brain = NexusBrain()

        # Layout
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Chat
        self.grid_rowconfigure(2, weight=0)  # Input
        self.grid_columnconfigure(0, weight=1)

        # Header
        self.header = ctk.CTkFrame(self, fg_color="#1a1a1a", height=50, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        
        self.title_label = ctk.CTkLabel(
            self.header,
            text="🤖 Nexus AI",
            font=("Segoe UI", 18, "bold"),
            text_color="#3B8ED0"
        )
        self.title_label.pack(pady=12)

        # Chat Area (Scrollable)
        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#121212",
            scrollbar_button_color="#333333",
            scrollbar_button_hover_color="#444444"
        )
        self.chat_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Input Area
        self.input_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=0)
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)

        self.input_container = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.input_container.pack(fill="x", padx=15, pady=15)

        self.input_entry = ctk.CTkEntry(
            self.input_container,
            placeholder_text="Message Nexus...",
            height=45,
            corner_radius=22,
            border_width=0,
            fg_color="#2B2B2B",
            font=("Segoe UI", 13)
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.send_btn = ctk.CTkButton(
            self.input_container,
            text="➤",
            width=45,
            height=45,
            corner_radius=22,
            fg_color="#1F6AA5",
            hover_color="#144870",
            font=("Segoe UI", 16),
            command=self.send_message
        )
        self.send_btn.pack(side="right")

        self.input_entry.bind("<Return>", self.send_message)
        self.is_thinking = False
        self.thinking_bubble = None

    def clean_markdown(self, text):
        """Convert markdown to clean readable text"""
        import re
        
        # Remove HTML tags like <br>
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Convert **bold** to UPPERCASE for emphasis
        text = re.sub(r'\*\*(.+?)\*\*', lambda m: m.group(1).upper(), text)
        
        # Convert *italic* to just text
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        
        # Convert headers to clean text with decoration
        text = re.sub(r'^#{1,2}\s*(.+)$', r'━━ \1 ━━', text, flags=re.MULTILINE)
        text = re.sub(r'^#{3,6}\s*(.+)$', r'• \1', text, flags=re.MULTILINE)
        
        # Convert markdown tables to clean format
        lines = text.split('\n')
        cleaned_lines = []
        in_table = False
        
        for line in lines:
            # Skip separator lines (|---|---|)
            if re.match(r'^\s*\|[-:\s|]+\|\s*$', line):
                continue
            
            # Convert table rows to bullet points
            if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
                # Extract cells
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if cells:
                    # First row might be header
                    if not in_table:
                        cleaned_lines.append('• ' + ' → '.join(cells))
                        in_table = True
                    else:
                        cleaned_lines.append('  › ' + ' | '.join(cells))
            else:
                in_table = False
                cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Clean up bullet points
        text = re.sub(r'^[-*]\s+', '• ', text, flags=re.MULTILINE)
        
        return text.strip()

    def add_message(self, message, is_user=True):
        if not is_user:
            message = self.clean_markdown(message)
        
        bubble = ChatBubble(self.chat_frame, message, is_user=is_user)
        bubble.pack(fill="x", pady=2)
        
        # Auto-scroll to bottom
        self.chat_frame._parent_canvas.yview_moveto(1.0)
        
        return bubble

    def send_message(self, event=None):
        user_text = self.input_entry.get().strip()
        if not user_text:
            return

        # Add User Message (Right side, Blue)
        self.add_message(user_text, is_user=True)
        self.input_entry.delete(0, "end")

        # Add Thinking Placeholder (Left side, Gray)
        self.thinking_bubble = self.add_message("Thinking...", is_user=False)
        self.is_thinking = True
        self.dot_count = 0
        
        # Start animation and AI processing
        self.animate_thinking()
        threading.Thread(target=self.process_ai, args=(user_text,), daemon=True).start()

    def animate_thinking(self):
        if self.is_thinking and self.thinking_bubble:
            self.dot_count = (self.dot_count + 1) % 4
            text = "Thinking" + "." * self.dot_count
            self.thinking_bubble.text_label.configure(text=text)
            self.after(400, self.animate_thinking)

    def process_ai(self, user_text):
        try:
            response = self.brain.get_response(user_text)
        except Exception as e:
            response = f"Error: {str(e)}"

        self.is_thinking = False

        def update_ui():
            # Remove thinking bubble
            if self.thinking_bubble:
                self.thinking_bubble.destroy()
                self.thinking_bubble = None
            
            # Add real AI response (Left side, Gray)
            self.add_message(response, is_user=False)

        self.after(0, update_ui)


if __name__ == "__main__":
    app = SidebarApp()
    app.mainloop()