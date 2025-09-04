from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit, QCheckBox

class AdvancedOptionsWidget(QWidget):
    def __init__(self, parent=None, opts=None):
        super().__init__(parent)
        self.opts = opts or {}
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.concurrent_fragments_edit = QLineEdit(self)
        self.concurrent_fragments_edit.setText(str(self.opts.get('concurrent_fragments', '')))
        layout.addRow("並列フラグメント数 (-N):", self.concurrent_fragments_edit)

        self.skip_unavailable_fragments_cb = QCheckBox("スキップ可能フラグメント (--skip-unavailable-fragments)", self)
        self.skip_unavailable_fragments_cb.setChecked(self.opts.get('skip_unavailable_fragments', False))
        layout.addRow(self.skip_unavailable_fragments_cb)

        self.abort_on_unavailable_fragments_cb = QCheckBox("フラグメント不可時中止 (--abort-on-unavailable-fragments)", self)
        self.abort_on_unavailable_fragments_cb.setChecked(self.opts.get('abort_on_unavailable_fragments', False))
        layout.addRow(self.abort_on_unavailable_fragments_cb)

        self.rate_limit_edit = QLineEdit(self)
        self.rate_limit_edit.setText(self.opts.get('limit_rate', ''))
        layout.addRow("レート制限 (-r, --limit-rate):", self.rate_limit_edit)

        self.retries_edit = QLineEdit(self)
        self.retries_edit.setText(str(self.opts.get('retries', '')))
        layout.addRow("リトライ回数 (-R, --retries):", self.retries_edit)

        self.file_access_retries_edit = QLineEdit(self)
        self.file_access_retries_edit.setText(str(self.opts.get('file_access_retries', '')))
        layout.addRow("ファイルアクセスリトライ (--file-access-retries):", self.file_access_retries_edit)

        self.fragment_retries_edit = QLineEdit(self)
        self.fragment_retries_edit.setText(str(self.opts.get('fragment_retries', '')))
        layout.addRow("フラグメントリトライ (--fragment-retries):", self.fragment_retries_edit)

        self.retry_sleep_edit = QLineEdit(self)
        self.retry_sleep_edit.setText(self.opts.get('retry_sleep', ''))
        layout.addRow("リトライスリープ (--retry-sleep):", self.retry_sleep_edit)

        self.buffer_size_edit = QLineEdit(self)
        self.buffer_size_edit.setText(self.opts.get('buffer_size', ''))
        layout.addRow("バッファサイズ (--buffer-size):", self.buffer_size_edit)

        self.resize_buffer_cb = QCheckBox("バッファサイズ自動調整 (--resize-buffer)", self)
        self.resize_buffer_cb.setChecked(self.opts.get('resize_buffer', False))
        layout.addRow(self.resize_buffer_cb)

        self.no_resize_buffer_cb = QCheckBox("バッファ自動調整禁止 (--no-resize-buffer)", self)
        self.no_resize_buffer_cb.setChecked(self.opts.get('no_resize_buffer', False))
        layout.addRow(self.no_resize_buffer_cb)

        self.http_chunk_size_edit = QLineEdit(self)
        self.http_chunk_size_edit.setText(self.opts.get('http_chunk_size', ''))
        layout.addRow("HTTPチャンクサイズ (--http-chunk-size):", self.http_chunk_size_edit)

        self.setLayout(layout)

    def get_options(self):
        def to_int_or_none(s):
            try:
                return int(s)
            except:
                return None
        opts = {
            'concurrent_fragments': to_int_or_none(self.concurrent_fragments_edit.text()),
            'skip_unavailable_fragments': self.skip_unavailable_fragments_cb.isChecked(),
            'abort_on_unavailable_fragments': self.abort_on_unavailable_fragments_cb.isChecked(),
            'limit_rate': self.rate_limit_edit.text(),
            'retries': to_int_or_none(self.retries_edit.text()),
            'file_access_retries': to_int_or_none(self.file_access_retries_edit.text()),
            'fragment_retries': to_int_or_none(self.fragment_retries_edit.text()),
            'retry_sleep': self.retry_sleep_edit.text(),
            'buffer_size': self.buffer_size_edit.text(),
            'resize_buffer': self.resize_buffer_cb.isChecked(),
            'no_resize_buffer': self.no_resize_buffer_cb.isChecked(),
            'http_chunk_size': self.http_chunk_size_edit.text()
        }
        return {k: v for k, v in opts.items() if v not in (None, '', False) or (isinstance(v, bool) and v)}
