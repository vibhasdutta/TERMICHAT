# ─────────────────────────────────────────────
# TermiChat Server — Version 1.0
# Author: VibhasDutta
# Date Updated: 2025-06-01
# ─────────────────────────────────────────────
import socket
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import time


class ChatClient:
    def __init__(self):
        self.client = None
        self.connected = False
        self.user_name = ""
        self.server_ip = ""
        self.port = 0
        self.is_admin = False
        self.online_users = []
        self.admin_users = []
        self.banned_users = []
        self.muted_users = []
        self.receiving = False  # Flag to control message receiving
        
        # Initialize GUI
        self.setup_gui()
        self.load_config()
        
    def setup_gui(self):
        # Main window
        self.root = tk.Tk()
        self.root.title("TERMICHAT - Advanced Chat Client")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2c3e50')
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TFrame', background='#2c3e50')
        style.configure('Custom.TButton', background='#3498db', foreground='white')
        style.configure('Custom.TLabel', background='#2c3e50', foreground='white')
        style.configure('Admin.TButton', background='#e74c3c', foreground='white')
        style.configure('Success.TButton', background='#27ae60', foreground='white')
        
        # Main container
        main_container = ttk.Frame(self.root, style='Custom.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create main layout - left panel and right chat area
        self.setup_left_panel(main_container)
        self.setup_right_panel(main_container)
        
    def setup_left_panel(self, parent):
        # Left panel for user lists and controls
        left_panel = ttk.Frame(parent, style='Custom.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Connection status and controls
        status_frame = ttk.Frame(left_panel, style='Custom.TFrame')
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = ttk.Label(status_frame, text="🔴 Disconnected", 
                                     style='Custom.TLabel', font=('Arial', 11, 'bold'))
        self.status_label.pack(anchor=tk.W)
        
        buttons_frame = ttk.Frame(status_frame, style='Custom.TFrame')
        buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.connect_btn = ttk.Button(buttons_frame, text="🔗 Connect", 
                                     command=self.connect_to_server, style='Custom.TButton')
        self.connect_btn.pack(fill=tk.X, pady=1)
        
        self.settings_btn = ttk.Button(buttons_frame, text="⚙️ Settings", 
                                      command=self.show_settings, style='Custom.TButton')
        self.settings_btn.pack(fill=tk.X, pady=1)
        
        self.commands_btn = ttk.Button(buttons_frame, text="📋 Commands", 
                                      command=self.show_commands_window, style='Custom.TButton')
        self.commands_btn.pack(fill=tk.X, pady=1)

        
    def setup_right_panel(self, parent):
        # Right panel for chat
        right_panel = ttk.Frame(parent, style='Custom.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Chat display area
        chat_frame = ttk.Frame(right_panel, style='Custom.TFrame')
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(chat_frame, text="💬 Chat Messages", 
                 style='Custom.TLabel', font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, height=30, width=70, 
            bg='#34495e', fg='white', font=('Consolas', 10),
            state=tk.DISABLED, wrap=tk.WORD
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Configure message type tags
        self.setup_message_tags()
        
        # Message input frame
        input_frame = ttk.Frame(right_panel, style='Custom.TFrame')
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="✉️ Message:", 
                 style='Custom.TLabel', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        message_entry_frame = ttk.Frame(input_frame, style='Custom.TFrame')
        message_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.message_entry = tk.Entry(
            message_entry_frame, font=('Arial', 11), 
            bg='#ecf0f1', fg='#2c3e50'
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.bind('<Return>', self.send_message)
        
        self.send_btn = ttk.Button(message_entry_frame, text="📤 Send", 
                                  command=self.send_message, style='Custom.TButton')
        self.send_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Initially disable input until connected
        self.message_entry.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)
        
    def setup_message_tags(self):
        """Configure text tags for different message types with colors"""
        # System messages (blue)
        self.chat_display.tag_configure("system", foreground="#3498db", font=('Consolas', 10, 'bold'))
        
        # Error messages (red)
        self.chat_display.tag_configure("error", foreground="#e74c3c", font=('Consolas', 10, 'bold'))
        
        # Success messages (green)
        self.chat_display.tag_configure("success", foreground="#27ae60", font=('Consolas', 10, 'bold'))
        
        # Admin messages (purple)
        self.chat_display.tag_configure("admin", foreground="#9b59b6", font=('Consolas', 10, 'bold'))
        
        # Warning messages (orange)
        self.chat_display.tag_configure("warning", foreground="#f39c12", font=('Consolas', 10, 'bold'))
        
        # Private messages (cyan)
        self.chat_display.tag_configure("private", foreground="#1abc9c", font=('Consolas', 10, 'italic'))
        
        # Own messages (light blue)
        self.chat_display.tag_configure("own", foreground="#85c1e9")
        
        # Server announcements (yellow)
        self.chat_display.tag_configure("announcement", foreground="#f1c40f", font=('Consolas', 10, 'bold'))
        
        # Join/Leave messages (gray)
        self.chat_display.tag_configure("join_leave", foreground="#95a5a6", font=('Consolas', 9, 'italic'))
        
    def update_user_lists(self):
        """Update the user list display"""
        self.users_listbox.delete(0, tk.END)
        
        # Add online users with status indicators
        for user in self.online_users:
            status_icon = "👑" if user in self.admin_users else "👤"
            mute_icon = "🔇" if user in self.muted_users else ""
            ban_icon = "🚫" if user in self.banned_users else ""
            
            display_name = f"{status_icon} {user} {mute_icon}{ban_icon}"
            self.users_listbox.insert(tk.END, display_name)
            
            # Color coding
            if user in self.admin_users:
                self.users_listbox.itemconfig(tk.END, {'fg': '#e74c3c'})  # Red for admins
            elif user in self.muted_users:
                self.users_listbox.itemconfig(tk.END, {'fg': '#f39c12'})  # Orange for muted
                
        
    def get_selected_user(self):
        """Get the currently selected user from the list"""
        selection = self.users_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user from the list!")
            return None
            
        selected_item = self.users_listbox.get(selection[0])
        # Extract username from display format "👑 username 🔇🚫"
        username = selected_item.split()[1] if len(selected_item.split()) > 1 else selected_item
        return username
        
    def quick_kick(self):
        user = self.get_selected_user()
        if user and user != self.user_name:
            if messagebox.askyesno("Confirm Kick", f"Kick user '{user}'?"):
                # Find user index in online list
                try:
                    index = self.online_users.index(user)
                    self.send_admin_command("kick", str(index))
                except ValueError:
                    messagebox.showerror("Error", "User not found in online list!")
        elif user == self.user_name:
            messagebox.showwarning("Invalid Action", "You cannot kick yourself!")
            
    def quick_ban(self):
        user = self.get_selected_user()
        if user and user != self.user_name:
            if messagebox.askyesno("Confirm Ban", f"Ban user '{user}'?"):
                try:
                    index = self.online_users.index(user)
                    self.send_admin_command("ban", str(index))
                except ValueError:
                    messagebox.showerror("Error", "User not found in online list!")
        elif user == self.user_name:
            messagebox.showwarning("Invalid Action", "You cannot ban yourself!")
            
    def quick_mute(self):
        user = self.get_selected_user()
        if user and user != self.user_name:
            if messagebox.askyesno("Confirm Mute", f"Mute user '{user}'?"):
                try:
                    index = self.online_users.index(user)
                    self.send_admin_command("mute", str(index))
                except ValueError:
                    messagebox.showerror("Error", "User not found in online list!")
        elif user == self.user_name:
            messagebox.showwarning("Invalid Action", "You cannot mute yourself!")
            
    def quick_unmute(self):
        user = self.get_selected_user()
        if user and user in self.muted_users:
            if messagebox.askyesno("Confirm Unmute", f"Unmute user '{user}'?"):
                try:
                    index = self.muted_users.index(user)
                    self.send_admin_command("unmute", str(index))
                except ValueError:
                    messagebox.showerror("Error", "User not found in muted list!")
        elif user not in self.muted_users:
            messagebox.showwarning("Invalid Action", "User is not muted!")
            
    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                data = json.load(f)
            
            self.server_ip = data.get('SERVER_IP', 'localhost')
            self.port = data.get('PORT', 8080)
            self.user_name = data.get('USER_NAME', socket.gethostname())
            
            self.add_to_chat(f"⚙️ Configuration loaded:\n🌐 Server: {self.server_ip}:{self.port}\n👤 Username: {self.user_name}\n", "system")
            self.add_to_chat(r"""
            _       __     __                             ______         ______                    _ ________          __ 
            | |     / /__  / /________  ____ ___  ___     /_  __/___     /_  __/__  _________ ___  (_) ____/ /_  ____ _/ /_
            | | /| / / _ \/ / ___/ __ \/ __ `__ \/ _ \     / / / __ \     / / / _ \/ ___/ __ `__ \/ / /   / __ \/ __ `/ __/
            | |/ |/ /  __/ / /__/ /_/ / / / / / /  __/    / / / /_/ /    / / /  __/ /  / / / / / / / /___/ / / / /_/ / /_  
            |__/|__/\___/_/\___/\____/_/ /_/ /_/\___/    /_/  \____/    /_/  \___/_/  /_/ /_/ /_/_/\____/_/ /_/\__,_/\__/  

            TermiChat Client — Version 1.0 | Author: VibhasDutta | Updated: 2025-06-01
            """)
        except FileNotFoundError:
            self.create_default_config()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
            
    def create_default_config(self):
        default_config = {
            'SERVER_IP': 'localhost',
            'PORT': 8080,
            'USER_NAME': socket.gethostname()
        }
        
        try:
            with open('config.json', 'w') as f:
                json.dump(default_config, f, indent=4)
            self.load_config()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create config: {e}")
    
    def show_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Settings")
        settings_window.geometry("400x250")
        settings_window.configure(bg='#2c3e50')
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings form
        frame = ttk.Frame(settings_window, style='Custom.TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Server IP
        ttk.Label(frame, text="🌐 Server IP:", style='Custom.TLabel').grid(row=0, column=0, sticky=tk.W, pady=5)
        ip_entry = tk.Entry(frame, font=('Arial', 10))
        ip_entry.insert(0, self.server_ip)
        ip_entry.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        
        # Port
        ttk.Label(frame, text="🔌 Port:", style='Custom.TLabel').grid(row=1, column=0, sticky=tk.W, pady=5)
        port_entry = tk.Entry(frame, font=('Arial', 10))
        port_entry.insert(0, str(self.port))
        port_entry.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        
        # Username
        ttk.Label(frame, text="👤 Username:", style='Custom.TLabel').grid(row=2, column=0, sticky=tk.W, pady=5)
        user_entry = tk.Entry(frame, font=('Arial', 10))
        user_entry.insert(0, self.user_name)
        user_entry.grid(row=2, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Button frame
        btn_frame = ttk.Frame(frame, style='Custom.TFrame')
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        def save_settings():
            try:
                new_config = {
                    'SERVER_IP': ip_entry.get(),
                    'PORT': int(port_entry.get()),
                    'USER_NAME': user_entry.get()
                }
                
                with open('config.json', 'w') as f:
                    json.dump(new_config, f, indent=4)
                
                self.server_ip = new_config['SERVER_IP']
                self.port = new_config['PORT']
                self.user_name = new_config['USER_NAME']
                
                self.add_to_chat("✅ Settings saved successfully!", "success")
                settings_window.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Invalid port number!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {e}")
        
        ttk.Button(btn_frame, text="💾 Save", command=save_settings, style='Custom.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=settings_window.destroy, style='Custom.TButton').pack(side=tk.LEFT)
    
    def show_commands_window(self):
        if hasattr(self, 'commands_window') and self.commands_window.winfo_exists():
            self.commands_window.lift()
            return
            
        self.commands_window = tk.Toplevel(self.root)
        self.commands_window.title("📋 Chat Commands")
        self.commands_window.geometry("600x600")
        self.commands_window.configure(bg='#2c3e50')
        
        # Commands frame
        frame = ttk.Frame(self.commands_window, style='Custom.TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="🎮 Available Commands", 
                 style='Custom.TLabel', font=('Arial', 14, 'bold')).pack(pady=(0, 15))
        
        commands_text = scrolledtext.ScrolledText(
            frame, height=20, width=70,
            bg='#34495e', fg='white', font=('Consolas', 10),
            state=tk.DISABLED, wrap=tk.WORD
        )
        commands_text.pack(fill=tk.BOTH, expand=True)
        
        # Command list - updated to remove prefix references
        commands_info = """
🟢 Check Online Users
   └ View who's currently connected to the server

👑 View Administrators
   └ Show all server administrators

🚫 Ban User (Admin Only)
   └ Permanently ban a user from the server

✅ Unban User (Admin Only)
   └ Remove a user from the ban list

📋 View Ban List (Admin Only)
   └ Show all currently banned users

👢 Kick User (Admin Only)
   └ Remove a user from the server temporarily

🔇 Mute User (Admin Only)
   └ Prevent a user from sending messages

🔊 Unmute User (Admin Only)
   └ Allow a muted user to send messages again

📢 Send Announcement (Admin Only)
   └ Broadcast a message to all users

🌐 Server Information
   └ Display server details and statistics

🚪 Disconnect
   └ Safely disconnect from the server

═══════════════════════════════════════

💡 All commands are available through buttons below:
"""
        
        commands_text.config(state=tk.NORMAL)
        commands_text.insert(tk.END, commands_info)
        commands_text.config(state=tk.DISABLED)
        
        # Quick action buttons frame
        buttons_frame = ttk.Frame(frame, style='Custom.TFrame')
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Row 1
        row1 = ttk.Frame(buttons_frame, style='Custom.TFrame')
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Button(row1, text="🟢 Online", 
                  command=self.request_online_users).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="👑 Admins", 
                  command=self.request_admin_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="🌐 Server Info", 
                  command=self.request_server_info).pack(side=tk.LEFT, padx=2)
        
        self.admin_button_refs = []  # Store button references to enable/disable later

        # Row 2: Ban, Unban, Kick
        row2 = ttk.Frame(buttons_frame, style='Custom.TFrame')
        row2.pack(fill=tk.X, pady=2)

        btn_ban = ttk.Button(row2, text="🚫 Ban", command=lambda: self.admin_action("ban"))
        btn_ban.pack(side=tk.LEFT, padx=2)
        self.admin_button_refs.append(btn_ban)

        btn_unban = ttk.Button(row2, text="✅ Unban", command=lambda: self.admin_action("unban"))
        btn_unban.pack(side=tk.LEFT, padx=2)
        self.admin_button_refs.append(btn_unban)

        btn_kick = ttk.Button(row2, text="👢 Kick", command=lambda: self.admin_action("kick"))
        btn_kick.pack(side=tk.LEFT, padx=2)
        self.admin_button_refs.append(btn_kick)

        # Row 3: Mute, Unmute, Announce
        row3 = ttk.Frame(buttons_frame, style='Custom.TFrame')
        row3.pack(fill=tk.X, pady=2)

        btn_mute = ttk.Button(row3, text="🔇 Mute", command=lambda: self.admin_action("mute"))
        btn_mute.pack(side=tk.LEFT, padx=2)
        self.admin_button_refs.append(btn_mute)

        btn_unmute = ttk.Button(row3, text="🔊 Unmute", command=lambda: self.admin_action("unmute"))
        btn_unmute.pack(side=tk.LEFT, padx=2)
        self.admin_button_refs.append(btn_unmute)

        btn_announce = ttk.Button(row3, text="📢 Announce", command=self.announce_message)
        btn_announce.pack(side=tk.LEFT, padx=2)
        self.admin_button_refs.append(btn_announce)

        # Row 4: Banlist
        row4 = ttk.Frame(buttons_frame, style='Custom.TFrame')
        row4.pack(fill=tk.X, pady=2)

        btn_banlist = ttk.Button(row4, text="📋 Ban List", command=self.request_ban_list)
        btn_banlist.pack(side=tk.LEFT, padx=2)
        self.admin_button_refs.append(btn_banlist)

        # Set all admin buttons enabled or disabled based on permission
        for btn in self.admin_button_refs:
            btn.config(state=tk.NORMAL if self.is_admin else tk.DISABLED)

    def announce_message(self):
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to server!")
            return
        message = simpledialog.askstring("📢 Announcement", "Enter announcement message:")
        if message:
            self.send_admin_command("announce", message)

    def admin_action(self, action):
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to server!")
            return

        if not self.online_users:
            messagebox.showinfo("Info", "No users are currently online.")
            return

        self.prompt_user_selection_popup(action)

    def prompt_user_selection_popup(self, action):
        """Popup window for admin to select a user for actions like ban/kick/mute"""
        popup = tk.Toplevel(self.root)
        popup.title(f"Select User to {action.capitalize()}")
        popup.geometry("300x300")
        popup.configure(bg="#2c3e50")
        popup.transient(self.root)
        popup.grab_set()

        ttk.Label(popup, text=f"Select user to {action}:", style='Custom.TLabel').pack(pady=10)

        listbox = tk.Listbox(popup, bg='#34495e', fg='white', font=('Consolas', 10), height=10)
        for user in self.online_users:
            if user != self.user_name:  # Prevent self-selection
                display = f"{'👑 ' if user in self.admin_users else ''}{user}"
                listbox.insert(tk.END, display)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        def send_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a user.")
                return
            selected_name = listbox.get(selection[0]).strip("👑 ").strip()
            try:
                index = self.online_users.index(selected_name)
                self.send_admin_command(action, str(index))
                popup.destroy()
            except ValueError:
                messagebox.showerror("Error", "User not found in online list.")

        ttk.Button(popup, text="✅ OK", command=send_selected, style='Success.TButton').pack(pady=(5, 10))

    def send_admin_command(self, command, data):
        """Send admin command to server with the required protocol"""
        if not self.connected:
            return
        
        try:
            # Send the command first
            command_msg = f"!{command}"  # Server still expects the prefix format
            self.send_raw_message(command_msg)
            
            # Send followup data after a small delay
            threading.Thread(target=lambda: self.send_followup_data(data), daemon=True).start()
            
        except Exception as e:
            self.add_to_chat(f"❌ Error sending admin command: {e}", "error")

    def send_followup_data(self, data):
        time.sleep(0.1)  # Small delay to ensure command is processed first
        try:
            if self.connected and self.client:
                self.client.send(f"{len(data):04}".encode('utf-8'))
                self.client.send(data.encode('utf-8'))
        except Exception as e:
            self.root.after(0, lambda e=e: self.add_to_chat(f"❌ Error sending followup data: {e}", "error"))
    
    def request_online_users(self):
        """Request list of online users"""
        if self.connected:
            self.send_raw_message("!online")
    
    def request_admin_list(self):
        """Request list of administrators"""
        if self.connected:
            self.send_raw_message("!adminlist")
    
    def request_server_info(self):
        """Request server information"""
        if self.connected:
            self.send_raw_message("!serverinfo")
    
    def request_ban_list(self):
        """Request list of banned users"""
        if self.connected:
            self.send_raw_message("!banlist")
    
    def connect_to_server(self):
        if self.connected:
            return
            
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(10.0)  # 10 second timeout for connection
            self.client.connect((self.server_ip, self.port))
            
            # Send username (no prefix needed anymore)
            self.client.send(f"{len(self.user_name):04}".encode('utf-8'))
            self.client.send(self.user_name.encode('utf-8'))
            
            # Send default prefix for server compatibility
            default_prefix = "!"
            self.client.send(f"{len(default_prefix):04}".encode('utf-8'))
            self.client.send(default_prefix.encode('utf-8'))
            
            # Check ban status
            ban_verify_len = int(self.client.recv(4).decode('utf-8'))
            ban_verify = self.client.recv(ban_verify_len).decode('utf-8')
            
            if ban_verify == 'you are banned':
                messagebox.showerror("Banned", f"You are banned from server {self.server_ip}:{self.port}")
                self.client.close()
                return
            
            # Server password authentication
            if not self.authenticate_server():
                return
                
            # Admin authentication if needed
            if not self.check_admin_auth():
                return
            
            # Remove timeout for normal operation
            self.client.settimeout(None)
            
            self.connected = True
            self.receiving = True
            self.status_label.config(text="🟢 Connected")
            self.connect_btn.config(text="🔌 Disconnect", command=self.disconnect_from_server)
            self.message_entry.config(state=tk.NORMAL)
            self.send_btn.config(state=tk.NORMAL)
            
            # Start receiving messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
            self.add_to_chat(f"✅ Connected to {self.server_ip}:{self.port}", "success")
            
            # Request initial user lists with delay
            threading.Timer(1.0, self.request_user_lists).start()
            
        except socket.timeout:
            messagebox.showerror("Connection Error", "Connection timeout! Check server address and port.")
            if self.client:
                self.client.close()
        except ConnectionRefusedError:
            messagebox.showerror("Connection Error", "Connection refused! Is the server running?")
            if self.client:
                self.client.close()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            if self.client:
                self.client.close()
    
    def authenticate_server(self):
        attempts = 0
        while attempts < 3:
            password = simpledialog.askstring("Server Password", 
                                            "Enter server password:", show='*')
            if not password:
                self.client.close()
                return False
                
            # Fixed: Changed from 8 to 9 to match server requirement
            if len(password) < 9:
                messagebox.showwarning("Invalid Password", 
                                     "Password must be at least 9 characters long!")
                continue
            
            try:
                self.client.send(f"{len(password):04}".encode('utf-8'))
                self.client.send(password.encode('utf-8'))
                
                verify_len = int(self.client.recv(4).decode('utf-8'))
                verify = self.client.recv(verify_len).decode('utf-8')
                
                if verify == 'access denied':
                    attempts += 1
                    messagebox.showerror("Access Denied", f"Wrong password! {3-attempts} attempts remaining")
                else:
                    return True
            except Exception as e:
                messagebox.showerror("Authentication Error", f"Error during authentication: {e}")
                self.client.close()
                return False
        
        messagebox.showerror("Authentication Failed", "Too many failed attempts!")
        self.client.close()
        return False
    
    def create_password_dialog(self, title, prompt):
        """Create a custom password dialog to avoid tkinter widget naming conflicts"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.configure(bg='#2c3e50')
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        result = {"password": None}
        
        # Create dialog content
        frame = ttk.Frame(dialog, style='Custom.TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text=prompt, style='Custom.TLabel').pack(pady=(0, 10))
        
        password_var = tk.StringVar()
        entry = tk.Entry(frame, textvariable=password_var, show='*', font=('Arial', 11))
        entry.pack(fill=tk.X, pady=(0, 15))
        entry.focus_set()
        
        button_frame = ttk.Frame(frame, style='Custom.TFrame')
        button_frame.pack()
        
        def on_ok():
            result["password"] = password_var.get()
            dialog.destroy()
        
        def on_cancel():
            result["password"] = None
            dialog.destroy()
        
        ttk.Button(button_frame, text="OK", command=on_ok, style='Custom.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel, style='Custom.TButton').pack(side=tk.LEFT)
        
        # Bind Enter key to OK
        entry.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return result["password"]

    def authenticate_server(self):
        attempts = 0
        while attempts < 3:
            # Replace simpledialog.askstring with custom dialog
            password = self.create_password_dialog("Server Password", "Enter server password:")
            if not password:
                self.client.close()
                return False
                
            if len(password) < 9:
                messagebox.showwarning("Invalid Password", 
                                    "Password must be at least 9 characters long!")
                continue
            
            try:
                self.client.send(f"{len(password):04}".encode('utf-8'))
                self.client.send(password.encode('utf-8'))
                
                verify_len = int(self.client.recv(4).decode('utf-8'))
                verify = self.client.recv(verify_len).decode('utf-8')
                
                if verify == 'access denied':
                    attempts += 1
                    messagebox.showerror("Access Denied", f"Wrong password! {3-attempts} attempts remaining")
                else:
                    return True
            except Exception as e:
                messagebox.showerror("Authentication Error", f"Error during authentication: {e}")
                self.client.close()
                return False
        
        messagebox.showerror("Authentication Failed", "Too many failed attempts!")
        self.client.close()
        return False

    def check_admin_auth(self):
        try:
            admin_verify_len = int(self.client.recv(4).decode('utf-8'))
            admin_verify = self.client.recv(admin_verify_len).decode('utf-8')
            
            if admin_verify == 'admin?':
                is_admin = messagebox.askyesno("Admin Check", "Are you an administrator?")
                response = "yes" if is_admin else "no"
                
                self.client.send(f"{len(response):04}".encode('utf-8'))
                self.client.send(response.encode('utf-8'))
                
                if is_admin:
                    attempts = 0
                    while attempts < 3:
                        # Replace simpledialog.askstring with custom dialog
                        admin_password = self.create_password_dialog("Admin Password", "Enter admin password:")
                        if not admin_password:
                            break
                            
                        if len(admin_password) < 9:
                            messagebox.showwarning("Invalid Password", 
                                                "Password must be at least 9 characters long!")
                            continue
                        
                        try:
                            self.client.send(f"{len(admin_password):04}".encode('utf-8'))
                            self.client.send(admin_password.encode('utf-8'))
                            
                            response_len = int(self.client.recv(4).decode('utf-8'))
                            admin_response = self.client.recv(response_len).decode('utf-8')
                            
                            if admin_response == 'access denied':
                                attempts += 1
                                messagebox.showerror("Access Denied", f"Wrong admin password! {3-attempts} attempts remaining")
                            else:
                                self.is_admin = True
                                self.add_to_chat("👑 Admin privileges granted!", "admin")
                                if hasattr(self, 'admin_button_refs'):
                                    for btn in self.admin_button_refs:
                                        btn.config(state=tk.NORMAL)
                                break
                        except Exception as e:
                            messagebox.showerror("Admin Auth Error", f"Error during admin authentication: {e}")
                            self.client.close()
                            return False
                    else:
                        messagebox.showerror("Authentication Failed", "Too many failed admin attempts!")
                        self.client.close()
                        return False
            elif admin_verify == "Welcome to the Server!":
                pass
                
        except Exception as e:
            self.add_to_chat(f"❌ Admin auth error: {e}", "error")
            return False
        
        return True
    
    def request_user_lists(self):
        """Request updated user lists from server"""
        if self.connected:
            try:
                # Request online users
                self.request_online_users()
                time.sleep(0.2)
                # Request admin list
                self.request_admin_list()
            except Exception as e:
                self.add_to_chat(f"❌ Error requesting user lists: {e}", "error")
    
    def disconnect_from_server(self):
        if self.connected:
            try:
                self.receiving = False
                self.send_raw_message("!exit")
                time.sleep(0.1)  # Give time for exit message to send
                self.client.close()
            except:
                pass
            
            self.connected = False
            self.is_admin = False
            self.online_users = []
            self.admin_users = []
            self.banned_users = []
            self.muted_users = []
            
            self.status_label.config(text="🔴 Disconnected")
            self.connect_btn.config(text="🔗 Connect", command=self.connect_to_server)
            self.message_entry.config(state=tk.DISABLED)
            self.send_btn.config(state=tk.DISABLED)
            
            # Update admin buttons in commands window if it exists
            if hasattr(self, 'admin_button_refs'):
                for btn in self.admin_button_refs:
                    btn.config(state=tk.DISABLED)
            
            self.update_user_lists()
            self.add_to_chat("❌ Disconnected from server", "warning")
    
    def send_message(self, event=None):
        if not self.connected:
            return
            
        message = self.message_entry.get().strip()
        if not message:
            return
        
        # Block command-like messages from being sent as regular chat
        if message.startswith('!'):
            messagebox.showwarning("Invalid Message", "Commands must be sent using the buttons in the Commands window!")
            self.message_entry.delete(0, tk.END)
            return
        
        try:
            self.send_raw_message(message)
            
            # Add own message to chat
            self.add_to_chat(f"[{self.user_name}] {message}", "own")
            
            self.message_entry.delete(0, tk.END)
                
        except Exception as e:
            self.add_to_chat(f"❌ Error sending message: {e}", "error")
    
    def send_raw_message(self, message):
        if not self.connected or not self.client:
            return
            
        try:
            msg_bytes = message.encode('utf-8')
            msg_length = len(msg_bytes)
            length_header = str(msg_length).encode('utf-8')
            length_header += b' ' * (64 - len(length_header))
            
            self.client.send(length_header)
            self.client.send(msg_bytes)
        except Exception as e:
            self.add_to_chat(f"❌ Error sending raw message: {e}", "error")
    
    def receive_messages(self):
        try:
            while self.connected and self.receiving:
                try:
                    message = self.client.recv(2048).decode('utf-8')
                    if not message:
                        break
                        
                    if message == "[200]Exit":
                        self.add_to_chat("❌ Server disconnected", "warning")
                        self.root.after(0, self.disconnect_from_server)
                        break
                    else:
                        self.process_received_message(message)
                        
                except socket.timeout:
                    continue
                except ConnectionResetError:
                    self.add_to_chat("🔒 Connection was reset by server", "error")
                    break
                except Exception as e:
                    if self.connected:
                        self.add_to_chat(f"🔒 Receive error: {e}", "error")
                    break
                    
        except Exception as e:
            if self.connected:
                self.add_to_chat(f"🔒 Connection lost: {e}", "error")
                
        # Cleanup on receive thread exit
        if self.connected:
            self.root.after(0, self.disconnect_from_server)
    
    def process_received_message(self, message):
        """Process and categorize received messages"""
        msg_type = "message"  # Default

        # ✅ PRIORITY: admin join message
        if message.startswith("👑") and "has joined the server" in message and "[ADMIN:" in message:
            msg_type = "admin"
        
        # 🚫 EXCLUSIVE: only if not admin
        elif "joined the server" in message or "left the chat" in message:
            msg_type = "join_leave"
        
        elif message.startswith("🟢") and ("Users" in message or "Online" in message):
            self.parse_online_users(message)
            return
        
        elif message.startswith("👑") and ("Admin" in message or "administrator" in message or "[" in message):
            self.parse_admin_users(message)
            return
        
        elif "No Admins are online" in message:
            self.admin_users = []
            return
        elif message.startswith("📢") or "ANNOUNCEMENT" in message.upper() or "Announcement" in message:
            msg_type = "announcement"
        
        elif message.startswith("⛔") or message.startswith("❌"):
            msg_type = "error"
        
        elif message.startswith("✅") or (message.startswith("🟢") and "granted" in message):
            msg_type = "success"
        
        elif message.startswith("⚠️") or message.startswith("🔶"):
            msg_type = "warning"
        
        elif "[PRIVATE]" in message or "[PM]" in message or "[DM]" in message:
            msg_type = "private"
        
        elif message.startswith("🔹[") or message.startswith("🔸["):
            # Command response with index → show it
            msg_type = "system"

        elif message.startswith("🔹") or message.startswith("🔸"):
            if "🔹" in message:
                self.parse_online_users(message)
            return
        
        elif message.startswith("🔗") and "Server Address" in message:
            msg_type = "system"
        
        elif message.startswith("💠"):
            msg_type = "message"

        self.add_to_chat(message, msg_type)

        
    def parse_online_users(self, message):
        if "Online Users:" in message:
            self.online_users = []

        elif "🔹" in message:
            user_info = message.replace("🔹 ", "").strip()
            if ":" in user_info:
                username = user_info.split(":")[0]
                if username not in self.online_users:
                    self.online_users.append(username)

        if self.user_name not in self.online_users:
            self.online_users.append(self.user_name)

    
    def parse_admin_users(self, message):
        if "👑" in message and "[" in message and "]" in message:
            parts = message.split("]", 1)
            if len(parts) > 1:
                user_info = parts[1].strip()
                if ":" in user_info:
                    username = user_info.split(":")[0]
                    if username not in self.admin_users:
                        self.admin_users.append(username)

        elif "No Admins are online" in message:
            self.admin_users = []

        # Always ensure self is included if admin
        if self.is_admin and self.user_name not in self.admin_users:
            self.admin_users.append(self.user_name)
    
    def add_to_chat(self, message, msg_type="message"):
        timestamp = time.strftime("[%H:%M:%S]")
        
        def update_chat():
            self.chat_display.config(state=tk.NORMAL)
            
            # Add message with appropriate tag
            full_message = f"{timestamp} {message}\n"
            self.chat_display.insert(tk.END, full_message, msg_type)
            
            self.chat_display.config(state=tk.DISABLED)
            self.chat_display.see(tk.END)
        
        # Ensure GUI updates happen on main thread
        if threading.current_thread() == threading.main_thread():
            update_chat()
        else:
            self.root.after(0, update_chat)
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        if self.connected:
            self.disconnect_from_server()
        self.root.destroy()

if __name__ == "__main__":
    try:
        app = ChatClient()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")