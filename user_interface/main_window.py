import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QMenuBar, QMenu, QAction, QFileDialog, QMessageBox,
    QProgressBar, QCheckBox
)
from PyQt5.QtCore import QThread, pyqtSignal
from engine.downloader import VideoDownloader
from engine.plugins import PluginManager
from .dialog_settings import SettingsDialog
from .download_thread import DownloadThread
from config.config_manager import ConfigManager
from .download_batch_thread import DownloadBatchThread
import version
import json
import csv
import sys
import os

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.app_version = version.__version__
        self.config_manager = ConfigManager()
        self.plugin_manager = PluginManager()
        self.load_config()
        self.init_ui()

    # ========= 設定読み込み =========
    def load_config(self):
        self.output_dir = self.config_manager.get("output_dir", "downloads")
        self.ffmpeg_path = self.config_manager.get("ffmpeg_path", "")
        self.enabled_plugins = self.config_manager.get("enabled_plugins", [])
        yt_dlp_opts_str = self.config_manager.get("yt_dlp_opts", "")
        try:
            self.yt_dlp_opts = json.loads(yt_dlp_opts_str) if yt_dlp_opts_str else {}
        except:
            self.yt_dlp_opts = {}

    # ========= UI初期化 =========
    def init_ui(self):
        self.setWindowTitle(f"Spinova v{self.app_version}")

        self.menu_bar = QMenuBar(self)
        self.init_menu()

        self.url_input = QLineEdit(self)
        self.format_combo = QComboBox(self)
        self.load_formats()
        self.download_btn = QPushButton("ダウンロード", self)
        self.download_btn.clicked.connect(self.start_download)
        self.status_label = QLabel("", self)
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        self.show_bytes_cb = QCheckBox("Bytes表示を有効にする", self)
        self.show_bytes_cb.setChecked(True)
        self.show_bytes_cb.setVisible(False)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        main_layout = QVBoxLayout()
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addWidget(QLabel("動画URL:"))
        main_layout.addWidget(self.url_input)
        main_layout.addLayout(self.init_format_layout())
        main_layout.addLayout(self.init_output_dir_layout())
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.show_bytes_cb)
        main_layout.addWidget(self.download_btn)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.log_area)
        self.setLayout(main_layout)

    # ========= メニューバー初期化とバージョン情報 =========
    def init_menu(self):
        file_menu = QMenu("ファイル", self)
        settings_action = QAction("設定", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        file_menu.addAction(settings_action)
        batch_download_action = QAction("CSV一括ダウンロード", self)
        batch_download_action.triggered.connect(self.open_csv_batch_dialog)
        file_menu.addAction(batch_download_action)

        help_menu = QMenu("ヘルプ", self)
        version_action = QAction("バージョン情報", self)
        version_action.triggered.connect(self.show_version_info)
        help_menu.addAction(version_action)

        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(help_menu)

    def show_version_info(self):
        QMessageBox.information(self, "バージョン情報", f"Spinova バージョン: {self.app_version}")

    # ========= 各UI部品のレイアウト分離 =========
    def init_format_layout(self):
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel("フォーマット選択:"))
        fmt_layout.addWidget(self.format_combo)
        return fmt_layout

    def init_output_dir_layout(self):
        out_layout = QHBoxLayout()
        self.output_dir_label = QLabel(f"保存先: {self.output_dir}", self)
        self.change_output_btn = QPushButton("保存先変更", self)
        self.change_output_btn.clicked.connect(self.open_output_dir_dialog)
        out_layout.addWidget(self.output_dir_label)
        out_layout.addWidget(self.change_output_btn)
        return out_layout

    # ========= フォーマットリスト読み込み =========
    def load_formats(self):
        formats = {
            "MP4 (動画+音声)": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "MP3 (音声のみ)": "bestaudio[ext=m4a]/bestaudio",
        }
        plugin_formats = {}
        for name in self.enabled_plugins:
            if name in self.plugin_manager.formats:
                plugin_formats[name] = self.plugin_manager.formats[name]
        combined_formats = {**formats, **plugin_formats}
        self.format_combo.clear()
        for name in combined_formats.keys():
            self.format_combo.addItem(name)

    # ========= 設定ダイアログ表示 =========
    def open_settings_dialog(self):
        dialog = SettingsDialog(
            self,
            current_output=self.output_dir,
            plugin_manager=self.plugin_manager,
            current_ffmpeg_path=self.ffmpeg_path,
            current_yt_dlp_opts=self.yt_dlp_opts,
        )
        if dialog.exec_():
            opts = dialog.get_yt_dlp_opts()
            self.yt_dlp_opts = opts
            self.output_dir = opts.get("output_dir", self.output_dir)
            self.ffmpeg_path = dialog.get_ffmpeg_path()
            self.status_label.setText("設定を更新しました。")
            self.output_dir_label.setText(f"保存先: {self.output_dir}")
            self.config_manager.set("output_dir", self.output_dir)
            self.config_manager.set("ffmpeg_path", self.ffmpeg_path)
            self.config_manager.set("enabled_plugins", self.enabled_plugins)
            self.config_manager.set("yt_dlp_opts", json.dumps(self.yt_dlp_opts, ensure_ascii=False))
            self.config_manager.save()

    # ========= ダウンロード先ディレクトリ選択 =========
    def open_output_dir_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "保存先フォルダ選択", self.output_dir)
        if folder:
            self.output_dir = folder
            self.output_dir_label.setText(f"保存先: {folder}")
            self.status_label.setText(f"保存先を {folder} に変更しました")

    # ========= 通常ダウンロード =========
    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("URLを入力してください。")
            return
        selected_fmt_name = self.format_combo.currentText()
        format_code = self.plugin_manager.get_all_formats().get(selected_fmt_name, "bestvideo+bestaudio/best")
        self.status_label.setText("ダウンロード開始...")
        self.download_btn.setEnabled(False)
        self.log_area.clear()
        self.progress_bar.setValue(0)
        self.thread = DownloadThread(
            url,
            format_code,
            output_dir=self.output_dir,
            ffmpeg_path=self.ffmpeg_path,
            yt_dlp_opts=self.yt_dlp_opts,
        )
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.download_finished)
        self.thread.start()

    # ========= 進捗UI更新 =========
    def update_progress(self, data):
        now = time.time()
        if not hasattr(self, '_last_update_time'):
            self._last_update_time = 0
        if now - self._last_update_time < 0.1:
            return
        self._last_update_time = now
        status = data.get("status")
        if status == "downloading":
            total_bytes = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded_bytes = data.get("downloaded_bytes", 0)
            if total_bytes and total_bytes > 0:
                percent = int(downloaded_bytes / total_bytes * 100)
                self.progress_bar.setValue(percent)
                if self.show_bytes_cb.isChecked():
                    msg = f"Downloading: {percent}% ({downloaded_bytes}/{total_bytes} bytes)"
                else:
                    msg = f"Downloading: {percent}%"
            else:
                if self.show_bytes_cb.isChecked():
                    msg = f"Downloading: {downloaded_bytes} bytes"
                else:
                    msg = "Downloading..."
        elif status == "finished":
            self.progress_bar.setValue(100)
            msg = "ダウンロード完了"
        elif status == "error":
            msg = "エラーが発生しました"
        else:
            msg = ""
        self.status_label.setText(msg)
        self.log_area.append(msg)

    # ========= 通常DL終了UI更新 =========
    def download_finished(self):
        self.download_btn.setEnabled(True)
        self.status_label.setText("ダウンロードが終了しました。")

    # ========= CSV一括ダウンロード =========
    def open_csv_batch_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "CSVファイルを選択", "", "CSV files (*.csv)")
        if not path:
            return
        try:
            urls = []
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) > 0:
                        url = row[0].strip()
                        if url.startswith("http"):
                            urls.append(url)
            if not urls:
                QMessageBox.warning(self, "警告", "CSVに有効なURLがありません。")
                return
            self.start_batch_download(urls)
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"CSV読み込み失敗: {e}")

    def start_batch_download(self, urls):
        if not urls:
            self.status_label.setText("ダウンロードするURLがありません。")
            return
        self.status_label.setText(f"{len(urls)}件のダウンロードを開始します。")
        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        format_code = self.plugin_manager.get_all_formats().get(
            self.format_combo.currentText(), "bestvideo+bestaudio/best"
        )
        self.batch_thread = DownloadBatchThread(
            urls,
            output_dir=self.output_dir,
            format_code=format_code,
            ffmpeg_path=self.ffmpeg_path,
            yt_dlp_opts=self.yt_dlp_opts,
        )
        self.batch_thread.progress.connect(self.append_log)
        self.batch_thread.finished_batch.connect(self.batch_download_finished)
        self.batch_thread.start()

    def append_log(self, message):
        self.log_area.append(message)
        self.status_label.setText(message)

    def batch_download_finished(self):
        self.status_label.setText("一括ダウンロードが終了しました。")
        self.download_btn.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

