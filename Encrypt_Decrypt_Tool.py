import os
import subprocess
import shutil
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from datetime import datetime
import threading

# Thread lock to prevent race conditions
lock = threading.Lock()

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
    with lock:
        if not os.path.exists(folder_path):
            log_widget.insert(ctk.END, f"Folder {folder_path} does not exist. Skipping encryption.\n")
            return

        try:
            formatted_date = get_formatted_date()
            tar_path = os.path.join(base_drive, f"{encrypted_name}_{formatted_date}.tar")
            encrypted_tar_path = os.path.join(base_drive, f"{encrypted_name}_{formatted_date}.tar.aes")

            log_widget.insert(ctk.END, f"Tar file will be saved to: {tar_path}\n")
            log_widget.insert(ctk.END, f"Encrypted file will be saved to: {encrypted_tar_path}\n")

            tar_command = f"tar -cvf {tar_path} -C {os.path.dirname(folder_path)} {os.path.basename(folder_path)}"
            subprocess.run(tar_command, shell=True, check=True)

            password = simpledialog.askstring("Password", "Enter encryption password:", show='*')
            if not password:
                raise ValueError("Encryption canceled, no password provided.")

            openssl_command = f"openssl enc -aes-256-cbc -salt -pbkdf2 -iter 10000 -in {tar_path} -out {encrypted_tar_path} -pass pass:{password}"
            subprocess.run(openssl_command, shell=True, check=True)

            os.remove(tar_path)

            log_widget.insert(ctk.END, f"Encrypted file saved to {encrypted_tar_path}\n")
            messagebox.showinfo("Success", f"Encrypted file saved to {encrypted_tar_path}")
        except Exception as e:
            log_widget.insert(ctk.END, f"Error: {str(e)}\n")
            messagebox.showerror("Error", str(e))

# Define the decryption function
def decrypt_folder(encrypted_name, folder_name, log_widget):
    with lock:
        try:
            formatted_date = get_formatted_date()
            encrypted_tar_path = os.path.join(base_drive, f"{encrypted_name}_{formatted_date}.tar.aes")
            tar_path = os.path.join(base_drive, f"{encrypted_name}_{formatted_date}.tar")

            if not os.path.exists(encrypted_tar_path):
                log_widget.insert(ctk.END, f"Encrypted file {encrypted_tar_path} does not exist. Skipping decryption.\n")
                return

            output_folder = f"Decrypted_{folder_name}_{formatted_date}"
            full_output_path = os.path.join(base_drive, output_folder)
            if not os.path.exists(full_output_path):
                os.makedirs(full_output_path)
                log_widget.insert(ctk.END, f"Created output directory at {full_output_path}\n")

            log_widget.insert(ctk.END, f"Encrypted file path: {encrypted_tar_path}\n")
            log_widget.insert(ctk.END, f"Tar file will be extracted to: {full_output_path}\n")

            password = simpledialog.askstring("Password", "Enter decryption password:", show='*')
            if not password:
                raise ValueError("Decryption canceled, no password provided.")

            openssl_command = f"openssl enc -d -aes-256-cbc -pbkdf2 -iter 10000 -in {encrypted_tar_path} -out {tar_path} -pass pass:{password}"
            subprocess.run(openssl_command, shell=True, check=True)

            tar_command = f"tar -xvf {tar_path} -C {full_output_path}"
            subprocess.run(tar_command, shell=True, check=True)

            os.remove(tar_path)

            log_widget.insert(ctk.END, f"Decrypted and extracted file saved to {full_output_path}\n")
            messagebox.showinfo("Success", f"Decrypted and extracted file saved to {full_output_path}")
        except Exception as e:
            log_widget.insert(ctk.END, f"Error: {str(e)}\n")
            messagebox.showerror("Error", str(e))

# Define the delete folder function
def delete_folder(folder_path, log_widget):
    with lock:
        if not os.path.exists(folder_path):
            log_widget.insert(ctk.END, f"Folder {folder_path} does not exist. Skipping deletion.\n")
            return

        try:
            shutil.rmtree(folder_path)
            log_widget.insert(ctk.END, f"Deleted {folder_path} successfully!\n")
            messagebox.showinfo("Success", f"Deleted {folder_path} successfully!")
        except Exception as e:
            log_widget.insert(ctk.END, f"Error deleting {folder_path}: {str(e)}\n")
            messagebox.showerror("Error", f"Error deleting {folder_path}: {str(e)}")

# Define function to handle folder opening
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
    note_text = "NOTE: Before encrypting, ensure your data and image folders are correctly named and located."
    note_label = ctk.CTkLabel(frame, text=note_text, font=("Arial", 10))
    note_label.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")

# Function to run the encryption or decryption in a separate thread
def run_in_thread(target, *args):
    thread = threading.Thread(target=target, args=args)
    thread.start()

# GUI setup using customtkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Encryption Tool")
root.geometry("635x500")  # Window size

# Frame setup
frame = ctk.CTkFrame(root)
frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

# Title Label
title_label = ctk.CTkLabel(frame, text="Encryption Tool", font=ctk.CTkFont(size=20, weight="bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="n")

# Button style with specified color
button_style = {"fg_color": "#6e9ccc", "hover_color": "#4b76a3"}

# Encrypt Button
btn_encrypt = ctk.CTkButton(frame, text="Encrypt Data/Images", command=lambda: run_in_thread(lambda: [encrypt_folder(data_folder_path, "Data", log_widget), encrypt_folder(images_folder_path, "Images", log_widget)]), **button_style)
btn_encrypt.grid(row=1, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

# Decrypt Button
btn_decrypt = ctk.CTkButton(frame, text="Decrypt Data/Images", command=lambda: run_in_thread(lambda: [decrypt_folder("Data", "Data", log_widget), decrypt_folder("Images", "Images", log_widget)]), **button_style)
btn_decrypt.grid(row=2, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

# Delete Button
btn_delete = ctk.CTkButton(frame, text="Delete Unencrypted Data/Images", command=lambda: run_in_thread(lambda: [delete_folder(data_folder_path, log_widget), delete_folder(images_folder_path, log_widget)]), **button_style)
btn_delete.grid(row=3, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

# Open Drive Button
btn_open_folders = ctk.CTkButton(frame, text="Open Drive", command=lambda: run_in_thread(open_folder, base_drive), **button_style)
btn_open_folders.grid(row=4, column=0, columnspan=2, pady=5, padx=10, sticky="ew")

# Add note label
add_note_label(frame)

# Log area
log_widget = ctk.CTkTextbox(frame, wrap="word", height=10)
log_widget.grid(row=6, column=0, columnspan=2, pady=5, padx=5, sticky="nsew")

# Adjust grid configuration
frame.grid_columnconfigure(0, weight=1)
frame.grid_rowconfigure(6, weight=1)

# Start the GUI event loop
root.mainloop()
