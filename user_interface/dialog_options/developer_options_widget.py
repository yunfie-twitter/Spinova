from PyQt5.QtWidgets import QWidget, QFormLayout, QCheckBox, QLabel

class DeveloperOptionsWidget(QWidget):
    def __init__(self, parent=None, opts=None):
        super().__init__(parent)
        self.opts = opts or {}
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        dev_label = QLabel("開発者向けオプション（慎重に使用してください）")
        dev_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addRow(dev_label)

        # 例の推奨されないオプションのチェックボックスを追加可能
        # ここには必要に応じて追加してください

        self.setLayout(layout)

    def get_options(self):
        # 現状は空の辞書返すだけ。必要なら追加実装
        return {}
