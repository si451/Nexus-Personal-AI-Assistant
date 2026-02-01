
import pystray
from PIL import Image, ImageDraw
import threading
import os
import sys
import webview
import time

class NexusTray:
    def __init__(self, app_name="Nexus AI", icon_path=None, on_open=None, on_exit=None):
        self.app_name = app_name
        self.on_open = on_open
        self.on_exit = on_exit
        self.icon_path = icon_path
        self.icon = None
        self.tray_thread = None

    def create_image(self):
        # Generate a default icon if none provided
        if self.icon_path and os.path.exists(self.icon_path):
            return Image.open(self.icon_path)
            
        # Fallback: Blue/Green Circle
        width = 64
        height = 64
        color1 = (0, 128, 255)
        color2 = (255, 255, 255)
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
        dc.rectangle((0, height // 2, width // 2, height), fill=color2)
        return image

    def setup_icon(self):
        menu = pystray.Menu(
            pystray.MenuItem("Open Nexus", self.on_open_clicked, default=True),
            pystray.MenuItem("Stop Autonomy (Exit)", self.on_exit_clicked)
        )
        self.icon = pystray.Icon("nexus_ai", self.create_image(), self.app_name, menu)

    def on_open_clicked(self, icon, item):
        if self.on_open:
            self.on_open()

    def on_exit_clicked(self, icon, item):
        self.icon.stop()
        if self.on_exit:
            self.on_exit()

    def run(self):
        self.setup_icon()
        self.icon.run()

    def run_detached(self):
        # Run tray in separate thread? No, pystray usually needs main thread on some OS.
        # We will design the main app to run pystray in main thread.
        pass

if __name__ == "__main__":
    # Test
    def open_app(): print("Open!")
    def exit_app(): print("Exit!")
    tray = NexusTray(on_open=open_app, on_exit=exit_app)
    tray.run()
