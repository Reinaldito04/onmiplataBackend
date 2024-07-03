import uvicorn
import socket
import tkinter as tk
from tkinter import messagebox

def get_local_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except socket.error as e:
        local_ip = f"Unable to get local IP: {e}"
    return local_ip

def get_network_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            network_ip = s.getsockname()[0]
        except Exception as e:
            network_ip = f"Unable to get network IP: {e}"
    return network_ip

def show_ip_dialog(local_ip, network_ip):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Server IP Information", f"Local IP: {local_ip}\nNetwork IP: {network_ip}:8000")

if __name__ == "__main__":
    local_ip = get_local_ip()
    network_ip = get_network_ip()
    show_ip_dialog(local_ip, network_ip)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
