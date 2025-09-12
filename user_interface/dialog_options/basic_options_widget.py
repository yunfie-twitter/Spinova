from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QCheckBox, QComboBox,
    QPushButton, QHBoxLayout, QFileDialog, QLabel
)
from PyQt5.QtCore import Qt

class BasicOptionsWidget(QWidget):
    def __init__(self, parent=None, proxy="", force_ipv4=False, force_ipv6=False,
                 socket_timeout=None, default_format="", plugin_formats=None,
                 output_dir="downloads", i18n=None):
        super().__init__(parent)
        self.i18n = i18n
        self.proxy = proxy
        self.force_ipv4 = force_ipv4
        self.force_ipv6 = force_ipv6
        self.socket_timeout = socket_timeout
        self.plugin_formats = plugin_formats or {}
        self.default_format = default_format if default_format else "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]"
        self.output_dir = output_dir
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # プロキシ
        self.proxy_edit = QLineEdit(self)
        self.proxy_edit.setText(self.proxy)
        proxy_label = self.i18n.t("basic_proxy") if self.i18n else "プロキシ (--proxy):"
        layout.addRow(proxy_label, self.proxy_edit)

        # IPv4/IPv6
        ipv4_text = self.i18n.t("basic_force_ipv4") if self.i18n else "IPv4強制 (--force-ipv4)"
        self.force_ipv4_cb = QCheckBox(ipv4_text, self)
        self.force_ipv4_cb.setChecked(self.force_ipv4)
        layout.addRow(self.force_ipv4_cb)

        ipv6_text = self.i18n.t("basic_force_ipv6") if self.i18n else "IPv6強制 (--force-ipv6)"
        self.force_ipv6_cb = QCheckBox(ipv6_text, self)
        self.force_ipv6_cb.setChecked(self.force_ipv6)
        layout.addRow(self.force_ipv6_cb)

        # ソケットタイムアウト
        self.socket_timeout_edit = QLineEdit(self)
        if self.socket_timeout is not None:
            self.socket_timeout_edit.setText(str(self.socket_timeout))
        timeout_label = self.i18n.t("basic_socket_timeout") if self.i18n else "ソケットタイムアウト (--socket-timeout):"
        layout.addRow(timeout_label, self.socket_timeout_edit)

        # 画質選択（動画ビットレート）
        quality_label = QLabel(self.i18n.t("video_quality") if self.i18n else "画質 (動画ビットレート):")
        self.quality_combo = QComboBox(self)
        # 例の画質プリセット、必要に応じ調整可
        qualities = [
            ("最高品質 (無制限)", "best"),
            ("1080p 以上", "bestaudio+bestvideo[height>=1080]"),
            ("720p 以上", "bestaudio+bestvideo[height>=720]"),
            ("480p 以上", "bestaudio+bestvideo[height>=480]"),
            ("360p 以上", "bestaudio+bestvideo[height>=360]"),
            ("音声のみ", "bestaudio/best"),
        ]
        for text, fmt in qualities:
            self.quality_combo.addItem(text, fmt)
        self.quality_combo.setCurrentIndex(0)
        layout.addRow(quality_label, self.quality_combo)

        # 音声ビットレート指定
        audio_bitrate_label = QLabel(self.i18n.t("audio_bitrate") if self.i18n else "音声ビットレート (kbps):")
        self.audio_bitrate_combo = QComboBox(self)
        audio_bitrates = [
            ("最高 (無指定)", ""),
            ("320 kbps", "320"),
            ("256 kbps", "256"),
            ("192 kbps", "192"),
            ("128 kbps", "128"),
            ("64 kbps", "64"),
        ]
        for text, val in audio_bitrates:
            self.audio_bitrate_combo.addItem(text, val)
        self.audio_bitrate_combo.setCurrentIndex(0)
        layout.addRow(audio_bitrate_label, self.audio_bitrate_combo)

        # デフォルトフォーマット
        self.format_combo = QComboBox(self)
        if self.i18n:
            mp4_text = self.i18n.t("format_mp4")
            mp3_text = self.i18n.t("format_mp3")
            custom_text = self.i18n.t("basic_custom_format")
            custom_placeholder = self.i18n.t("basic_custom_placeholder")
        else:
            mp4_text = "MP4 (動画+音声)"
            mp3_text = "MP3 (音声のみ)"
            custom_text = "カスタム"
            custom_placeholder = "カスタムフォーマットを入力"

        self.format_combo.addItem(mp4_text, "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]")
        self.format_combo.addItem(mp3_text, "bestaudio[ext=m4a]/bestaudio")

        for name, fmt in self.plugin_formats.items():
            self.format_combo.addItem(name, fmt)

        self.format_combo.addItem(custom_text, "custom")

        self.custom_format_edit = QLineEdit(self)
        self.custom_format_edit.setPlaceholderText(custom_placeholder)
        self.custom_format_edit.setVisible(False)

        format_label = self.i18n.t("basic_default_format") if self.i18n else "デフォルトフォーマット:"
        layout.addRow(format_label, self.format_combo)
        layout.addRow("", self.custom_format_edit)

        self.format_combo.currentIndexChanged.connect(self.on_format_changed)
        self.custom_format_edit.textChanged.connect(self.on_custom_format_changed)

        # 出力ディレクトリ
        outdir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit(self)
        self.output_dir_edit.setText(self.output_dir)
        outdir_layout.addWidget(self.output_dir_edit)

        browse_text = self.i18n.t("settings_browse") if self.i18n else "参照"
        browse_btn = QPushButton(browse_text, self)
        browse_btn.clicked.connect(self.browse_folder)
        outdir_layout.addWidget(browse_btn)

        outdir_label = self.i18n.t("basic_output_directory") if self.i18n else "規定ダウンロード場所:"
        layout.addRow(outdir_label, outdir_layout)

        # Bytes表示オプション
        bytes_text = self.i18n.t("bytes_display_enable") if self.i18n else "Bytes表示を有効にする"
        self.show_bytes_cb = QCheckBox(bytes_text, self)
        self.show_bytes_cb.setChecked(True)
        layout.addRow(self.show_bytes_cb)

        self.setLayout(layout)
        self.set_default_format_selection()

    def browse_folder(self):
        dialog_title = self.i18n.t("dialog_select_folder") if self.i18n else "保存先フォルダ選択"
        folder = QFileDialog.getExistingDirectory(self, dialog_title, self.output_dir_edit.text())
        if folder:
            self.output_dir_edit.setText(folder)

    def on_format_changed(self, index):
        fmt = self.format_combo.itemData(index)
        self.custom_format_edit.setVisible(fmt == "custom")
        # 画質・音声ビットレートと連動させる例（カスタム以外は設定）
        if fmt != "custom":
            # フォーマット直接選択時はカスタム入力非活性か空白にするなど工夫可
            pass

    def on_custom_format_changed(self, text):
        # カスタム入力時に画質・音声ビットレートを解除するなどのロジックを入れても良い
        pass

    def set_default_format_selection(self):
        target_fmt = self.default_format.strip().lower()
        index = -1
        for i in range(self.format_combo.count()):
            fmt_data = self.format_combo.itemData(i)
            if fmt_data and fmt_data.strip().lower() == target_fmt:
                index = i
                break

        if index == -1:
            index = self.format_combo.count() - 1  # カスタム
            self.custom_format_edit.setText(self.default_format)
            self.custom_format_edit.setVisible(True)
        else:
            self.custom_format_edit.setVisible(False)

        self.format_combo.setCurrentIndex(index)

    def set_options(self, opts):
        self.proxy_edit.setText(opts.get("proxy", ""))
        self.force_ipv4_cb.setChecked(opts.get("force_ipv4", False))
        self.force_ipv6_cb.setChecked(opts.get("force_ipv6", False))
        sock_timeout = opts.get("socket_timeout", None)
        self.socket_timeout_edit.setText(str(sock_timeout) if sock_timeout else "")
        self.default_format = opts.get("default_format", self.default_format)
        self.output_dir = opts.get("output_dir", self.output_dir)
        self.output_dir_edit.setText(self.output_dir)
        self.set_default_format_selection()

        # 画質と音声ビットレートはoptsまたはフォーマット文字列解析が必要ならここで処理

    def get_options(self):
        try:
            timeout = float(self.socket_timeout_edit.text())
        except ValueError:
            timeout = None

        idx = self.format_combo.currentIndex()
        fmt_data = self.format_combo.itemData(idx)
        if fmt_data == "custom":
            default_fmt = self.custom_format_edit.text().strip()
        else:
            default_fmt = fmt_data

        # 画質、音声ビットレートの選択値からフォーマット文字列を組み立てる
        # ここでは単純にdefault_fmtのみ返しています

        return {
            "proxy": self.proxy_edit.text().strip(),
            "force_ipv4": self.force_ipv4_cb.isChecked(),
            "force_ipv6": self.force_ipv6_cb.isChecked(),
            "socket_timeout": timeout,
            "default_format": default_fmt,
            "output_dir": self.output_dir_edit.text().strip(),
            # 必要に応じ "video_quality": self.quality_combo.currentData(),
            # "audio_bitrate": self.audio_bitrate_combo.currentData()
        }
