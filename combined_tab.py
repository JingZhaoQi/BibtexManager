from PyQt6.QtWidgets import QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSplitter
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
import search_module
from base_tab import BaseTab
from PyQt6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter, QTextDocument

class LaTeXHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False

    def set_dark_mode(self, is_dark):
        self.dark_mode = is_dark
        self.rehighlight()

    def highlightBlock(self, text):
        format = QTextCharFormat()
        color = Qt.GlobalColor.white if self.dark_mode else Qt.GlobalColor.black
        format.setForeground(color)
        self.setFormat(0, len(text), format)


class CombinedSearchThread(QThread):
    result_ready = pyqtSignal(str, list)

    def __init__(self, citations):
        super().__init__()
        self.citations = citations

    def run(self):
        search_result, not_found = search_module.get_bibtex_from_citations(self.citations)
        self.result_ready.emit(search_result, not_found)

class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(False)  # 只接受纯文本
        self.highlighter = LaTeXHighlighter(self.document())
        self.dark_mode = False

    def set_dark_mode(self, is_dark):
        self.dark_mode = is_dark
        self.highlighter.set_dark_mode(is_dark)
        self.update_text_color()

    def update_text_color(self):
        color = Qt.GlobalColor.white if self.dark_mode else Qt.GlobalColor.black
        self.setStyleSheet(f"QTextEdit {{ color: {color.name}; }}")

    def insertFromMimeData(self, source):
        if source.hasText():
            self.insertPlainText(source.text())
        else:
            super().insertFromMimeData(source)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.highlighter.rehighlight()


class CombinedTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.not_found_entries = []
        #self.citations_entry = CustomTextEdit()

    def update_dark_mode(self, is_dark):
        self.citations_entry.set_dark_mode(is_dark)

    def setup_ui(self):
        self.citations_entry = CustomTextEdit()
        self.citations_entry.setPlaceholderText("Enter LaTeX citations")
        self.layout.addWidget(self.citations_entry)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_citations)

        self.result_text = QTextEdit()

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.citations_entry)
        splitter.addWidget(self.search_button)
        splitter.addWidget(self.result_text)
        self.layout.addWidget(splitter)

        button_layout = QHBoxLayout()
        self.copy_button = self.setup_copy_button()
        button_layout.addWidget(self.copy_button)

        add_button = QPushButton("Add to BibTeX File")
        add_button.clicked.connect(self.add_to_bibtex_file)
        button_layout.addWidget(add_button)

        self.layout.addLayout(button_layout)
        

    def search_citations(self):
        self.result_text.setPlainText("Searching...")
        citations = self.citations_entry.toPlainText()

        self.search_thread = CombinedSearchThread(citations)
        self.search_thread.result_ready.connect(self.update_result)
        self.search_thread.start()

    def update_result(self, search_result, not_found):
        self.result_text.setPlainText(search_result)
        self.not_found_entries = not_found

    def add_to_bibtex_file(self):
        super().add_to_bibtex_file()
        if self.not_found_entries:
            self.show_custom_message("Not Found Entries", f"The following entries were not found:\n{', '.join(self.not_found_entries)}")
