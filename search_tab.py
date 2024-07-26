from PyQt6.QtWidgets import QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QThread, pyqtSignal,QTimer 
import search_module
from base_tab import BaseTab

class SearchThread(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, search_function, query, is_title=True):
        super().__init__()
        self.search_function = search_function
        self.query = query
        self.is_title = is_title

    def run(self):
        result = self.search_function(self.query, self.is_title)
        self.result_ready.emit(result)

class SearchTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.title_entry = QLineEdit()
        self.title_entry.setPlaceholderText("Enter paper title or arXiv ID")
        self.title_entry.returnPressed.connect(self.search_title)
        self.layout.addWidget(self.title_entry)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_title)
        self.layout.addWidget(search_button)

        self.result_text = QTextEdit()
        self.layout.addWidget(self.result_text)

        button_layout = QHBoxLayout()
        self.copy_button = self.setup_copy_button()
        button_layout.addWidget(self.copy_button)

        add_button = QPushButton("Add to BibTeX File")
        add_button.clicked.connect(self.add_to_bibtex_file)
        button_layout.addWidget(add_button)

        self.layout.addLayout(button_layout)

    def search_title(self):
        query = self.title_entry.text().strip()
        if not query:
            self.result_text.setPlainText("Please enter a search query.")
            return

        self.result_text.setPlainText("Searching...")
        self.search_thread = SearchThread(search_module.get_bibtex, query)
        self.search_thread.result_ready.connect(self.update_result)
        self.search_thread.start()

    def update_result(self, result):
        if result:
            self.result_text.setPlainText(result)
        else:
            self.result_text.setPlainText(f"No BibTeX found for query: {self.title_entry.text()}")