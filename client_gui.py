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
        self.client_prefix = ""
        self.server_ip = ""
        self.port = 0
        
        # Initialize GUI
        self.setup_gui()
        self.load_config()
        
    def setup_gui(self):
        # Main window
        self.root = tk.Tk()
        self.root.title("Chat Client")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TFrame', background='#2c3e50')
        style.configure('Custom.TButton', background='#3498db', foreground='white')
        style.configure('Custom.TLabel', background='#2c3e50', foreground='white')
        
        # Main frame
        main_frame = ttk.Frame(self.root, style='Custom.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection status frame
        status_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="🔴 Disconnected", 
                                     style='Custom.TLabel', font=('Arial', 12, 'bold'))
        self.status_label.pack(side=tk.LEFT)
        
        self.connect_btn = ttk.Button(status_frame, text="🔗 Connect", 
                                     command=self.connect_to_server, style='Custom.TButton')
        self.connect_btn.pack(side=tk.RIGHT)
        
        self.settings_btn = ttk.Button(status_frame, text="⚙️ Settings", 
                                      command=self.show_settings, style='Custom.TButton')
        self.settings_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        self.commands_btn = ttk.Button(status_frame, text="📋 Commands", 
                                      command=self.show_commands_window, style='Custom.TButton')
        self.commands_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Chat display area
        chat_frame = ttk.Frame(main_frame, style='Custom.TFrame')
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Label(chat_frame, text="💬 Chat Messages", 
                 style='Custom.TLabel', font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, height=20, width=80, 
            bg='#34495e', fg='white', font=('Consolas', 10),
            state=tk.DISABLED, wrap=tk.WORD
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Message input frame
        input_frame = ttk.Frame(main_frame, style='Custom.TFrame')
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
        
    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                data = json.load(f)
            
            self.server_ip = data.get('SERVER_IP', 'localhost')
            self.port = data.get('PORT', 8080)
            self.user_name = data.get('USER_NAME', socket.gethostname())
            self.client_prefix = data.get('PREFIX', '!')
            
            self.add_to_chat(f"⚙️ Configuration loaded:\n🌐 Server: {self.server_ip}:{self.port}\n👤 Username: {self.user_name}\n🏷️ Prefix: {self.client_prefix}\n", "system")
            
        except FileNotFoundError:
            self.create_default_config()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
            
    def create_default_config(self):
        default_config = {
            'SERVER_IP': 'localhost',
            'PORT': 8080,
            'USER_NAME': socket.gethostname(),
            'PREFIX': '!'
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
        settings_window.geometry("400x300")
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
        
        # Prefix
        ttk.Label(frame, text="🏷️ Prefix:", style='Custom.TLabel').grid(row=3, column=0, sticky=tk.W, pady=5)
        prefix_entry = tk.Entry(frame, font=('Arial', 10))
        prefix_entry.insert(0, self.client_prefix)
        prefix_entry.grid(row=3, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        
        frame.columnconfigure(1, weight=1)
        
        # Button frame
        btn_frame = ttk.Frame(frame, style='Custom.TFrame')
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def save_settings():
            try:
                new_config = {
                    'SERVER_IP': ip_entry.get(),
                    'PORT': int(port_entry.get()),
                    'USER_NAME': user_entry.get(),
                    'PREFIX': prefix_entry.get()
                }
                
                with open('config.json', 'w') as f:
                    json.dump(new_config, f, indent=4)
                
                self.server_ip = new_config['SERVER_IP']
                self.port = new_config['PORT']
                self.user_name = new_config['USER_NAME']
                self.client_prefix = new_config['PREFIX']
                
                self.add_to_chat("✅ Settings saved successfully!", "system")
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
        self.commands_window.geometry("500x600")
        self.commands_window.configure(bg='#2c3e50')
        
        # Commands frame
        frame = ttk.Frame(self.commands_window, style='Custom.TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="🎮 Available Commands", 
                 style='Custom.TLabel', font=('Arial', 14, 'bold')).pack(pady=(0, 15))
        
        commands_text = scrolledtext.ScrolledText(
            frame, height=25, width=60,
            bg='#34495e', fg='white', font=('Consolas', 10),
            state=tk.DISABLED, wrap=tk.WORD
        )
        commands_text.pack(fill=tk.BOTH, expand=True)
        
        # Command list
        commands_info = f"""
🟢 {self.client_prefix}online
   └ Check who's currently online

👑 {self.client_prefix}adminlist
   └ Show all server administrators

🚫 {self.client_prefix}ban
   └ Ban a member (Admin only)
   └ You'll be prompted for the member index

✅ {self.client_prefix}unban
   └ Unban a member (Admin only)
   └ You'll be prompted for the member index

📋 {self.client_prefix}banlist
   └ Show all banned members (Admin only)

👢 {self.client_prefix}kick
   └ Kick a member (Admin only)
   └ You'll be prompted for the member index

🌐 {self.client_prefix}serverinfo
   └ Display server information

🔧 {self.client_prefix}shutdown
   └ Shutdown server (Admin only)

🚪 {self.client_prefix}exit
   └ Exit the chat

❓ {self.client_prefix}help
   └ Show this help information

═══════════════════════════════════════

💡 Quick Command Buttons:
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
                  command=lambda: self.send_command(f"{self.client_prefix}online")).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="👑 Admins", 
                  command=lambda: self.send_command(f"{self.client_prefix}adminlist")).pack(side=tk.LEFT, padx=2)
        ttk.Button(row1, text="🌐 Server Info", 
                  command=lambda: self.send_command(f"{self.client_prefix}serverinfo")).pack(side=tk.LEFT, padx=2)
        
        # Row 2
        row2 = ttk.Frame(buttons_frame, style='Custom.TFrame')
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Button(row2, text="🚫 Ban", 
                  command=lambda: self.admin_action("ban")).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text="✅ Unban", 
                  command=lambda: self.admin_action("unban")).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text="👢 Kick", 
                  command=lambda: self.admin_action("kick")).pack(side=tk.LEFT, padx=2)
        
        # Row 3 
        row4 = ttk.Frame(buttons_frame, style='Custom.TFrame')
        row4.pack(fill=tk.X, pady=2)

        ttk.Button(row4, text="🔇 Mute", command=lambda: self.admin_action("mute")).pack(side=tk.LEFT, padx=2)
        ttk.Button(row4, text="🔊 Unmute", command=lambda: self.admin_action("unmute")).pack(side=tk.LEFT, padx=2)
        ttk.Button(row4, text="📢 Announce", command=self.announce_message).pack(side=tk.LEFT, padx=2)
        
        # Row 4
        row3 = ttk.Frame(buttons_frame, style='Custom.TFrame')
        row3.pack(fill=tk.X, pady=2)
        
        ttk.Button(row3, text="📋 Ban List", 
                  command=lambda: self.send_command(f"{self.client_prefix}banlist")).pack(side=tk.LEFT, padx=2)
        ttk.Button(row3, text="🚪 Exit", 
                  command=self.disconnect_from_server).pack(side=tk.LEFT, padx=2)


    def announce_message(self):
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to server!")
            return
        message = simpledialog.askstring("📢 Announcement", "Enter announcement message:")
        if message:
            self.send_command(f"{self.client_prefix}announce")
            threading.Thread(target=lambda: self.send_followup_data(message), daemon=True).start()

    def admin_action(self, action):
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to server!")
            return

        self.send_command(f"{self.client_prefix}{action}")
        self.chat_display.insert(tk.END, f"⌛ Waiting for server to send list...\n")
        threading.Thread(target=lambda: self.handle_admin_target_selection(action), daemon=True).start()

    def handle_admin_target_selection(self,action):
        try:
            time.sleep(0.2)
            self.client.settimeout(2.0)

            options = []
            while True:
                msg = self.client.recv(2048).decode('utf-8')
                if msg.startswith("🔹[") or msg.startswith("🔸["):
                    options.append(msg)
                elif msg.startswith("⛔") or msg.startswith("⚠️"):
                    messagebox.showinfo("Info", msg)
                    self.client.settimeout(None)
                    return
                elif msg.startswith("Enter index to"):
                    break  # Server is ready for index input
                else:
                    # Probably a broadcast or unrelated message
                    self.add_to_chat(msg)
                    break

            self.client.settimeout(None)

            if not options:
                messagebox.showinfo("Info", "No users available for this action.")
                return

            options_text = "\n".join(options)
            index = simpledialog.askinteger("Select User", f"{options_text}\n\nEnter index:")

            if index is not None:
                self.send_followup_data(str(index))

        except socket.timeout:
            messagebox.showerror("Timeout", "No user list received from server.")
        except Exception as e:
            self.add_to_chat(f"❌ Admin action error: {e}", "error")

    def send_followup_data(self, data):
        time.sleep(0.1)  # Small delay to ensure command is processed first
        try:
            self.client.send(f"{len(data):04}".encode('utf-8'))
            self.client.send(data.encode('utf-8'))
        except Exception as e:
            self.add_to_chat(f"❌ Error sending followup data: {e}", "error")
    
    def send_command(self, command):
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to server!")
            return
        
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, command)
        self.send_message()
    
    def connect_to_server(self):
        if self.connected:
            return
            
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.server_ip, self.port))
            
            # Send username and prefix
            self.client.send(f"{len(self.user_name):04}".encode('utf-8'))
            self.client.send(self.user_name.encode('utf-8'))
            self.client.send(f"{len(self.client_prefix):04}".encode('utf-8'))
            self.client.send(self.client_prefix.encode('utf-8'))
            
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
            self.check_admin_auth()
            
            self.connected = True
            self.status_label.config(text="🟢 Connected")
            self.connect_btn.config(text="🔌 Disconnect", command=self.disconnect_from_server)
            self.message_entry.config(state=tk.NORMAL)
            self.send_btn.config(state=tk.NORMAL)
            
            # Start receiving messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
            self.add_to_chat(f"✅ Connected to {self.server_ip}:{self.port}", "system")
            
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
                return False
                
            if len(password) <= 8:
                messagebox.showwarning("Invalid Password", 
                                     "Password must be at least 8 characters long!")
                continue
            
            self.client.send(f"{len(password):04}".encode('utf-8'))
            self.client.send(password.encode('utf-8'))
            
            verify_len = int(self.client.recv(4).decode('utf-8'))
            verify = self.client.recv(verify_len).decode('utf-8')
            
            if verify == 'access denied':
                attempts += 1
                messagebox.showerror("Access Denied", f"Wrong password! {3-attempts} attempts remaining")
            else:
                return True
        
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
                        admin_password = simpledialog.askstring("Admin Password", 
                                                               "Enter admin password:", show='*')
                        if not admin_password:
                            break
                            
                        if len(admin_password) <= 8:
                            messagebox.showwarning("Invalid Password", 
                                                 "Password must be at least 8 characters long!")
                            continue
                        
                        self.client.send(f"{len(admin_password):04}".encode('utf-8'))
                        self.client.send(admin_password.encode('utf-8'))
                        
                        response_len = int(self.client.recv(4).decode('utf-8'))
                        admin_response = self.client.recv(response_len).decode('utf-8')
                        
                        if admin_response == 'access denied':
                            attempts += 1
                            messagebox.showerror("Access Denied", f"Wrong admin password! {3-attempts} attempts remaining")
                        else:
                            self.add_to_chat("👑 Admin privileges granted!", "system")
                            break
                    else:
                        messagebox.showerror("Authentication Failed", "Too many failed admin attempts!")
                        self.client.close()
                        return False
        except Exception as e:
            self.add_to_chat(f"❌ Admin auth error: {e}", "error")
        
        return True
    
    def disconnect_from_server(self):
        if self.connected:
            try:
                self.send_raw_message(f"{self.client_prefix}exit")
                self.client.close()
            except:
                pass
            
            self.connected = False
            self.status_label.config(text="🔴 Disconnected")
            self.connect_btn.config(text="🔗 Connect", command=self.connect_to_server)
            self.message_entry.config(state=tk.DISABLED)
            self.send_btn.config(state=tk.DISABLED)
            self.add_to_chat("❌ Disconnected from server", "system")
    
    def send_message(self, event=None):
        if not self.connected:
            return
            
        message = self.message_entry.get().strip()
        if not message:
            return
        
        try:
            self.send_raw_message(message)
            self.message_entry.delete(0, tk.END)
            
            # Handle exit command
            if message.startswith(f"{self.client_prefix}exit"):
                self.disconnect_from_server()
                
        except Exception as e:
            self.add_to_chat(f"❌ Error sending message: {e}", "error")
    
    def send_raw_message(self, message):
        msg_bytes = message.encode('utf-8')
        msg_length = len(msg_bytes)
        length_header = str(msg_length).encode('utf-8')
        length_header += b' ' * (64 - len(length_header))
        
        self.client.send(length_header)
        self.client.send(msg_bytes)
    
    def receive_messages(self):
        try:
            while self.connected:
                message = self.client.recv(2048).decode('utf-8')
                if message == "[200]Exit":
                    self.add_to_chat("❌ Server disconnected", "system")
                    self.root.after(0, self.disconnect_from_server)
                    break
                else:
                    self.add_to_chat(message, "message")
                    
        except Exception as e:
            if self.connected:
                self.add_to_chat(f"🔒 Connection lost: {e}", "error")
                self.root.after(0, self.disconnect_from_server)
    
    def add_to_chat(self, message, msg_type="message"):
        timestamp = time.strftime("[%H:%M:%S]")
        
        self.chat_display.config(state=tk.NORMAL)
        
        if msg_type == "system":
            self.chat_display.insert(tk.END, f"{timestamp} {message}\n", "system")
        elif msg_type == "error":
            self.chat_display.insert(tk.END, f"{timestamp} {message}\n", "error")
        else:
            self.chat_display.insert(tk.END, f"{timestamp} {message}\n")
        
        # Configure text tags for different message types
        self.chat_display.tag_configure("system", foreground="#3498db")
        self.chat_display.tag_configure("error", foreground="#e74c3c")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
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