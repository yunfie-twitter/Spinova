from PyQt5.QtCore import QThread, pyqtSignal
from engine.downloader import VideoDownloader

class DownloadThread(QThread):
    progress = pyqtSignal(dict)

    def __init__(self, url, format_code, output_dir, ffmpeg_path=None, yt_dlp_opts=None):
        super().__init__()
        self.url = url
        self.format_code = format_code
        self.output_dir = output_dir
        self.ffmpeg_path = ffmpeg_path
        self.yt_dlp_opts = yt_dlp_opts

    def run(self):
        def progress_cb(d):
            self.progress.emit(d)
        try:
            downloader = VideoDownloader(
                progress_callback=progress_cb,
                ffmpeg_path=self.ffmpeg_path,
                yt_dlp_extra_opts=self.yt_dlp_opts,
            )
            downloader.download_video(self.url, output_dir=self.output_dir, format_code=self.format_code)
        except Exception as e:
            self.progress.emit({
                'status': 'error',
                'error': str(e),
                'url': self.url,
            })
