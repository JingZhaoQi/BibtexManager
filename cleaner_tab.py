from PyQt6.QtWidgets import QPushButton, QTextEdit, QVBoxLayout, QLabel
from PyQt6.QtCore import QThread, pyqtSignal
import search_module
from base_tab import BaseTab

class CleanerThread(QThread):
    result_ready = pyqtSignal(list)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        duplicates = search_module.check_and_clean_bib(self.file_path)
        self.result_ready.emit(duplicates)

class CleanerTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        description = QLabel("This function removes duplicate items from the selected BibTeX file.")
        description.setWordWrap(True)
        self.layout.addWidget(description)

        clean_button = QPushButton("Remove Duplicate Entries")
        clean_button.clicked.connect(self.clean_bibtex)
        self.layout.addWidget(clean_button)

        self.result_text = QTextEdit()
        self.layout.addWidget(self.result_text)

    def clean_bibtex(self):
        file_path = self.parent.bibtex_file_path.text()
        if not file_path:
            self.show_custom_message("Error", "Please select a BibTeX file first.")
            return
        
        self.cleaner_thread = CleanerThread(file_path)
        self.cleaner_thread.result_ready.connect(self.update_result)
        self.cleaner_thread.start()

    def update_result(self, duplicates):
        if duplicates:
            result = f"Cleaned BibTeX file. Removed duplicate entries for:\n{', '.join(duplicates)}"
        else:
            result = "No duplicate entries found in the BibTeX file."
        
        self.result_text.setPlainText(result)
        self.show_custom_message("Cleaning Complete", result)
