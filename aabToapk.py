import os
import sys
import tempfile
import shutil
import subprocess
import pkg_resources
import tkinter as tk
import zipfile
from tkinter import filedialog, messagebox

def get_bundletool_path():
    bundletool_jar = pkg_resources.resource_string(__name__, 'resources/bundletool.jar')
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jar')
    with open(temp_file.name, 'wb') as f:
        f.write(bundletool_jar)
    return temp_file.name

def convert_aab_to_apks(aab_path, apks_path, keystore_path, keystore_password, key_alias, key_password):
    bundletool_path = get_bundletool_path()
    try:
        command = [
            'java', '-jar', bundletool_path, 'build-apks',
            '--bundle=' + aab_path,
            '--output=' + apks_path,
            '--ks=' + keystore_path,
            '--ks-pass=pass:' + keystore_password,
            '--key-pass=pass:' + key_password,
            '--ks-key-alias=' + key_alias,
            '--mode=universal'
        ]
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        os.remove(bundletool_path)

def extract_apk_from_apks(apks_path, apk_output_folder):
    try:
        with zipfile.ZipFile(apks_path, 'r') as zip_ref:
            apk_files = [file for file in zip_ref.namelist() if file.endswith('.apk')]
            if not apk_files:
                raise ValueError("No APK files found in APKS file.")
            for file in apk_files:
                apk_output_path = os.path.join(apk_output_folder, "extracted.apk")
                zip_ref.extract(file, apk_output_folder)
                os.rename(os.path.join(apk_output_folder, file), apk_output_path)
                return apk_output_path
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
        
def browse_file(entry):
    filename = filedialog.askopenfilename()
    if filename:
        entry.delete(0, tk.END)
        entry.insert(0, filename)

def browse_save_file(entry):
    filename = filedialog.asksaveasfilename(defaultextension=".apks", filetypes=[("APKS files", "*.apks")])
    if filename:
        entry.delete(0, tk.END)
        entry.insert(0, filename)

def browse_folder(entry):
    foldername = filedialog.askdirectory()
    if foldername:
        entry.delete(0, tk.END)
        entry.insert(0, foldername)

def process_files():
    aab_path = aab_path_entry.get()
    apks_path = apks_path_entry.get()
    apk_output_folder = apk_folder_entry.get()
    keystore_path = keystore_path_entry.get()
    keystore_password = keystore_password_entry.get()
    key_alias = key_alias_entry.get()
    key_password = key_password_entry.get()

    if not (aab_path and apks_path and apk_output_folder and keystore_path and keystore_password and key_alias and key_password):
        messagebox.showerror("Error", "Please provide all required fields.")
        return

    # Convert AAB to APKS
    if not convert_aab_to_apks(aab_path, apks_path, keystore_path, keystore_password, key_alias, key_password):
        messagebox.showerror("Error", "Failed to convert AAB to APKS.")
        return

    # Extract APK from APKS
    apk_file_path = extract_apk_from_apks(apks_path, apk_output_folder)
    if not apk_file_path:
        messagebox.showerror("Error", "Failed to extract APK from APKS.")
        return

    messagebox.showinfo("Success", f"APK extracted successfully. Saved to {apk_file_path}")

# GUI 설정
root = tk.Tk()
root.title("AAB to APK Converter")

tk.Label(root, text="AAB File:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
aab_path_entry = tk.Entry(root, width=50)
aab_path_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: browse_file(aab_path_entry)).grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="APKS File:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.E)
apks_path_entry = tk.Entry(root, width=50)
apks_path_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Save as", command=lambda: browse_save_file(apks_path_entry)).grid(row=1, column=2, padx=10, pady=5)

tk.Label(root, text="APK File Directory:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.E)
apk_folder_entry = tk.Entry(root, width=50)
apk_folder_entry.grid(row=2, column=1, padx=10, pady=5)
tk.Button(root, text="Save as", command=lambda: browse_folder(apk_folder_entry)).grid(row=2, column=2, padx=10, pady=5)

tk.Label(root, text="Keystore File:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.E)
keystore_path_entry = tk.Entry(root, width=50)
keystore_path_entry.grid(row=3, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", command=lambda: browse_file(keystore_path_entry)).grid(row=3, column=2, padx=10, pady=5)

tk.Label(root, text="Keystore Password:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.E)
keystore_password_entry = tk.Entry(root, show="*", width=50)
keystore_password_entry.grid(row=4, column=1, padx=10, pady=5)

tk.Label(root, text="Key Alias:").grid(row=5, column=0, padx=10, pady=5, sticky=tk.E)
key_alias_entry = tk.Entry(root, width=50)
key_alias_entry.grid(row=5, column=1, padx=10, pady=5)

tk.Label(root, text="Key Password:").grid(row=6, column=0, padx=10, pady=5, sticky=tk.E)
key_password_entry = tk.Entry(root, show="*", width=50)
key_password_entry.grid(row=6, column=1, padx=10, pady=5)

tk.Button(root, text="Convert", command=process_files).grid(row=7, column=1, padx=10, pady=10)

root.mainloop()
