import os
import yt_dlp

class VideoDownloader:
    def __init__(self, progress_callback=None, ffmpeg_path=None, yt_dlp_extra_opts=None):
        self.progress_callback = progress_callback
        self.ffmpeg_path = ffmpeg_path
        self.yt_dlp_extra_opts = yt_dlp_extra_opts or {}

    def download_video(self, url: str, output_dir: str = "downloads", format_code: str = "bestvideo+bestaudio/best"):
        ydl_opts = {
            'format': format_code,
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'progress_hooks': [self._progress_hook] if self.progress_callback else [],
            'ignoreerrors': True,
        }

        if self.ffmpeg_path:
            ydl_opts['ffmpeg_location'] = self.ffmpeg_path

        cookie_path = os.path.join(os.getcwd(), 'cookie.txt')
        if os.path.exists(cookie_path):
            ydl_opts['cookiefile'] = cookie_path

        if self.yt_dlp_extra_opts:
            ydl_opts.update(self.yt_dlp_extra_opts)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            # エラー発生時にprogress_callbackへエラー情報を送る
            if self.progress_callback:
                self.progress_callback({
                    'status': 'error',
                    'error': str(e),
                    'url': url,
                })
            else:
                # コールバックが設定されていなければ例外を再送出
                raise

    def _progress_hook(self, d):
        if self.progress_callback:
            self.progress_callback(d)
