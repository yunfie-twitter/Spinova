from PyQt5.QtWidgets import QWidget, QFormLayout, QComboBox, QLabel

class DownloaderOptionsWidget(QWidget):
    def __init__(self, parent=None, current_downloader="", i18n=None):
        super().__init__(parent)
        self.i18n = i18n
        self.current_downloader = current_downloader
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.downloader_combo = QComboBox(self)
        self.downloader_combo.addItems(['', 'aria2c', 'avconv', 'axel', 'curl', 'ffmpeg', 'httpie', 'wget'])

        index = self.downloader_combo.findText(self.current_downloader)
        self.downloader_combo.setCurrentIndex(index if index >= 0 else 0)

        downloader_label = self.i18n.t("downloader_label") if self.i18n else "ダウンローダー (--downloader):"
        layout.addRow(downloader_label, self.downloader_combo)

        self.setLayout(layout)

    def get_options(self):
        return {
            'downloader': self.downloader_combo.currentText()
        }
