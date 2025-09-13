import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QMenuBar, QMenu, QAction, QFileDialog, QMessageBox,
    QProgressBar, QCheckBox, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from engine.downloader import VideoDownloader
from engine.plugins import PluginManager
from .dialog_settings import SettingsDialog
from .download_thread import DownloadThread
from config.config_manager import ConfigManager
from .download_batch_thread import DownloadBatchThread
from config.i18n import I18N
import version
import json
import csv
import sys
import os

class LanguageDialog(QDialog):
    def __init__(self, parent, i18n):
        super().__init__(parent)
        self.i18n = i18n
        self.selected_locale = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.i18n.t("dialog_language_title"))
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel(self.i18n.t("dialog_language_text")))
        
        self.combo = QComboBox()
        available_locales = self.i18n.get_available_locales()
        
        for locale in available_locales:
            temp_i18n = I18N(locale)
            lang_name = temp_i18n.get_language_name()
            self.combo.addItem(f"{lang_name} ({locale})", locale)
        
        layout.addWidget(self.combo)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def accept(self):
        self.selected_locale = self.combo.currentData()
        super().accept()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.app_version = version.__version__
        self.config_manager = ConfigManager()
        self.plugin_manager = PluginManager()
        
        # 言語設定読み込み
        saved_locale = self.config_manager.get("locale", "ja")
        self.i18n = I18N(saved_locale)
        
        # スレッド追跡とタイマー初期化
        self.current_thread = None
        self.current_batch_thread = None
        self.ui_recovery_timer = QTimer()
        self.ui_recovery_timer.timeout.connect(self.force_ui_recovery)
        self.ui_recovery_timer.setSingleShot(True)
        
        self.load_config()
        self.init_ui()

    def load_config(self):
        self.output_dir = self.config_manager.get("output_dir", "downloads")
        self.ffmpeg_path = self.config_manager.get("ffmpeg_path", "")
        self.enabled_plugins = self.config_manager.get("enabled_plugins", [])
        yt_dlp_opts_str = self.config_manager.get("yt_dlp_opts", "")
        try:
            self.yt_dlp_opts = json.loads(yt_dlp_opts_str) if yt_dlp_opts_str else {}
        except:
            self.yt_dlp_opts = {}

    def init_ui(self):
        self.setWindowTitle(f"{self.i18n.t('window_title')} v{self.app_version}")
        self.menu_bar = QMenuBar(self)
        self.init_menu()

        self.url_input = QLineEdit(self)
        self.format_combo = QComboBox(self)
        self.load_formats()

        self.download_btn = QPushButton(self.i18n.t("button_download"), self)
        self.download_btn.clicked.connect(self.start_download)

        self.status_label = QLabel("", self)
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)

        self.show_bytes_cb = QCheckBox(self.i18n.t("bytes_display_enable"), self)
        self.show_bytes_cb.setChecked(True)
        self.show_bytes_cb.setVisible(False)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        main_layout = QVBoxLayout()
        main_layout.setMenuBar(self.menu_bar)
        main_layout.addWidget(QLabel(self.i18n.t("label_video_url")))
        main_layout.addWidget(self.url_input)
        main_layout.addLayout(self.init_format_layout())
        main_layout.addLayout(self.init_output_dir_layout())
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.show_bytes_cb)
        main_layout.addWidget(self.download_btn)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.log_area)

        self.setLayout(main_layout)

    def init_menu(self):
        file_menu = QMenu(self.i18n.t("menu_file"), self)
        settings_action = QAction(self.i18n.t("action_settings"), self)
        settings_action.triggered.connect(self.open_settings_dialog)
        file_menu.addAction(settings_action)

        batch_download_action = QAction(self.i18n.t("action_csv_batch"), self)
        batch_download_action.triggered.connect(self.open_csv_batch_dialog)
        file_menu.addAction(batch_download_action)

        file_menu.addSeparator()

        language_action = QAction(self.i18n.t("action_language"), self)
        language_action.triggered.connect(self.open_language_dialog)
        file_menu.addAction(language_action)

        # ログ表示切替メニューを追加
        self.toggle_log_action = QAction(self.i18n.t("action_toggle_log"), self)
        self.toggle_log_action.setCheckable(True)
        self.toggle_log_action.setChecked(True)
        self.toggle_log_action.triggered.connect(self.toggle_log_visibility)
        file_menu.addAction(self.toggle_log_action)

        # ログクリアメニューを追加
        clear_log_action = QAction(self.i18n.t("action_clear_log"), self)
        clear_log_action.triggered.connect(self.clear_log)
        file_menu.addAction(clear_log_action)

        help_menu = QMenu(self.i18n.t("menu_help"), self)
        version_action = QAction(self.i18n.t("action_version"), self)
        version_action.triggered.connect(self.show_version_info)
        help_menu.addAction(version_action)

        self.menu_bar.addMenu(file_menu)
        self.menu_bar.addMenu(help_menu)

    def toggle_log_visibility(self):
        visible = self.toggle_log_action.isChecked()
        self.log_area.setVisible(visible)

    def clear_log(self):
        reply = QMessageBox.question(self, self.i18n.t("confirm"), 
                                   self.i18n.t("confirm_clear_log"),
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.log_area.clear()

    def show_version_info(self):
        version_text = self.i18n.t("dialog_version_text").format(version=self.app_version)
        QMessageBox.information(self, self.i18n.t("dialog_version_title"), version_text)

    def open_language_dialog(self):
        dialog = LanguageDialog(self, self.i18n)
        if dialog.exec_():
            if dialog.selected_locale and dialog.selected_locale != self.i18n.locale:
                self.config_manager.set("locale", dialog.selected_locale)
                self.config_manager.save()
                QMessageBox.information(self, self.i18n.t("dialog_language_title"), 
                                      self.i18n.t("language_restart_required"))

    def init_format_layout(self):
        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel(self.i18n.t("label_format_select")))
        fmt_layout.addWidget(self.format_combo)
        return fmt_layout

    def init_output_dir_layout(self):
        out_layout = QHBoxLayout()
        self.output_dir_label = QLabel(f"{self.i18n.t('label_output_dir')} {self.output_dir}", self)
        self.change_output_btn = QPushButton(self.i18n.t("button_change_output"), self)
        self.change_output_btn.clicked.connect(self.open_output_dir_dialog)
        out_layout.addWidget(self.output_dir_label)
        out_layout.addWidget(self.change_output_btn)
        return out_layout

    def load_formats(self):
        formats = {
            self.i18n.t("format_mp4"): "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            self.i18n.t("format_mp3"): "bestaudio[ext=m4a]/bestaudio",
        }
        plugin_formats = {}
        for name in self.enabled_plugins:
            if name in self.plugin_manager.formats:
                plugin_formats[name] = self.plugin_manager.formats[name]

        combined_formats = {**formats, **plugin_formats}
        self.format_combo.clear()
        for name in combined_formats.keys():
            self.format_combo.addItem(name)

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
            self.status_label.setText(self.i18n.t("msg_settings_updated"))
            self.output_dir_label.setText(f"{self.i18n.t('label_output_dir')} {self.output_dir}")

            self.config_manager.set("output_dir", self.output_dir)
            self.config_manager.set("ffmpeg_path", self.ffmpeg_path)
            self.config_manager.set("enabled_plugins", self.enabled_plugins)
            self.config_manager.set("yt_dlp_opts", json.dumps(self.yt_dlp_opts, ensure_ascii=False))
            self.config_manager.save()

    def open_output_dir_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, self.i18n.t("dialog_select_folder"), self.output_dir)
        if folder:
            self.output_dir = folder
            self.output_dir_label.setText(f"{self.i18n.t('label_output_dir')} {folder}")
            msg = self.i18n.t("msg_output_changed").format(folder=folder)
            self.status_label.setText(msg)

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText(self.i18n.t("msg_enter_url"))
            return

        selected_fmt_name = self.format_combo.currentText()
        format_code = self.plugin_manager.get_all_formats().get(selected_fmt_name, "bestvideo+bestaudio/best")

        self.status_label.setText(self.i18n.t("msg_start_download"))
        self.download_btn.setEnabled(False)
        self.log_area.clear()
        self.progress_bar.setValue(0)

        # UI復帰タイマー開始（30秒でタイムアウト）
        self.ui_recovery_timer.start(30000)

        self.current_thread = DownloadThread(
            url,
            format_code,
            output_dir=self.output_dir,
            ffmpeg_path=self.ffmpeg_path,
            yt_dlp_opts=self.yt_dlp_opts,
        )
        self.current_thread.progress.connect(self.update_progress)
        self.current_thread.finished.connect(self.download_finished)
        self.current_thread.error_occurred.connect(self.handle_thread_error)
        self.current_thread.start()

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
                    msg = self.i18n.t("downloading_bytes").format(
                        percent=percent, downloaded=downloaded_bytes, total=total_bytes)
                else:
                    msg = self.i18n.t("downloading_percent").format(percent=percent)
            else:
                if self.show_bytes_cb.isChecked():
                    msg = self.i18n.t("downloading_bytes_only").format(downloaded=downloaded_bytes)
                else:
                    msg = self.i18n.t("downloading_unknown")
        elif status == "finished":
            self.progress_bar.setValue(100)
            msg = self.i18n.t("msg_download_complete")
        elif status == "error":
            # 詳細エラー情報をログに表示
            error_type = data.get("error_type", "UnknownError")
            error_msg = data.get("error", "")
            url = data.get("url", "")
            msg = f"{self.i18n.t('msg_error_occurred')} [{error_type}] {error_msg}"
            if url:
                msg += f" (URL: {url})"
        else:
            msg = ""

        self.status_label.setText(msg)
        if msg:
            self.log_area.append(f"[{time.strftime('%H:%M:%S')}] {msg}")

    def download_finished(self):
        self.ui_recovery_timer.stop()
        self.download_btn.setEnabled(True)
        self.current_thread = None
        self.status_label.setText(self.i18n.t("msg_download_finished"))

    def handle_thread_error(self, error_msg):
        self.ui_recovery_timer.stop()
        self.download_btn.setEnabled(True)
        self.current_thread = None
        error_log = f"[{time.strftime('%H:%M:%S')}] スレッドエラー: {error_msg}"
        self.log_area.append(error_log)
        self.status_label.setText(self.i18n.t("msg_thread_error"))

    def force_ui_recovery(self):
        """タイムアウト時の強制UI復帰"""
        self.download_btn.setEnabled(True)
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.terminate()
            self.current_thread.wait(3000)
        if self.current_batch_thread and self.current_batch_thread.isRunning():
            self.current_batch_thread.terminate()
            self.current_batch_thread.wait(3000)
        
        self.current_thread = None
        self.current_batch_thread = None
        error_log = f"[{time.strftime('%H:%M:%S')}] タイムアウトによりUI復帰を実行しました"
        self.log_area.append(error_log)
        self.status_label.setText(self.i18n.t("msg_timeout_recovery"))

    def open_csv_batch_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, self.i18n.t("dialog_select_csv"), "", "CSV files (*.csv)")
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
                QMessageBox.warning(self, self.i18n.t("warning"), self.i18n.t("csv_no_valid_urls"))
                return

            self.start_batch_download(urls)

        except Exception as e:
            error_msg = self.i18n.t("csv_read_failed").format(error=str(e))
            QMessageBox.critical(self, self.i18n.t("error"), error_msg)

    def start_batch_download(self, urls):
        if not urls:
            self.status_label.setText(self.i18n.t("msg_no_urls"))
            return

        msg = self.i18n.t("msg_batch_start").format(count=len(urls))
        self.status_label.setText(msg)
        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        # UI復帰タイマー開始（バッチ処理用に長めに設定）
        self.ui_recovery_timer.start(120000)  # 2分

        format_code = self.plugin_manager.get_all_formats().get(
            self.format_combo.currentText(), "bestvideo+bestaudio/best"
        )
        
        self.current_batch_thread = DownloadBatchThread(
            urls,
            output_dir=self.output_dir,
            format_code=format_code,
            ffmpeg_path=self.ffmpeg_path,
            yt_dlp_opts=self.yt_dlp_opts,
        )
        
        self._batch_error_detected = False  # エラーフラグ

        # エラー検出用の進捗スロットを追加
        def on_progress_log(msg):
            self.append_log(msg)
            if "失敗" in msg or "error" in msg.lower() or "エラー" in msg:
                self._batch_error_detected = True

        def on_finished(success):
            self.batch_download_finished(success and not self._batch_error_detected)

        def on_error(error_msg):
            self.handle_batch_error(error_msg)

        self.current_batch_thread.progress.connect(on_progress_log)
        self.current_batch_thread.finished_batch.connect(on_finished)
        self.current_batch_thread.error_occurred.connect(on_error)
        self.current_batch_thread.start()

    def append_log(self, message):
        timestamp = time.strftime('%H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        self.log_area.append(log_msg)
        self.status_label.setText(message)

    def batch_download_finished(self, success=True):
        self.ui_recovery_timer.stop()
        self.current_batch_thread = None
        
        if success:
            self.status_label.setText(self.i18n.t("msg_batch_finished"))
        else:
            self.status_label.setText(self.i18n.t("msg_batch_finished_with_errors"))
        
        self.download_btn.setEnabled(True)

    def handle_batch_error(self, error_msg):
        self.ui_recovery_timer.stop()
        self.current_batch_thread = None
        self.download_btn.setEnabled(True)
        error_log = f"バッチ処理エラー: {error_msg}"
        self.append_log(error_log)
        self.status_label.setText(self.i18n.t("msg_batch_error"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
