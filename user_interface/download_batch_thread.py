from PyQt5.QtCore import QThread, pyqtSignal
from engine.downloader import VideoDownloader

class DownloadBatchThread(QThread):
    progress = pyqtSignal(str)  # ログ文字列をGUIへ送信
    finished_batch = pyqtSignal()

    def __init__(self, urls, output_dir, format_code, ffmpeg_path=None, yt_dlp_opts=None):
        super().__init__()
        self.urls = urls
        self.output_dir = output_dir
        self.format_code = format_code
        self.ffmpeg_path = ffmpeg_path
        self.yt_dlp_opts = yt_dlp_opts

    def run(self):
        downloader = VideoDownloader(
            ffmpeg_path=self.ffmpeg_path,
            yt_dlp_extra_opts=self.yt_dlp_opts,
        )

        for url in self.urls:
            try:
                self.progress.emit(f"ダウンロード開始: {url}")
                downloader.download_video(url, output_dir=self.output_dir, format_code=self.format_code)
                self.progress.emit(f"ダウンロード成功: {url}")
            except Exception as e:
                self.progress.emit(f"ダウンロード失敗: {url} エラー: {e}")

        self.finished_batch.emit()
