import os
import yt_dlp

class VideoDownloader:
    def __init__(self, progress_callback=None, ffmpeg_path=None, yt_dlp_extra_opts=None, cookie_path=None):
        self.progress_callback = progress_callback
        self.ffmpeg_path = ffmpeg_path
        self.yt_dlp_extra_opts = yt_dlp_extra_opts or {}
        self.cookie_path = cookie_path or os.path.join(os.getcwd(), 'cookie.txt')

    def download_video(self, url: str, output_dir: str = "downloads", format_code: str = "bestvideo+bestaudio/best"):
        # 出力ディレクトリがなければ作成
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        ydl_opts = {
            'format': format_code,
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'ignoreerrors': True,
            'progress_hooks': [self._progress_hook] if self.progress_callback else [],
        }

        if self.ffmpeg_path:
            ydl_opts['ffmpeg_location'] = self.ffmpeg_path

        if os.path.exists(self.cookie_path):
            ydl_opts['cookiefile'] = self.cookie_path

        if self.yt_dlp_extra_opts:
            ydl_opts.update(self.yt_dlp_extra_opts)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except yt_dlp.utils.DownloadError as e:
            self._handle_error('DownloadError', str(e), url)
        except yt_dlp.utils.ExtractorError as e:
            self._handle_error('ExtractorError', str(e), url)
        except Exception as e:
            self._handle_error('UnknownError', str(e), url)

    def _progress_hook(self, d):
        if self.progress_callback:
            try:
                self.progress_callback(d)
            except Exception as e:
                # コールバック内例外は抑制しつつ報告
                print(f"Progress callback error: {e}")

    def _handle_error(self, error_type, error_message, url):
        if self.progress_callback:
            self.progress_callback({
                'status': 'error',
                'error_type': error_type,
                'error': error_message,
                'url': url,
            })
        else:
            raise Exception(f"[{error_type}] {error_message}")
