from PyQt5.QtWidgets import QWidget, QFormLayout, QComboBox, QLabel

class DownloaderOptionsWidget(QWidget):
    def __init__(self, parent=None, current_downloader=""):
        super().__init__(parent)
        self.current_downloader = current_downloader
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.downloader_combo = QComboBox(self)
        self.downloader_combo.addItems(['', 'aria2c', 'avconv', 'axel', 'curl', 'ffmpeg', 'httpie', 'wget'])
        index = self.downloader_combo.findText(self.current_downloader)
        self.downloader_combo.setCurrentIndex(index if index >= 0 else 0)

        layout.addRow("ダウンローダー (--downloader):", self.downloader_combo)

        self.setLayout(layout)

    def get_options(self):
        return {
            'downloader': self.downloader_combo.currentText()
        }
