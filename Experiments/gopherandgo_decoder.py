import base64
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import tempfile
import webbrowser
import re
from PIL import Image
from io import BytesIO
import os
import sys
import sqlite3
import socketserver
import threading
import mimetypes
import urllib.parse

class GopherRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        request = self.request.recv(1024).strip().decode("utf-8")
        selector = urllib.parse.unquote(request.split("\t")[0])  # Decode URL-encoded selector
        
        if selector == "" or selector == ".":
            # Serve the Gopher menu
            menu = "iWelcome to Our Gopher Server\r\n"  # Informational header
            menu += "1Main Directory\t/\tlocalhost\t70\r\n"
            self.request.sendall(menu.encode("utf-8"))
        elif selector == "/":
            # Serve the main directory listing
            menu = "iContents of Main Directory\tfake\t(NULL)\t0\r\n"  # Prettified header
            menu += "i--------------------------------\tfake\t(NULL)\t0\r\n"  # Decorative separator
            try:
                for item in os.listdir(gopher_folder):
                    item_path = os.path.join(gopher_folder, item)
                    if os.path.isfile(item_path):
                        menu += "0{}\t/{}\tlocalhost\t70\r\n".format(item, item)
            except Exception as e:
                menu += "3Error: {}\tfake\t(NULL)\t0\r\n".format(str(e))
            menu += "1Return to Main Menu\t.\tlocalhost\t70\r\n"  # Link to go back to the main menu
            self.request.sendall(menu.encode("utf-8"))
        else:
            # Serve the requested file
            selector = selector.lstrip('/')
            file_path = os.path.join(gopher_folder, selector)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as file:
                    content = file.read()
                self.request.sendall(content)
            else:
                self.request.sendall(b"Error: File not found.")


def start_gopher_server():
    server = socketserver.TCPServer((host, port), GopherRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()

def is_base64(s):
    try:
        base64.b64decode(s)
        return True
    except Exception:
        return False

def save_file(file_content, file_extension):
    file_name = urllib.parse.quote(f"decoded_file{file_extension}")
    file_path = os.path.join(gopher_folder, file_name)
    with open(file_path, "wb") as file:
        file.write(file_content)
    messagebox.showinfo("Success", f"{file_extension.upper()} file saved.")

def open_file(file_path):
    if sys.platform == "win32":
        os.startfile(file_path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        os.system(f"{opener} {file_path}")

def compile_base64():
    base64_code = code_entry.get("1.0", tk.END).strip()
    
    if not base64_code:
        messagebox.showwarning("Warning", "Please enter the base64 code.")
        return
    
    try:
        # Check if the specified format is present
        if "-----" in base64_code:
            # Extract base64 code between the dashes
            base64_code = re.findall(r'-----(.*?)-----', base64_code, re.DOTALL)
            if base64_code:
                base64_code = base64_code[0].strip()
            else:
                messagebox.showwarning("Warning", "No valid base64 code found between the dashes.")
                return
        else:
            # Remove non-base64 content
            base64_code = re.sub(r'[^a-zA-Z0-9+/=\s]', '', base64_code)
            base64_code = ''.join(base64_code.split())
        
        if not is_base64(base64_code):
            messagebox.showwarning("Warning", "Invalid base64 code.")
            return
        
        decoded_content = base64.b64decode(base64_code)
        
        # Check if the decoded content is an image
        try:
            image = Image.open(BytesIO(decoded_content))
            image.verify()
            is_image = True
        except:
            is_image = False
        
        if is_image:
            # Save the decoded image
            if save_image_var.get():
                save_file(decoded_content, ".png")
            
            # Open the decoded image in the default image viewer
            if open_image_var.get():
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    temp_file.write(decoded_content)
                    temp_file_path = temp_file.name
                open_file(temp_file_path)
        else:
            # Check if the decoded content is HTML
            try:
                decoded_html = decoded_content.decode("utf-8")
                if "<html" in decoded_html.lower() and "</html>" in decoded_html.lower():
                    is_html = True
                else:
                    is_html = False
            except:
                is_html = False
            
            if is_html:
                # Save the decoded HTML
                if save_html_var.get():
                    save_file(decoded_html.encode("utf-8"), ".html")
                
                # Open the decoded HTML in the default web browser
                if open_html_var.get():
                    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".html") as temp_file:
                        temp_file.write(decoded_html)
                        temp_file_path = temp_file.name
                    webbrowser.open(temp_file_path)
            else:
                # Check if the decoded content is plain text
                try:
                    decoded_text = decoded_content.decode("utf-8")
                    is_text = True
                except:
                    is_text = False
                
                if is_text:
                    # Save the decoded text file to the Gopher folder
                    if save_text_var.get():
                        file_name = urllib.parse.quote("decoded_text.txt")
                        file_path = os.path.join(gopher_folder, file_name)
                        with open(file_path, "w") as file:
                            file.write(decoded_text)
                        messagebox.showinfo("Success", "Text file saved to the Gopher folder.")
                else:
                    # Prompt the user to select the file format
                    file_formats = [".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".zip", ".rar", ".7z"]
                    selected_format = tk.StringVar(value=file_formats[0])
                    
                    file_format_window = tk.Toplevel(window)
                    file_format_window.title("Select File Format")
                    file_format_window.geometry("300x150")
                    file_format_window.configure(bg="#FFFFFF")
                    
                    file_format_frame = ttk.Frame(file_format_window, padding=20)
                    file_format_frame.pack(fill=tk.BOTH, expand=True)
                    
                    file_format_label = ttk.Label(file_format_frame, text="Select the file format:")
                    file_format_label.pack(anchor=tk.W, pady=(0, 10))
                    
                    file_format_dropdown = ttk.Combobox(file_format_frame, textvariable=selected_format, values=file_formats, state="readonly")
                    file_format_dropdown.pack(fill=tk.X, pady=(0, 20))
                    
                    def save_file_as_format():
                        file_extension = selected_format.get()
                        save_file(decoded_content, file_extension)
                        file_format_window.destroy()
                    
                    save_button = ttk.Button(file_format_frame, text="Save", command=save_file_as_format, style="Accent.TButton")
                    save_button.pack(pady=(0, 10))
                    
                    file_format_window.grab_set()
                    file_format_window.wait_window()
        
        messagebox.showinfo("Success", "Decoding completed.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def open_base64_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r") as file:
            base64_code = file.read().strip()
            code_entry.delete("1.0", tk.END)
            code_entry.insert(tk.END, base64_code)

def open_settings():
    settings_window = tk.Toplevel(window)
    settings_window.title("Settings")
    settings_window.geometry("400x450")
    settings_window.configure(bg="#FFFFFF")
    
    settings_frame = ttk.Frame(settings_window, padding=20)
    settings_frame.pack(fill=tk.BOTH, expand=True)
    
    # Open HTML option
    open_html_checkbox = ttk.Checkbutton(settings_frame, text="Open HTML file after decoding", variable=open_html_var)
    open_html_checkbox.pack(anchor=tk.W, pady=(0, 10))
    
    # Save HTML option
    save_html_checkbox = ttk.Checkbutton(settings_frame, text="Prompt to save HTML file after decoding", variable=save_html_var)
    save_html_checkbox.pack(anchor=tk.W, pady=(0, 10))
    
    # Open Image option
    open_image_checkbox = ttk.Checkbutton(settings_frame, text="Open image file after decoding", variable=open_image_var)
    open_image_checkbox.pack(anchor=tk.W, pady=(0, 10))
    
    # Save Image option
    save_image_checkbox = ttk.Checkbutton(settings_frame, text="Prompt to save image file after decoding", variable=save_image_var)
    save_image_checkbox.pack(anchor=tk.W, pady=(0, 10))
    
    # Save Text option
    save_text_checkbox = ttk.Checkbutton(settings_frame, text="Prompt to save text file after decoding", variable=save_text_var)
    save_text_checkbox.pack(anchor=tk.W, pady=(0, 20))
    
    close_button = ttk.Button(settings_frame, text="Close", command=settings_window.destroy, style="Accent.TButton")
    close_button.pack(pady=(0, 10))

def read_varac_database():
    try:
        # Default path to the VarAC SQLite database
        default_db_path = "C:\\VarAC\\VarAC.db"
        
        if not os.path.isfile(default_db_path):
            # Prompt the user to select the directory containing the VarAC database
            messagebox.showinfo("Information", "VarAC database not found in the default location. Please select the directory containing the VarAC database.")
            db_directory = filedialog.askdirectory(title="Select VarAC Database Directory")
            if not db_directory:
                return
            
            # Check if the VarAC database file exists in the selected directory
            db_path = os.path.join(db_directory, "VarAC.db")
            if not os.path.isfile(db_path):
                messagebox.showerror("Error", "VarAC database not found in the selected directory.")
                return
        else:
            db_path = default_db_path
        
        # Connect to the VarAC SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query the datastream table to get the latest base64 code
        cursor.execute("SELECT entry FROM datastream ORDER BY id DESC")
        results = cursor.fetchall()
        
        base64_code = ""
        for result in results:
            entry = result[0]
            if "-----" in entry:
                # Extract base64 code between the dashes
                base64_code = re.findall(r'-----(.*?)-----', entry, re.DOTALL)
                if base64_code:
                    base64_code = base64_code[0].strip()
                    break
        
        if base64_code:
            code_entry.delete("1.0", tk.END)
            code_entry.insert(tk.END, base64_code)
            compile_base64()
        else:
            messagebox.showinfo("Information", "No base64 code found in the VarAC database.")
        
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"An error occurred while reading the VarAC database: {str(e)}")

# Gopher server configuration
host = "localhost"
port = 70
gopher_folder = os.path.abspath("gopher_files")  # Convert to absolute path

# Create the Gopher files folder if it doesn't exist
if not os.path.exists(gopher_folder):
    os.makedirs(gopher_folder)

# Start the Gopher server
start_gopher_server()

# Create the main window
window = tk.Tk()
window.title("Base64 Decoder")
window.geometry("800x600")
window.configure(bg="#FFFFFF")

# Create a style for the main window
style = ttk.Style(window)
style.theme_use("clam")
style.configure(".", background="#FFFFFF", foreground="#333333", font=("Segoe UI", 12))
style.configure("TFrame", background="#FFFFFF")
style.configure("TLabel", background="#FFFFFF", foreground="#333333", font=("Segoe UI", 14))
style.configure("TButton", font=("Segoe UI", 12), padding=10)
style.configure("Accent.TButton", background="#007BFF", foreground="#FFFFFF", font=("Segoe UI", 12, "bold"), padding=10)

# Create a frame for the main content
main_frame = ttk.Frame(window, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# Create and pack the label
label = ttk.Label(main_frame, text="Enter base64 code:")
label.pack(anchor=tk.W, pady=(0, 10))

# Create and pack the text entry field
code_entry = tk.Text(main_frame, height=15, width=80, font=("Consolas", 12), bg="#F5F5F5", fg="#333333", padx=10, pady=10, wrap=tk.WORD, bd=0, highlightthickness=1, highlightcolor="#CCCCCC", highlightbackground="#CCCCCC")
code_entry.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

# Create a frame for the buttons
button_frame = ttk.Frame(main_frame)
button_frame.pack(anchor=tk.W)

# Create and pack the decode button
decode_button = ttk.Button(button_frame, text="Decode", command=compile_base64, style="Accent.TButton")
decode_button.pack(side=tk.LEFT, padx=(0, 10))

# Create and pack the open file button
open_file_button = ttk.Button(button_frame, text="Open Base64 File", command=open_base64_file)
open_file_button.pack(side=tk.LEFT, padx=(0, 10))

# Create and pack the read from VarAC database button
read_database_button = ttk.Button(button_frame, text="Read from VarAC", command=read_varac_database)
read_database_button.pack(side=tk.LEFT, padx=(0, 10))

# Create and pack the settings button 
settings_button = ttk.Button(button_frame, text="Settings", command=open_settings)
settings_button.pack(side=tk.LEFT)

# Create variables for settings options
open_html_var = tk.BooleanVar(value=True)
save_html_var = tk.BooleanVar(value=False)
save_text_var = tk.BooleanVar(value=False)
open_image_var = tk.BooleanVar(value=True)
save_image_var = tk.BooleanVar(value=False)

# Start the main event loop
window.mainloop()