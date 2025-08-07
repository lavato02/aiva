import tkinter as tk
from tkinter import ttk
import threading
from core.aiva_runner import AivaRunner

class AivaUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Aiva Kontrol Paneli v2.2")
        
        # Widgetlar
        self.cmd_entry = tk.Text(root, height=5, width=60)
        self.start_btn = ttk.Button(root, text="Başlat (F9)", command=self.start_aiva)
        self.stop_btn = ttk.Button(root, text="Durdur (F10)", command=self.stop_aiva, state=tk.DISABLED)
        self.log_text = tk.Text(root, height=15, state=tk.DISABLED)
        
        # Yerleşim
        self.cmd_entry.pack(pady=10)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        self.log_text.pack(pady=10)
        
        # Aiva Kontrolcü
        self.aiva_runner = AivaRunner(self.update_log)
        self._aiva_thread = None
        
        # Kısayollar
        self.root.bind("<F9>", lambda e: self.start_aiva())
        self.root.bind("<F10>", lambda e: self.stop_aiva())

    def start_aiva(self):
        if self.aiva_runner.is_running:
            return
            
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        custom_prompt = self.cmd_entry.get("1.0", tk.END).strip()
        self._aiva_thread = threading.Thread(
            target=self.aiva_runner.start,
            args=(custom_prompt,),
            daemon=True
        )
        self._aiva_thread.start()
        self.monitor_thread()

    def monitor_thread(self):
        if self._aiva_thread.is_alive():
            self.root.after(500, self.monitor_thread)
        else:
            self.stop_btn.invoke()

    def stop_aiva(self):
        if not self.aiva_runner.is_running:
            return
            
        self.stop_btn.config(state=tk.DISABLED)
        self.aiva_runner.stop()
        
        if self._aiva_thread:
            self._aiva_thread.join(timeout=2.0)
            
        self.start_btn.config(state=tk.NORMAL)

    def update_log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

def run_ui():
    root = tk.Tk()
    root.geometry("800x600")
    AivaUI(root)
    root.mainloop()