import os
import subprocess
import shutil
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
from datetime import datetime

# Function to determine the available drive
def get_available_drive():
    for drive in ['E:', 'J:']:  # Adjust drive letters as needed
        if os.path.exists(drive):
            return drive
    raise RuntimeError("No specified drives are available.")

# Get the available drive
try:
    base_drive = get_available_drive()
except RuntimeError as e:
    messagebox.showerror("Error", str(e))
    raise SystemExit(e)

# Define the paths (Adjust folder names as needed)
data_folder_path = os.path.join(base_drive, "Data_Folder")
images_folder_path = os.path.join(base_drive, "Images_Folder")

# Function to get formatted date
def get_formatted_date():
    return datetime.now().strftime('%m-%d-%Y')

# Define the encryption function
def encrypt_folder(folder_path, encrypted_name, log_widget):
    if not os.path.exists(folder_path):
        log_widget.insert(tk.END, f"Folder {folder_path} does not exist. Skipping encryption.\n")
        return

    try:
        formatted_date = get_formatted_date()
        # Full paths for tar and encrypted files at the root of the available drive
        tar_path = os.path.join(base_drive, f"{encrypted_name}_{formatted_date}.tar")
        encrypted_tar_path = os.path.join(base_drive, f"{encrypted_name}_{formatted_date}.tar.aes")

        # Log the paths where files will be saved
        log_widget.insert(tk.END, f"Tar file will be saved to: {tar_path}\n")
        log_widget.insert(tk.END, f"Encrypted file will be saved to: {encrypted_tar_path}\n")

        # Compress the folder
        tar_command = f"tar -cvf {tar_path} -C {os.path.dirname(folder_path)} {os.path.basename(folder_path)}"
        subprocess.run(tar_command, shell=True, check=True)

        # Prompt for password
        password = simpledialog.askstring("Password", "Enter encryption password:", show='*')
        if not password:
            raise ValueError("Encryption canceled, no password provided.")

        # Encrypt the tarred folder
        openssl_command = f"openssl enc -aes-256-cbc -salt -pbkdf2 -iter 10000 -in {tar_path} -out {encrypted_tar_path} -pass pass:{password}"
        subprocess.run(openssl_command, shell=True, check=True)

        # Clean up the tar file
        os.remove(tar_path)

        log_widget.insert(tk.END, f"Encrypted file saved to {encrypted_tar_path}\n")
        messagebox.showinfo("Success", f"Encrypted file saved to {encrypted_tar_path}")
    except Exception as e:
        log_widget.insert(tk.END, f"Error: {str(e)}\n")
        messagebox.showerror("Error", str(e))

# Define the decryption function
def decrypt_folder(encrypted_name, folder_name, log_widget):
    try:
        formatted_date = get_formatted_date()
        # Full path for the encrypted file
        encrypted_tar_path = os.path.join(base_drive, f"{encrypted_name}_{formatted_date}.tar.aes")
        tar_path = os.path.join(base_drive, f"{encrypted_name}_{formatted_date}.tar")

        if not os.path.exists(encrypted_tar_path):
            log_widget.insert(tk.END, f"Encrypted file {encrypted_tar_path} does not exist. Skipping decryption.\n")
            return
        
        # Ensure the output directory exists and is correct
        output_folder = f"Decrypted_{folder_name}_{formatted_date}"
        full_output_path = os.path.join(base_drive, output_folder)
        if not os.path.exists(full_output_path):
            os.makedirs(full_output_path)
            log_widget.insert(tk.END, f"Created output directory at {full_output_path}\n")

        # Log the paths for decryption
        log_widget.insert(tk.END, f"Encrypted file path: {encrypted_tar_path}\n")
        log_widget.insert(tk.END, f"Tar file will be extracted to: {full_output_path}\n")

        # Prompt for password
        password = simpledialog.askstring("Password", "Enter decryption password:", show='*')
        if not password:
            raise ValueError("Decryption canceled, no password provided.")

        # Decrypt the tarred folder
        openssl_command = f"openssl enc -d -aes-256-cbc -pbkdf2 -iter 10000 -in {encrypted_tar_path} -out {tar_path} -pass pass:{password}"
        subprocess.run(openssl_command, shell=True, check=True)

        # Extract the tarred folder
        tar_command = f"tar -xvf {tar_path} -C {full_output_path}"
        subprocess.run(tar_command, shell=True, check=True)

        # Clean up the tar file
        os.remove(tar_path)

        log_widget.insert(tk.END, f"Decrypted and extracted file saved to {full_output_path}\n")
        messagebox.showinfo("Success", f"Decrypted and extracted file saved to {full_output_path}")
    except Exception as e:
        log_widget.insert(tk.END, f"Error: {str(e)}\n")
        messagebox.showerror("Error", str(e))

# Define the delete folder function with more detailed checks
def delete_folder(folder_path, log_widget):
    if not os.path.exists(folder_path):
        log_widget.insert(tk.END, f"Folder {folder_path} does not exist. Skipping deletion.\n")
        return

    try:
        shutil.rmtree(folder_path)
        log_widget.insert(tk.END, f"Deleted {folder_path} successfully!\n")
        messagebox.showinfo("Success", f"Deleted {folder_path} successfully!")
    except Exception as e:
        log_widget.insert(tk.END, f"Error deleting {folder_path}: {str(e)}\n")
        messagebox.showerror("Error", f"Error deleting {folder_path}: {str(e)}")

# Define function to handle folder opening with error checks
def open_folder(path):
    if not os.path.exists(path):
        messagebox.showerror("Error", f"Path {path} does not exist.")
        return
    
    try:
        os.startfile(path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open {path}: {str(e)}")

# Function to add a note label
def add_note_label(frame):
    note_text = ("NOTE: Before encrypting, ensure your data and image folders are correctly named and located.")
    note_label = tk.Label(frame, text=note_text, font=("Arial", 10), fg="white", bg="#2d2d30", wraplength=500)
    note_label.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

# GUI setup and button bindings
root = tk.Tk()
root.title("Encryption Tool")
root.geometry("635x450")  # Window size
root.configure(bg='#2d2d30')

# Layout management
frame = tk.Frame(root, padx=20, pady=20, bg='#2d2d30')
frame.pack(expand=True, fill=tk.BOTH)

# Label
title_label = tk.Label(frame, text="Encryption Tool", font=("Arial", 16, "bold"), fg="white", bg="#2d2d30")
title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="n")

# Button styles
button_style = {"font": ("Arial", 12), "padx": 5, "pady": 5, "bg": "#1c97ea", "fg": "white", "relief": tk.RAISED, "borderwidth": 2}
open_delete_button_style = {"font": ("Arial", 10), "width": 25, "padx": 5, "pady": 5, "bg": "#3f3f46", "fg": "white", "relief": tk.RAISED, "borderwidth": 2}
log_style = {"bg": "#1e1e1e", "fg": "white", "borderwidth": 2, "relief": tk.RAISED}

# Combined buttons for data and images
btn_encrypt = tk.Button(frame, text="Encrypt Data/Images", command=lambda: [encrypt_folder(data_folder_path, "Data", log_widget), encrypt_folder(images_folder_path, "Images", log_widget)], **button_style)
btn_encrypt.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

btn_decrypt = tk.Button(frame, text="Decrypt Data/Images", command=lambda: [decrypt_folder("Data", "Data", log_widget), decrypt_folder("Images", "Images", log_widget)], **button_style)
btn_decrypt.grid(row=2, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

btn_delete = tk.Button(frame, text="Delete Unencrypted Data/Images", command=lambda: [delete_folder(data_folder_path, log_widget), delete_folder(images_folder_path, log_widget)], **open_delete_button_style)
btn_delete.grid(row=3, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

btn_open_folders = tk.Button(frame, text="Open Drive", command=lambda: open_folder(base_drive), **open_delete_button_style)
btn_open_folders.grid(row=4, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

# Add note label
add_note_label(frame)

# Log area
log_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=10, font=("Arial", 10), **log_style)
log_widget.grid(row=6, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")

# Prevent unwanted resizing
frame.grid_columnconfigure(0, weight=1)
frame.grid_columnconfigure(1, weight=1)
frame.grid_rowconfigure(6, weight=1)

# Start the GUI event loop
root.mainloop()
