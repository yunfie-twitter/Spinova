from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QCheckBox, QComboBox,
    QPushButton, QHBoxLayout, QFileDialog
)

class BasicOptionsWidget(QWidget):
    def __init__(self, parent=None, proxy="", force_ipv4=False, force_ipv6=False,
                 socket_timeout=None, default_format="", plugin_formats=None,
                 output_dir="downloads"):
        super().__init__(parent)

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
        layout.addRow("プロキシ (--proxy):", self.proxy_edit)

        # IPv4/IPv6
        self.force_ipv4_cb = QCheckBox("IPv4強制 (--force-ipv4)", self)
        self.force_ipv4_cb.setChecked(self.force_ipv4)
        layout.addRow(self.force_ipv4_cb)

        self.force_ipv6_cb = QCheckBox("IPv6強制 (--force-ipv6)", self)
        self.force_ipv6_cb.setChecked(self.force_ipv6)
        layout.addRow(self.force_ipv6_cb)

        # ソケットタイムアウト
        self.socket_timeout_edit = QLineEdit(self)
        if self.socket_timeout is not None:
            self.socket_timeout_edit.setText(str(self.socket_timeout))
        layout.addRow("ソケットタイムアウト (--socket-timeout):", self.socket_timeout_edit)

        # デフォルトフォーマット
        self.format_combo = QComboBox(self)
        self.format_combo.addItem("MP4 (動画+音声)", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]")
        self.format_combo.addItem("MP3 (音声のみ)", "bestaudio[ext=m4a]/bestaudio")
        for name, fmt in self.plugin_formats.items():
            self.format_combo.addItem(name, fmt)
        self.format_combo.addItem("カスタム", "custom")

        self.custom_format_edit = QLineEdit(self)
        self.custom_format_edit.setPlaceholderText("カスタムフォーマットを入力")
        self.custom_format_edit.setVisible(False)

        layout.addRow("デフォルトフォーマット:", self.format_combo)
        layout.addRow("", self.custom_format_edit)

        self.format_combo.currentIndexChanged.connect(self.on_format_changed)

        # 出力ディレクトリ
        outdir_layout = QHBoxLayout()
        self.output_dir_edit = QLineEdit(self)
        self.output_dir_edit.setText(self.output_dir)
        outdir_layout.addWidget(self.output_dir_edit)

        browse_btn = QPushButton("参照", self)
        browse_btn.clicked.connect(self.browse_folder)
        outdir_layout.addWidget(browse_btn)

        layout.addRow("規定ダウンロード場所:", outdir_layout)

        # Bytes表示オプション
        self.show_bytes_cb = QCheckBox("Bytes表示を有効にする", self)
        self.show_bytes_cb.setChecked(True)
        layout.addRow(self.show_bytes_cb)

        self.setLayout(layout)
        self.set_default_format_selection()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "保存先フォルダ選択", self.output_dir_edit.text())
        if folder:
            self.output_dir_edit.setText(folder)

    def on_format_changed(self, index):
        fmt = self.format_combo.itemData(index)
        self.custom_format_edit.setVisible(fmt == "custom")

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

    # 外部から設定を反映
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

    # 現在の設定を取得
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

        return {
            "proxy": self.proxy_edit.text().strip(),
            "force_ipv4": self.force_ipv4_cb.isChecked(),
            "force_ipv6": self.force_ipv6_cb.isChecked(),
            "socket_timeout": timeout,
            "default_format": default_fmt,
            "output_dir": self.output_dir_edit.text().strip()
        }
