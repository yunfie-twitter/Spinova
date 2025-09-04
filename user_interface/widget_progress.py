from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel

class ProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("進行状況なし", self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def update_progress(self, percent: int, status: str = ""):
        self.progress_bar.setValue(percent)
        self.label.setText(status)
