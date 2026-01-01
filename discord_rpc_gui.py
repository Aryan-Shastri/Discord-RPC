import customtkinter as ctk
from pypresence import Presence
import time
import threading
import json
import tkinter as tk
from tkinter import filedialog
from urllib.parse import urlparse
from datetime import datetime, date
import webbrowser
import platform
import os
import sys

# Platform Logic
SYSTEM_OS = platform.system()
if SYSTEM_OS == "Windows":
    import winreg

from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

class DiscordRPCApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Custom Discord RPC")
        self.geometry("700x850") # Increased height
        self.resizable(False, False)

        self.RPC = None
        self.running = False
        self.start_time = None # For "Elapsed" mode

        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Menu Bar ---
        self.menu_frame = ctk.CTkFrame(self, height=30)
        self.menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 10))
        
        self.btn_save = ctk.CTkButton(self.menu_frame, text="Save Preset", width=100, command=self.save_preset, fg_color="#444")
        self.btn_save.pack(side="left", padx=10, pady=5)
        
        self.btn_load = ctk.CTkButton(self.menu_frame, text="Load Preset", width=100, command=self.load_preset, fg_color="#444")
        self.btn_load.pack(side="left", padx=10, pady=5)

        # --- Tab View ---
        self.tabview = ctk.CTkTabview(self, width=650, height=500)
        self.tabview.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        
        # Create Tabs
        self.tab_general = self.tabview.add("General")
        self.tab_images = self.tabview.add("Images")
        self.tab_buttons = self.tabview.add("Buttons")
        self.tab_advanced = self.tabview.add("Advanced")

        # Configure Grids for Tabs
        self.tab_general.grid_columnconfigure(1, weight=1)
        self.tab_images.grid_columnconfigure(1, weight=1)
        self.tab_buttons.grid_columnconfigure(1, weight=1)
        self.tab_advanced.grid_columnconfigure(1, weight=1)

        # --- Tab: General ---
        # Application ID
        self.lbl_app_id = ctk.CTkLabel(self.tab_general, text="Application ID (Client ID):")
        self.lbl_app_id.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_app_id = ctk.CTkEntry(self.tab_general, placeholder_text="Enter your App ID here")
        self.entry_app_id.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Activity Type
        self.lbl_type = ctk.CTkLabel(self.tab_general, text="Activity Type:")
        self.lbl_type.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.type_var = ctk.StringVar(value="Playing")
        self.opt_type = ctk.CTkComboBox(self.tab_general, values=["Playing", "Listening", "Watching", "Competing"], variable=self.type_var)
        self.opt_type.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Details
        self.lbl_details = ctk.CTkLabel(self.tab_general, text="Details:")
        self.lbl_details.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.entry_details = ctk.CTkEntry(self.tab_general, placeholder_text="Line 1 of your status")
        self.entry_details.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # State
        self.lbl_state = ctk.CTkLabel(self.tab_general, text="State:")
        self.lbl_state.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.entry_state = ctk.CTkEntry(self.tab_general, placeholder_text="Line 2 of your status")
        self.entry_state.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # Auto-Features (New Row)
        self.chk_autoconnect_var = ctk.BooleanVar(value=False)
        self.chk_autoconnect = ctk.CTkCheckBox(self.tab_general, text="Auto Connect on Launch", variable=self.chk_autoconnect_var, command=self.save_last_config)
        self.chk_autoconnect.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.chk_autostart_var = ctk.BooleanVar(value=False)
        self.chk_autostart = ctk.CTkCheckBox(self.tab_general, text="Run on Startup", variable=self.chk_autostart_var, command=self.toggle_autostart)
        self.chk_autostart.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        # --- Tab: Images ---
        # Large Image
        self.lbl_large_image = ctk.CTkLabel(self.tab_images, text="Large Image Key (or URL):")
        self.lbl_large_image.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_large_image = ctk.CTkEntry(self.tab_images, placeholder_text="Key of the large asset")
        self.entry_large_image.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.lbl_large_text = ctk.CTkLabel(self.tab_images, text="Large Image Text:")
        self.lbl_large_text.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_large_text = ctk.CTkEntry(self.tab_images, placeholder_text="Tooltip for large image")
        self.entry_large_text.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Small Image
        self.lbl_small_image = ctk.CTkLabel(self.tab_images, text="Small Image Key (or URL):")
        self.lbl_small_image.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.entry_small_image = ctk.CTkEntry(self.tab_images, placeholder_text="Key of the small asset")
        self.entry_small_image.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.lbl_small_text = ctk.CTkLabel(self.tab_images, text="Small Image Text:")
        self.lbl_small_text.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.entry_small_text = ctk.CTkEntry(self.tab_images, placeholder_text="Tooltip for small image")
        self.entry_small_text.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # --- Tab: Buttons ---
        # Button 1
        self.lbl_btn1_label = ctk.CTkLabel(self.tab_buttons, text="Button 1 Label:")
        self.lbl_btn1_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_btn1_label = ctk.CTkEntry(self.tab_buttons, placeholder_text="Text for button 1")
        self.entry_btn1_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.lbl_btn1_url = ctk.CTkLabel(self.tab_buttons, text="Button 1 URL:")
        self.lbl_btn1_url.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_btn1_url = ctk.CTkEntry(self.tab_buttons, placeholder_text="URL for button 1")
        self.entry_btn1_url.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Button 2
        self.lbl_btn2_label = ctk.CTkLabel(self.tab_buttons, text="Button 2 Label:")
        self.lbl_btn2_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.entry_btn2_label = ctk.CTkEntry(self.tab_buttons, placeholder_text="Text for button 2")
        self.entry_btn2_label.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.lbl_btn2_url = ctk.CTkLabel(self.tab_buttons, text="Button 2 URL:")
        self.lbl_btn2_url.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.entry_btn2_url = ctk.CTkEntry(self.tab_buttons, placeholder_text="URL for button 2")
        self.entry_btn2_url.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # --- Tab: Advanced ---
        # Party Size
        self.lbl_party = ctk.CTkLabel(self.tab_advanced, text="Party Size (Current / Max):")
        self.lbl_party.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.party_frame = ctk.CTkFrame(self.tab_advanced, fg_color="transparent")
        self.party_frame.grid(row=0, column=1, padx=10, pady=10, sticky="w") # Changed sticky to w for better look
        
        self.entry_party_current = ctk.CTkEntry(self.party_frame, placeholder_text="1", width=60)
        self.entry_party_current.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(self.party_frame, text="/").pack(side="left")
        
        self.entry_party_max = ctk.CTkEntry(self.party_frame, placeholder_text="5", width=60)
        self.entry_party_max.pack(side="left", padx=(5, 0))

        # Timestamp Options
        self.lbl_timestamp = ctk.CTkLabel(self.tab_advanced, text="Timestamp:")
        self.lbl_timestamp.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.timestamp_option = ctk.CTkComboBox(self.tab_advanced, values=["None", "Time Elapsed", "Local Time (12h)", "Local Time (24h)"])
        self.timestamp_option.set("Time Elapsed")
        self.timestamp_option.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Control Buttons
        self.btn_connect = ctk.CTkButton(self, text="Connect", command=self.connect_rpc, fg_color="green")
        self.btn_connect.grid(row=15, column=0, padx=20, pady=20, sticky="ew")

        self.btn_update = ctk.CTkButton(self, text="Update Presence", command=self.update_presence, state="disabled")
        self.btn_update.grid(row=15, column=1, padx=20, pady=20, sticky="ew")
        
        self.btn_disconnect = ctk.CTkButton(self, text="Disconnect", command=self.disconnect_rpc, fg_color="red", state="disabled")
        self.btn_disconnect.grid(row=16, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        self.lbl_warning = ctk.CTkLabel(self, text="Note: You cannot see your own buttons!", text_color="orange", font=("Arial", 12))
        self.lbl_warning.grid(row=17, column=0, columnspan=2, padx=20, pady=(0, 5))

        self.status_label = ctk.CTkLabel(self, text="Status: Disconnected", text_color="gray")
        self.status_label.grid(row=18, column=0, columnspan=2, padx=20, pady=5)

        # Tray setup
        self.protocol("WM_DELETE_WINDOW", self.withdraw_window)
        
        # Start Minimized Check
        # If launched with specific arg or just check config later?
        # Ideally we check config immediately. But config load happens later?
        # Let's move load_last_config earlier or check it.
        # Actually, let's just initialize tray thread now.
        
        # Auto-load last config
        self.load_last_config()

    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color=(30, 30, 30))
        d = ImageDraw.Draw(image)
        d.rectangle((16, 16, 48, 48), fill=(88, 101, 242)) # Discord Blurple
        # d.text removed to avoid dependency on fonts
        
        menu = pystray.Menu(
            item('Open', self.show_window, default=True),
            item('Quit', self.quit_app)
        )
        self.tray_icon = pystray.Icon("DiscordRPC", image, "Discord RPC", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def withdraw_window(self):
        self.withdraw()
        if not hasattr(self, 'tray_icon'):
            self.create_tray_icon()
        
        # Notification (Optional, maybe skip for now to avoid complexity)
        # self.tray_icon.notify("App minimized to tray.", "Discord RPC")

    def show_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def quit_app(self):
        self.tray_icon.stop()
        self.running = False
        self.destroy() # Close tkinter
        sys.exit()

    def validate_url(self, url):
        if not url: return None
        if not url.startswith(('http://', 'https://')):
            return 'https://' + url
        return url

    def save_last_config(self):
        """Saves current fields to config.json automatically"""
        data = {
            "app_id": self.entry_app_id.get(),
            "type": self.type_var.get(),
            "details": self.entry_details.get(),
            "state": self.entry_state.get(),
            "large_image": self.entry_large_image.get(),
            "large_text": self.entry_large_text.get(),
            "small_image": self.entry_small_image.get(),
            "small_text": self.entry_small_text.get(),
            "btn1_label": self.entry_btn1_label.get(),
            "btn1_url": self.entry_btn1_url.get(),
            "btn2_label": self.entry_btn2_label.get(),
            "btn2_url": self.entry_btn2_url.get(),
            "timestamp_mode": self.timestamp_option.get(),
            "party_current": self.entry_party_current.get(),
            "party_max": self.entry_party_max.get(),
            "auto_connect": self.chk_autoconnect_var.get(),
            "run_on_startup": self.chk_autostart_var.get()
        }
        try:
            with open("config.json", 'w') as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass # Silent fail for auto-save

    def load_last_config(self):
        """Loads from config.json if exists"""
        try:
            with open("config.json", 'r') as f:
                data = json.load(f)
            
            self.entry_app_id.delete(0, tk.END); self.entry_app_id.insert(0, data.get("app_id", ""))
            self.type_var.set(data.get("type", "Playing"))
            self.entry_details.delete(0, tk.END); self.entry_details.insert(0, data.get("details", ""))
            self.entry_state.delete(0, tk.END); self.entry_state.insert(0, data.get("state", ""))
            self.entry_large_image.delete(0, tk.END); self.entry_large_image.insert(0, data.get("large_image", ""))
            self.entry_large_text.delete(0, tk.END); self.entry_large_text.insert(0, data.get("large_text", ""))
            self.entry_small_image.delete(0, tk.END); self.entry_small_image.insert(0, data.get("small_image", ""))
            self.entry_small_text.delete(0, tk.END); self.entry_small_text.insert(0, data.get("small_text", ""))
            self.entry_btn1_label.delete(0, tk.END); self.entry_btn1_label.insert(0, data.get("btn1_label", ""))
            self.entry_btn1_url.delete(0, tk.END); self.entry_btn1_url.insert(0, data.get("btn1_url", ""))
            self.entry_btn2_label.delete(0, tk.END); self.entry_btn2_label.insert(0, data.get("btn2_label", ""))
            self.entry_btn2_url.delete(0, tk.END); self.entry_btn2_url.insert(0, data.get("btn2_url", ""))
            
            self.timestamp_option.set(data.get("timestamp_mode", "Time Elapsed"))
            self.entry_party_current.delete(0, tk.END); self.entry_party_current.insert(0, data.get("party_current", ""))
            self.entry_party_max.delete(0, tk.END); self.entry_party_max.insert(0, data.get("party_max", ""))

            # Auto-Features
            self.chk_autoconnect_var.set(data.get("auto_connect", False))
            self.chk_autostart_var.set(data.get("run_on_startup", False))
            
            # Check for autostart sync (just in case external change)
            # self.toggle_autostart() # Don't recursive call, just set var.

            if self.chk_autoconnect_var.get():
                self.after(1500, self.connect_rpc)
            
            # Start Minimized Logic
            # If "Run on Startup" is checked, we assume the user MIGHT have started from startup.
            # But we only want to start minimized if it WAS from startup.
            # The Registry approach usually adds arguments.
            # Let's check sys.argv for "--minimized"
            if "--minimized" in sys.argv:
                self.withdraw_window()

        except FileNotFoundError:
            pass

        except FileNotFoundError:
            pass
        except Exception:
            pass
            
    def toggle_autostart(self):
        """Adds or removes the app from system startup"""
        enable = self.chk_autostart_var.get()
        self.save_last_config() # Save state
        
        if getattr(sys, 'frozen', False):
            app_path = sys.executable
        else:
            app_path = os.path.abspath(sys.argv[0])
        
        # Add "--minimized" argument for startup
        cmd = f'"{app_path}" --minimized'
        # For non-frozen python scripts we need python exe
        if not getattr(sys, 'frozen', False):
             # This is tricky without full path to python. 
             # We assume user uses exe for this feature.
             pass

        try:
            if SYSTEM_OS == "Windows":
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
                if enable:
                    winreg.SetValueEx(key, "DiscordRPC_GUI", 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(key, "DiscordRPC_GUI")
                    except FileNotFoundError:
                        pass
                winreg.CloseKey(key)
                
            elif SYSTEM_OS == "Linux":
                autostart_dir = os.path.expanduser("~/.config/autostart")
                os.makedirs(autostart_dir, exist_ok=True)
                desktop_file = os.path.join(autostart_dir, "discord_rpc_gui.desktop")
                
                if enable:
                    content = f"""[Desktop Entry]
Type=Application
Name=Custom Discord RPC
Exec={cmd}
Terminal=false
Hidden=true
"""

                    with open(desktop_file, "w") as f:
                        f.write(content)
                else:
                    if os.path.exists(desktop_file):
                        os.remove(desktop_file)
                        
            print(f"Debug: Autostart set to {enable}")
            
        except Exception as e:
            print(f"Error setting autostart: {e}")
            self.status_label.configure(text=f"Autostart Error: {e}", text_color="red")


    def save_preset(self):
        # ... existing save_preset code ...
        pass # Placeholder to indicate I am not deleting save_preset, just checking context

    # (Actually I need to match the context exactly to avoid deleting save_preset)
    # Re-writing code block with correct context:

    def save_preset(self):
        data = {
            "app_id": self.entry_app_id.get(),
            "type": self.type_var.get(),
            "details": self.entry_details.get(),
            "state": self.entry_state.get(),
            "large_image": self.entry_large_image.get(),
            "large_text": self.entry_large_text.get(),
            "small_image": self.entry_small_image.get(),
            "small_text": self.entry_small_text.get(),
            "btn1_label": self.entry_btn1_label.get(),
            "btn1_url": self.entry_btn1_url.get(),
            "btn2_label": self.entry_btn2_label.get(),
            "btn2_url": self.entry_btn2_url.get(),
            "timestamp_mode": self.timestamp_option.get(),
            "party_current": self.entry_party_current.get(),
            "party_max": self.entry_party_max.get()
        }
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
                self.status_label.configure(text="Preset Saved!", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"Save Error: {e}", text_color="red")

    def load_preset(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                self.entry_app_id.delete(0, tk.END); self.entry_app_id.insert(0, data.get("app_id", ""))
                self.type_var.set(data.get("type", "Playing"))
                self.entry_details.delete(0, tk.END); self.entry_details.insert(0, data.get("details", ""))
                self.entry_state.delete(0, tk.END); self.entry_state.insert(0, data.get("state", ""))
                self.entry_large_image.delete(0, tk.END); self.entry_large_image.insert(0, data.get("large_image", ""))
                self.entry_large_text.delete(0, tk.END); self.entry_large_text.insert(0, data.get("large_text", ""))
                self.entry_small_image.delete(0, tk.END); self.entry_small_image.insert(0, data.get("small_image", ""))
                self.entry_small_text.delete(0, tk.END); self.entry_small_text.insert(0, data.get("small_text", ""))
                self.entry_btn1_label.delete(0, tk.END); self.entry_btn1_label.insert(0, data.get("btn1_label", ""))
                self.entry_btn1_url.delete(0, tk.END); self.entry_btn1_url.insert(0, data.get("btn1_url", ""))
                self.entry_btn2_label.delete(0, tk.END); self.entry_btn2_label.insert(0, data.get("btn2_label", ""))
                self.entry_btn2_url.delete(0, tk.END); self.entry_btn2_url.insert(0, data.get("btn2_url", ""))
                
                self.timestamp_option.set(data.get("timestamp_mode", "Time Elapsed"))
                self.entry_party_current.delete(0, tk.END); self.entry_party_current.insert(0, data.get("party_current", ""))
                self.entry_party_max.delete(0, tk.END); self.entry_party_max.insert(0, data.get("party_max", ""))

                self.status_label.configure(text="Preset Loaded!", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"Load Error: {e}", text_color="red")

    def connect_rpc(self):
        client_id = self.entry_app_id.get().strip()
        if not client_id:
            self.status_label.configure(text="Status: Please enter a Client ID!", text_color="red")
            return

        self.status_label.configure(text="Status: Connecting...", text_color="orange")
        self.btn_connect.configure(state="disabled")
        
        threading.Thread(target=self._connect_thread, args=(client_id,), daemon=True).start()

    def _connect_thread(self, client_id):
        try:
            self.RPC = Presence(client_id)
            self.RPC.connect()
            self.running = True
            self.start_time = time.time() # Track start time of connection
            self.after(0, lambda: self._on_connect_success())
        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: self._on_connect_fail(err_msg))

    def _on_connect_success(self):
        self.status_label.configure(text="Status: Connected!", text_color="green")
        self.btn_connect.configure(state="disabled")
        self.btn_update.configure(state="normal")
        self.btn_disconnect.configure(state="normal")
        self.entry_app_id.configure(state="disabled")

    def _on_connect_fail(self, error_message):
        self.status_label.configure(text=f"Error: {error_message}", text_color="red")
        self.btn_connect.configure(state="normal")

    def update_presence(self):
        if not self.RPC or not self.running:
            return
        threading.Thread(target=self._update_thread, daemon=True).start()

    def _update_thread(self):
        try:
            details = self.entry_details.get() or None
            state = self.entry_state.get() or None
            large_image = self.entry_large_image.get().strip().lower() or None
            large_text = self.entry_large_text.get().strip() or None
            small_image = self.entry_small_image.get().strip().lower() or None
            small_text = self.entry_small_text.get().strip() or None
            
            # Button Validation
            btn1_url = self.validate_url(self.entry_btn1_url.get())
            btn2_url = self.validate_url(self.entry_btn2_url.get())

            buttons = []
            if self.entry_btn1_label.get() and btn1_url:
                buttons.append({"label": self.entry_btn1_label.get(), "url": btn1_url})
            if self.entry_btn2_label.get() and btn2_url:
                buttons.append({"label": self.entry_btn2_label.get(), "url": btn2_url})
            
            if not buttons: 
                buttons = None
            
            # Activity Type
            activity_map = {"Playing": 0, "Streaming": 1, "Listening": 2, "Watching": 3, "Competing": 5}
            act_type_int = activity_map.get(self.type_var.get(), 0)
            from pypresence import ActivityType
            act_type = ActivityType(act_type_int)

            # Timestamp Logic
            timestamp_mode = self.timestamp_option.get()
            start = None
            if timestamp_mode == "Time Elapsed":
                start = self.start_time or time.time()
            elif "Local Time" in timestamp_mode:
                now = datetime.now()
                midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
                
                if "12h" in timestamp_mode:
                    if now.hour >= 12:
                        # If PM, assume start was Noon (12:00 PM) so elapsed matches 12h clock
                        start = int(midnight.replace(hour=12).timestamp())
                    else:
                        # If AM, start is midnight
                        start = int(midnight.timestamp())
                else:
                    # 24h Mode: Always start midnight
                    start = int(midnight.timestamp())
            
            # Party Size Logic
            party_size = None
            p_curr = self.entry_party_current.get()
            p_max = self.entry_party_max.get()
            if p_curr and p_max:
                try:
                    party_size = [int(p_curr), int(p_max)]
                except ValueError:
                    print("Debug: Invalid party size values")

            self.RPC.update(
                details=details,
                state=state,
                large_image=large_image,
                large_text=large_text,
                small_image=small_image,
                small_text=small_text,
                buttons=buttons,
                start=start,
                party_size=party_size,
                instance=False,
                activity_type=act_type
            )
            
            # Auto-save successful config
            self.save_last_config()
            
            self.after(0, lambda: self.status_label.configure(text="Status: Presence Updated!", text_color="green"))
            
        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: self.status_label.configure(text=f"Error Updating: {err_msg}", text_color="red"))

    def disconnect_rpc(self):
        if self.RPC:
            self.RPC.close()
            self.RPC = None
        
        self.running = False
        self.status_label.configure(text="Status: Disconnected", text_color="gray")
        self.btn_connect.configure(state="normal")
        self.btn_update.configure(state="disabled")
        self.btn_disconnect.configure(state="disabled")
        self.entry_app_id.configure(state="normal")

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    app = DiscordRPCApp()
    app.mainloop()
