import base64
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import tempfile
import webbrowser
import re
import os
import sys
import imghdr
import subprocess

def is_base64(s):
    try:
        base64.b64decode(s)
        return True
    except Exception:
        return False

def save_file(file_content, file_extension):
    file_path = filedialog.asksaveasfilename(defaultextension=file_extension, filetypes=[(f"{file_extension.upper()} Files", f"*{file_extension}")])
    if file_path:
        with open(file_path, "wb") as file:
            file.write(file_content)
        messagebox.showinfo("Success", f"{file_extension.upper()} file saved.")
        return file_path
    return None

def open_file(file_path):
    if file_path:
        if sys.platform == "win32":
            os.startfile(file_path)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, file_path])

def detect_file_format(decoded_content):
    # Check if the decoded content is an image
    image_format = imghdr.what(None, decoded_content)
    if image_format:
        return image_format

    # Check if the decoded content is HTML
    try:
        decoded_html = decoded_content.decode("utf-8")
        if "<html" in decoded_html.lower() and "</html>" in decoded_html.lower():
            return "html"
    except:
        pass

    # Check for common file signatures or patterns
    file_signatures = {
        "pdf": b"%PDF-",
        "zip": b"PK\x03\x04",
        "rar": b"Rar!\x1a\x07",
        "7z": b"7z\xBC\xAF\x27\x1C",
        "tar": b"ustar\x00",
        "gz": b"\x1F\x8B\x08",
        "bz2": b"BZh",
        "exe": b"MZ",
        "doc": b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1",
        "xls": b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1",
        "ppt": b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1",
        "docx": b"PK\x03\x04",
        "xlsx": b"PK\x03\x04",
        "pptx": b"PK\x03\x04",
    }

    for file_format, signature in file_signatures.items():
        if decoded_content.startswith(signature):
            return file_format

    return None

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
        
        # Detect the file format
        file_format = detect_file_format(decoded_content)
        
        if file_format:
            if file_format in imghdr.tests:
                # Save the decoded image if the option is enabled
                if save_image_var.get():
                    saved_file_path = save_file(decoded_content, f".{file_format}")
            elif file_format == "html":
                # Save the decoded HTML if the option is enabled
                if save_html_var.get():
                    saved_file_path = save_file(decoded_content, ".html")
                    # Open the saved HTML in the default web browser if the option is enabled
                    if open_html_var.get():
                        webbrowser.open(saved_file_path)
                else:
                    # Open the decoded HTML in the default web browser if the option is enabled
                    if open_html_var.get():
                        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".html") as temp_file:
                            temp_file.write(decoded_content.decode("utf-8"))
                            temp_file_path = temp_file.name
                        webbrowser.open(temp_file_path)
            else:
                # Save the decoded file with the detected extension
                save_file(decoded_content, f".{file_format}")
        else:
            select_file_format(decoded_content)
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def select_file_format(decoded_content):
    file_formats = [".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv", ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".webm", ".mkv", ".avi", ".mp4", ".mov", ".wmv", ".flv", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".eps", ".ai", ".exe", ".dll", ".bat", ".sh", ".py", ".js", ".html", ".css", ".json", ".xml", ".yaml", ".db", ".sql", ".mdb", ".accdb", ".eml", ".msg", ".iso", ".img", ".dmg", ".ttf", ".otf", ".woff", ".woff2"]
    selected_format = tk.StringVar(value=file_formats[0])
    custom_format = tk.StringVar()
    
    file_format_window = tk.Toplevel(window)
    file_format_window.title("Select File Format")
    file_format_window.geometry("400x250")
    file_format_window.configure(bg="#FFFFFF")
    
    file_format_frame = ttk.Frame(file_format_window, padding=20)
    file_format_frame.pack(fill=tk.BOTH, expand=True)
    
    file_format_label = ttk.Label(file_format_frame, text="Select the file format:")
    file_format_label.pack(anchor=tk.W, pady=(0, 10))
    
    file_format_dropdown = ttk.Combobox(file_format_frame, textvariable=selected_format, values=file_formats, state="readonly")
    file_format_dropdown.pack(fill=tk.X, pady=(0, 10))
    
    custom_format_frame = ttk.Frame(file_format_frame)
    custom_format_frame.pack(fill=tk.X, pady=(0, 10))
    
    custom_format_label = ttk.Label(custom_format_frame, text="Or enter a custom format:")
    custom_format_label.pack(side=tk.LEFT)
    
    custom_format_entry = ttk.Entry(custom_format_frame, textvariable=custom_format)
    custom_format_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
    
    button_frame = ttk.Frame(file_format_frame)
    button_frame.pack(fill=tk.X)
    
    def save_file_as_format():
        file_extension = custom_format.get().strip()
        if not file_extension:
            file_extension = selected_format.get()
        if not file_extension.startswith("."):
            file_extension = "." + file_extension
        save_file(decoded_content, file_extension)
        file_format_window.destroy()
    
    save_button = ttk.Button(button_frame, text="Save", command=save_file_as_format)
    save_button.pack(side=tk.LEFT, padx=(0, 10))
    
    cancel_button = ttk.Button(button_frame, text="Cancel", command=file_format_window.destroy)
    cancel_button.pack(side=tk.LEFT)
    
    file_format_window.grab_set()
    file_format_window.wait_window()

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
    settings_window.geometry("400x400")
    settings_window.configure(bg="#FFFFFF")
    
    settings_frame = ttk.Frame(settings_window, padding=20)
    settings_frame.pack(fill=tk.BOTH, expand=True)
    
    settings_label = ttk.Label(settings_frame, text="Settings", font=("Segoe UI", 16, "bold"))
    settings_label.pack(anchor=tk.W, pady=(0, 20))
    
    # Open HTML option
    open_html_checkbox = ttk.Checkbutton(settings_frame, text="Open HTML file after decoding", variable=open_html_var)
    open_html_checkbox.pack(anchor=tk.W, pady=(0, 10))
    
    # Save HTML option
    save_html_checkbox = ttk.Checkbutton(settings_frame, text="Prompt to save HTML file after decoding", variable=save_html_var)
    save_html_checkbox.pack(anchor=tk.W, pady=(0, 10))
    
    close_button = ttk.Button(settings_frame, text="Close", command=settings_window.destroy, style="Accent.TButton")
    close_button.pack(pady=(0, 10))

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

# Create and pack the settings button
settings_button = ttk.Button(button_frame, text="Settings", command=open_settings)
settings_button.pack(side=tk.LEFT)

# Create variables for settings options
open_html_var = tk.BooleanVar(value=True)
save_html_var = tk.BooleanVar(value=False)
open_image_var = tk.BooleanVar(value=True)
save_image_var = tk.BooleanVar(value=False)

# Start the main event loop
window.mainloop()