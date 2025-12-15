import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import sys

def get_available_cameras():
    """
    Test the ports and returns a list of available ports and their names (if possible).
    """
    current_camera_index = 0
    available_cameras = []
    
    # Check first 10 indexes
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available_cameras.append(i)
            cap.release()
    return available_cameras

class CameraLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCII Face Cam - Launcher")
        self.root.geometry("400x300")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Title
        title_label = ttk.Label(root, text="Select Your Camera", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=20)
        
        # Camera List
        self.camera_var = tk.StringVar()
        self.combo = ttk.Combobox(root, textvariable=self.camera_var, state="readonly")
        self.combo.pack(pady=10)
        
        # Refresh Button
        self.scan_btn = ttk.Button(root, text="Scan Cameras", command=self.scan_cameras)
        self.scan_btn.pack(pady=5)
        
        # Launch Button
        self.launch_btn = ttk.Button(root, text="Launch ASCII Mode", command=self.launch, state="disabled")
        self.launch_btn.pack(pady=20)
        
        # Initial Scan
        self.root.after(100, self.scan_cameras)

    def scan_cameras(self):
        self.combo.set("Scanning...")
        self.root.update()
        
        cams = get_available_cameras()
        
        if cams:
            self.combo['values'] = [f"Camera {i}" for i in cams]
            self.combo.current(0)
            self.launch_btn.config(state="normal")
        else:
            self.combo['values'] = ["No cameras found"]
            self.combo.set("No cameras found")
            self.launch_btn.config(state="disabled")

    def launch(self):
        selection = self.combo.get()
        if not selection or "Camera" not in selection:
            return
            
        # Extract index
        try:
            index = int(selection.split(" ")[1])
            # Print index to stdout so Go can read it
            print(index)
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid selection: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraLauncher(root)
    root.mainloop()
