from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit, QCheckBox

class AdvancedOptionsWidget(QWidget):
    def __init__(self, parent=None, opts=None, i18n=None):
        super().__init__(parent)
        self.i18n = i18n
        self.opts = opts or {}
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.concurrent_fragments_edit = QLineEdit(self)
        self.concurrent_fragments_edit.setText(str(self.opts.get('concurrent_fragments', '')))
        concurrent_label = self.i18n.t("advanced_concurrent_fragments") if self.i18n else "並列フラグメント数 (-N):"
        layout.addRow(concurrent_label, self.concurrent_fragments_edit)

        skip_text = self.i18n.t("advanced_skip_unavailable") if self.i18n else "スキップ可能フラグメント (--skip-unavailable-fragments)"
        self.skip_unavailable_fragments_cb = QCheckBox(skip_text, self)
        self.skip_unavailable_fragments_cb.setChecked(self.opts.get('skip_unavailable_fragments', False))
        layout.addRow(self.skip_unavailable_fragments_cb)

        abort_text = self.i18n.t("advanced_abort_on_unavailable") if self.i18n else "フラグメント不可時中止 (--abort-on-unavailable-fragments)"
        self.abort_on_unavailable_fragments_cb = QCheckBox(abort_text, self)
        self.abort_on_unavailable_fragments_cb.setChecked(self.opts.get('abort_on_unavailable_fragments', False))
        layout.addRow(self.abort_on_unavailable_fragments_cb)

        self.rate_limit_edit = QLineEdit(self)
        self.rate_limit_edit.setText(self.opts.get('limit_rate', ''))
        rate_label = self.i18n.t("advanced_rate_limit") if self.i18n else "レート制限 (-r, --limit-rate):"
        layout.addRow(rate_label, self.rate_limit_edit)

        self.retries_edit = QLineEdit(self)
        self.retries_edit.setText(str(self.opts.get('retries', '')))
        retries_label = self.i18n.t("advanced_retries") if self.i18n else "リトライ回数 (-R, --retries):"
        layout.addRow(retries_label, self.retries_edit)

        self.file_access_retries_edit = QLineEdit(self)
        self.file_access_retries_edit.setText(str(self.opts.get('file_access_retries', '')))
        file_access_label = self.i18n.t("advanced_file_access_retries") if self.i18n else "ファイルアクセスリトライ (--file-access-retries):"
        layout.addRow(file_access_label, self.file_access_retries_edit)

        self.fragment_retries_edit = QLineEdit(self)
        self.fragment_retries_edit.setText(str(self.opts.get('fragment_retries', '')))
        fragment_label = self.i18n.t("advanced_fragment_retries") if self.i18n else "フラグメントリトライ (--fragment-retries):"
        layout.addRow(fragment_label, self.fragment_retries_edit)

        self.retry_sleep_edit = QLineEdit(self)
        self.retry_sleep_edit.setText(self.opts.get('retry_sleep', ''))
        sleep_label = self.i18n.t("advanced_retry_sleep") if self.i18n else "リトライスリープ (--retry-sleep):"
        layout.addRow(sleep_label, self.retry_sleep_edit)

        self.buffer_size_edit = QLineEdit(self)
        self.buffer_size_edit.setText(self.opts.get('buffer_size', ''))
        buffer_label = self.i18n.t("advanced_buffer_size") if self.i18n else "バッファサイズ (--buffer-size):"
        layout.addRow(buffer_label, self.buffer_size_edit)

        resize_text = self.i18n.t("advanced_resize_buffer") if self.i18n else "バッファサイズ自動調整 (--resize-buffer)"
        self.resize_buffer_cb = QCheckBox(resize_text, self)
        self.resize_buffer_cb.setChecked(self.opts.get('resize_buffer', False))
        layout.addRow(self.resize_buffer_cb)

        no_resize_text = self.i18n.t("advanced_no_resize_buffer") if self.i18n else "バッファ自動調整禁止 (--no-resize-buffer)"
        self.no_resize_buffer_cb = QCheckBox(no_resize_text, self)
        self.no_resize_buffer_cb.setChecked(self.opts.get('no_resize_buffer', False))
        layout.addRow(self.no_resize_buffer_cb)

        self.http_chunk_size_edit = QLineEdit(self)
        self.http_chunk_size_edit.setText(self.opts.get('http_chunk_size', ''))
        chunk_label = self.i18n.t("advanced_http_chunk_size") if self.i18n else "HTTPチャンクサイズ (--http-chunk-size):"
        layout.addRow(chunk_label, self.http_chunk_size_edit)

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
