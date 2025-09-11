from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QPushButton
from .dialog_options.basic_options_widget import BasicOptionsWidget
from .dialog_options.advanced_options_widget import AdvancedOptionsWidget
from .dialog_options.downloader_options_widget import DownloaderOptionsWidget
from .dialog_options.developer_options_widget import DeveloperOptionsWidget

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_output="downloads", plugin_manager=None,
                 current_ffmpeg_path="", current_yt_dlp_opts=None, i18n=None):
        super().__init__(parent)
        self.i18n = i18n or parent.i18n if hasattr(parent, 'i18n') else None
        self.plugin_manager = plugin_manager
        self.current_yt_dlp_opts = current_yt_dlp_opts or {}
        self.output_dir = current_output
        self.ffmpeg_path = current_ffmpeg_path
        self.init_ui()

    def init_ui(self):
        if self.i18n:
            self.setWindowTitle(self.i18n.t('settings_dialog_title'))
        else:
            self.setWindowTitle('設定')

        main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget(self)

        plugin_formats = self.plugin_manager.formats if self.plugin_manager else {}

        self.basic_tab = BasicOptionsWidget(
            parent=self,
            proxy=self.current_yt_dlp_opts.get('proxy', ''),
            force_ipv4=self.current_yt_dlp_opts.get('force_ipv4', False),
            force_ipv6=self.current_yt_dlp_opts.get('force_ipv6', False),
            socket_timeout=self.current_yt_dlp_opts.get('socket_timeout', None),
            default_format=self.current_yt_dlp_opts.get('default_format', ''),
            plugin_formats=plugin_formats,
            i18n=self.i18n
        )

        self.advanced_tab = AdvancedOptionsWidget(parent=self, opts=self.current_yt_dlp_opts, i18n=self.i18n)
        self.downloader_tab = DownloaderOptionsWidget(parent=self,
                                                    current_downloader=self.current_yt_dlp_opts.get('downloader', ''),
                                                    i18n=self.i18n)
        self.developer_tab = DeveloperOptionsWidget(parent=self, i18n=self.i18n)

        if self.i18n:
            self.tab_widget.addTab(self.basic_tab, self.i18n.t("tab_basic_options"))
            self.tab_widget.addTab(self.advanced_tab, self.i18n.t("tab_advanced_options"))
            self.tab_widget.addTab(self.downloader_tab, self.i18n.t("tab_downloader"))
            self.tab_widget.addTab(self.developer_tab, self.i18n.t("tab_developer"))
            save_btn_text = self.i18n.t("settings_save")
        else:
            self.tab_widget.addTab(self.basic_tab, "基本オプション")
            self.tab_widget.addTab(self.advanced_tab, "詳細オプション")
            self.tab_widget.addTab(self.downloader_tab, "ダウンローダー")
            self.tab_widget.addTab(self.developer_tab, "開発者向け")
            save_btn_text = "保存"

        main_layout.addWidget(self.tab_widget)

        save_btn = QPushButton(save_btn_text, self)
        save_btn.clicked.connect(self.accept)
        main_layout.addWidget(save_btn)

        self.setLayout(main_layout)

    def get_yt_dlp_opts(self):
        opts = {}
        opts.update(self.basic_tab.get_options())
        opts.update(self.advanced_tab.get_options())
        opts.update(self.downloader_tab.get_options())
        opts.update(self.developer_tab.get_options())
        return {k: v for k, v in opts.items() if v not in (None, '', False) or (isinstance(v, bool) and v)}

    def get_output_dir(self):
        return self.output_dir

    def get_ffmpeg_path(self):
        return self.ffmpeg_path

    def get_enabled_plugins(self):
        if self.plugin_manager:
            return list(self.plugin_manager.plugins.keys())
        return []
