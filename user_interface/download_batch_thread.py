from PyQt5.QtCore import QThread, pyqtSignal
from engine.downloader import VideoDownloader
import traceback

class DownloadBatchThread(QThread):
    progress = pyqtSignal(str)  # ログ文字列をGUIへ送信
    finished_batch = pyqtSignal(bool)  # 成功/失敗フラグ付き
    error_occurred = pyqtSignal(str)  # 致命的エラー通知

    def __init__(self, urls, output_dir, format_code, ffmpeg_path=None, yt_dlp_opts=None):
        super().__init__()
        self.urls = urls
        self.output_dir = output_dir
        self.format_code = format_code
        self.ffmpeg_path = ffmpeg_path
        self.yt_dlp_opts = yt_dlp_opts

    def run(self):
        success_count = 0
        error_count = 0
        
        try:
            downloader = VideoDownloader(
                ffmpeg_path=self.ffmpeg_path,
                yt_dlp_extra_opts=self.yt_dlp_opts,
            )
            
            total_urls = len(self.urls)
            
            for i, url in enumerate(self.urls, 1):
                try:
                    self.progress.emit(f"[{i}/{total_urls}] ダウンロード開始: {url}")
                    downloader.download_video(url, output_dir=self.output_dir, format_code=self.format_code)
                    success_count += 1
                    self.progress.emit(f"[{i}/{total_urls}] ダウンロード成功: {url}")
                    
                except Exception as e:
                    error_count += 1
                    error_msg = f"[{i}/{total_urls}] ダウンロード失敗: {url} エラー: {str(e)}"
                    self.progress.emit(error_msg)
                    
                    # デバッグ用の詳細エラー情報（必要に応じて）
                    if hasattr(e, '__traceback__'):
                        tb_lines = traceback.format_exception(type(e), e, e.__traceback__)
                        tb_summary = ''.join(tb_lines[-3:]).strip()  # 最後の3行のみ
                        self.progress.emit(f"詳細エラー: {tb_summary}")

            # 完了サマリー
            self.progress.emit(f"バッチ処理完了 - 成功: {success_count}, 失敗: {error_count}")
            
        except Exception as fatal_error:
            # 致命的エラー（ダウンローダー作成失敗など）
            error_msg = f"バッチ処理中に致命的なエラーが発生: {str(fatal_error)}"
            self.progress.emit(error_msg)
            self.error_occurred.emit(error_msg)
            self.finished_batch.emit(False)
            return
            
        finally:
            # 必ず終了シグナルを送信
            success = error_count == 0
            self.finished_batch.emit(success)
