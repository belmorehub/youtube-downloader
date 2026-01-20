import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
from downloader import YtDlpWrapper
import os

ctk.set_appearance_mode("System")  
ctk.set_default_color_theme("blue") 

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        self.geometry(f"{700}x{500}")

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=0)

        self.logo_label = ctk.CTkLabel(self, text="YT Downloader", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, columnspan=4, padx=20, pady=(20, 10))

        self.url_label = ctk.CTkLabel(self, text="Video URL:")
        self.url_label.grid(row=1, column=0, padx=20, pady=10, sticky="e")
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Paste YouTube Link Here")
        self.url_entry.grid(row=1, column=1, columnspan=2, padx=(0, 20), pady=10, sticky="ew")

       
        self.dir_label = ctk.CTkLabel(self, text="Save to:")
        self.dir_label.grid(row=2, column=0, padx=20, pady=10, sticky="e")
        self.dir_entry = ctk.CTkEntry(self, placeholder_text="Select Download Folder")
        self.dir_entry.grid(row=2, column=1, padx=(0, 10), pady=10, sticky="ew")
        self.dir_entry.insert(0, os.getcwd()) 
        self.browse_button = ctk.CTkButton(self, text="Browse", command=self.browse_folder, width=100)
        self.browse_button.grid(row=2, column=2, padx=(0, 20), pady=10)

        
        self.format_label = ctk.CTkLabel(self, text="Format:")
        self.format_label.grid(row=3, column=0, padx=20, pady=10, sticky="e")
        self.format_option = ctk.CTkOptionMenu(self, values=["Best Video+Audio", "Audio Only (MP3)", "1080p MP4"])
        self.format_option.grid(row=3, column=1, padx=(0, 20), pady=10, sticky="w")
        self.format_option.set("Best Video+Audio")

        self.download_button = ctk.CTkButton(self, text="Download", command=self.start_download_thread)
        self.download_button.grid(row=4, column=0, columnspan=4, padx=20, pady=20)

        
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=5, column=0, columnspan=4, padx=20, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self, text="Ready")
        self.status_label.grid(row=6, column=0, columnspan=4, padx=20, pady=5)

        self.downloader = YtDlpWrapper()
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, folder)

    def start_download_thread(self):
        url = self.url_entry.get()
        path = self.dir_entry.get()
        fmt_selection = self.format_option.get()

        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        if not path:
             messagebox.showerror("Error", "Please select a save directory")
             return

      
        fmt_map = {
            "Best Video+Audio": "video",
            "Audio Only (MP3)": "audio",
            "1080p MP4": "mp4_1080p"
        }
        format_type = fmt_map.get(fmt_selection, 'video')

        self.download_button.configure(state="disabled")
        self.status_label.configure(text="Starting download...")
        self.progress_bar.set(0)

        thread = threading.Thread(target=self.run_download, args=(url, path, format_type))
        thread.start()

    def run_download(self, url, path, format_type):
        try:
            self.downloader.download(
                url=url, 
                save_path=path, 
                format_type=format_type,
                progress_callback=self.update_progress,
                completion_callback=self.on_complete,
                error_callback=self.on_error
            )
        except Exception as e:
            self.on_error(str(e))

    def update_progress(self, info):
        
        self.after(0, lambda: self._update_progress_ui(info))

    def _update_progress_ui(self, info):
        if info['status'] == 'downloading':
            p = info['percent'] / 100.0
            self.progress_bar.set(p)
            status_text = f"Downloading: {info['percent']}% | Speed: {info['speed']} | ETA: {info['eta']}"
            self.status_label.configure(text=status_text)
        elif info['status'] == 'finished':
            self.progress_bar.set(1.0)
            self.status_label.configure(text=f"Processing finished: {info['filename']}")

    def on_complete(self):
        self.after(0, lambda: self._on_complete_ui())
    
    def _on_complete_ui(self):
        self.download_button.configure(state="normal")
        self.status_label.configure(text="Download Complete!")
        messagebox.showinfo("Success", "Download completed successfully!")

    def on_error(self, error_msg):
        self.after(0, lambda: self._on_error_ui(error_msg))

    def _on_error_ui(self, error_msg):
        self.download_button.configure(state="normal")
        self.status_label.configure(text=f"Error: {error_msg}")
        messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    app = App()
    app.mainloop()
