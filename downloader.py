import yt_dlp
import os

class YtDlpWrapper:
    def __init__(self):
        self._cancel_requested = False

    def download(self, url, save_path, format_type='video', progress_callback=None, completion_callback=None, error_callback=None):
        """
        Downloads media from the given URL.
        
        Args:
            url (str): YouTube URL.
            save_path (str): Directory to save the file.
            format_type (str): 'video' (best video+audio), 'audio' (mp3), or 'mp4_1080p'.
            progress_callback (callable): Function to call with progress dict.
            completion_callback (callable): Function to call when finished.
            error_callback (callable): Function to call on error.
        """
        self._cancel_requested = False
        
        ydl_opts = {
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: self._my_hook(d, progress_callback)],
                }

        if format_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        elif format_type == 'mp4_1080p':
             ydl_opts.update({
                'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            })
        else: 
            ydl_opts.update({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if completion_callback:
                completion_callback()
        except Exception as e:
            if error_callback:
                error_callback(str(e))
            else:
                print(f"Error: {e}")

    def _my_hook(self, d, progress_callback):
        if self._cancel_requested:
            raise Exception("Download cancelled by user")
            
        if d['status'] == 'downloading':
            if progress_callback:
               
                p = d.get('_percent_str', '0%').replace('%', '')
                try:
                    percent = float(p)
                except ValueError:
                    percent = 0.0
                
                info = {
                    'status': 'downloading',
                    'percent': percent,
                    'filename': d.get('filename', 'Unknown'),
                    'eta': d.get('_eta_str', 'Unknown'),
                    'speed': d.get('_speed_str', 'Unknown')
                }
                progress_callback(info)
        elif d['status'] == 'finished':
            if progress_callback:
                progress_callback({
                    'status': 'finished',
                    'percent': 100.0,
                    'filename': d.get('filename', 'Unknown')
                })

    def cancel(self):
        self._cancel_requested = True
