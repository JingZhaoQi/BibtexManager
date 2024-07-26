import sys
import warnings
import os
import re
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel
from PyQt6.QtGui import QIcon, QFont, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt, QSettings, QTimer
from search_tab import SearchTab
from combined_tab import CombinedTab
from cleaner_tab import CleanerTab
from utils import load_stylesheet, apply_stylesheet
from darkdetect import isDark
import certifi
cert_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Resources', 'cacert.pem'))
if not os.path.exists(cert_path):
    cert_path = certifi.where()

#os.environ['SSL_CERT_FILE'] = cert_path
#os.environ['REQUESTS_CA_BUNDLE'] = cert_path
#os.environ['SSL_CERT_FILE'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Resources', 'cacert.pem'))
#os.environ['REQUESTS_CA_BUNDLE'] = os.environ['SSL_CERT_FILE']


# Suppress the specific DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning, message="sipPyTypeDict")

# 设置日志
log_file = os.path.expanduser('./bibtexmanager_log.txt')
logging.basicConfig(filename=log_file, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def search_function():
    logging.debug("Starting search function")
    try:
        # 执行搜索操作
        result = perform_search()
        logging.debug(f"Search completed. Result: {result}")
    except Exception as e:
        logging.exception("An error occurred during search")

def excepthook(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = excepthook



class ReferenceManagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bibtex Manager")
        self.setGeometry(100, 100, 800, 600)  # Reduced window size
        
        self.app = QApplication.instance()
        self.app.setFont(QFont("Arial", 14))
        
        self.settings = QSettings("YourCompany", "ReferenceManager")
        self.load_settings()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.setup_bibtex_selection()

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        #print("Creating tabs...")
        self.search_tab = SearchTab(self)
        self.combined_tab = CombinedTab(self)
        self.cleaner_tab = CleanerTab(self)

        self.tabs.addTab(self.search_tab, "Title Search")
        self.tabs.addTab(self.combined_tab, "Citations Search")
        self.tabs.addTab(self.cleaner_tab, "Remove Duplicate Items")

        self.create_menu_bar()
        self.setAcceptDrops(True)
        self.last_system_theme = isDark()
        self.user_theme_override = False
        
        # Set initial theme
        #print("Setting initial theme...")
        self.set_theme(self.settings.value("dark_mode", self.last_system_theme, type=bool))
        
        
        # Periodically check system theme
        self.theme_check_timer = QTimer(self)
        self.theme_check_timer.timeout.connect(self.check_system_theme)
        self.theme_check_timer.start(5000)  # Check every 5 seconds

    def set_theme(self, dark_mode):
        self.settings.setValue("dark_mode", dark_mode)
        apply_stylesheet(self, dark_mode)
        self.update_dark_mode_text()
        self.combined_tab.update_dark_mode(dark_mode)

    def check_system_theme(self):
        current_system_theme = isDark()
        if current_system_theme != self.last_system_theme:
            self.last_system_theme = current_system_theme
            if not self.user_theme_override:
                self.set_theme(current_system_theme)

    def toggle_dark_mode(self):
        current_mode = self.settings.value("dark_mode", False, type=bool)
        new_mode = not current_mode
        self.set_theme(new_mode)
        self.user_theme_override = True

    def update_dark_mode_text(self):
        is_dark_mode = self.settings.value("dark_mode", False, type=bool)
        action_text = "Switch to Light Mode" if is_dark_mode else "Switch to Dark Mode"
        self.toggle_dark_mode_action.setText(action_text)

    def create_menu_bar(self):
        #print("Creating menu bar...")
        menu_bar = self.menuBar()
        menu_font = QFont("Arial", 14)
        menu_bar.setFont(menu_font)

        # View menu
        view_menu = menu_bar.addMenu("View")
        view_menu.setFont(menu_font)
        self.toggle_dark_mode_action = view_menu.addAction("Toggle Light/Dark Mode")
        self.toggle_dark_mode_action.triggered.connect(self.toggle_dark_mode)


    def update_dark_mode_text(self):
        is_dark_mode = self.settings.value("dark_mode", False, type=bool)
        action_text = "Switch to Light Mode" if is_dark_mode else "Switch to Dark Mode"
        self.toggle_dark_mode_action.setText(action_text)

    def setup_bibtex_selection(self):
        #print("Setting up BibTeX selection...")
        bibtex_layout = QVBoxLayout()
        
        label = QLabel("Select BibTeX File:")
        label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        bibtex_layout.addWidget(label)

        file_layout = QHBoxLayout()
        self.bibtex_file_path = QLineEdit()
        self.bibtex_file_path.setPlaceholderText("Drag & drop BibTeX file here or use Browse button")
        self.bibtex_file_path.setAcceptDrops(True)
        self.bibtex_file_path.dragEnterEvent = self.dragEnterEvent
        self.bibtex_file_path.dropEvent = self.dropEvent
        self.bibtex_file_path.textChanged.connect(self.update_bibtex_path)
        file_layout.addWidget(self.bibtex_file_path)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_bibtex_file)
        file_layout.addWidget(browse_button)

        bibtex_layout.addLayout(file_layout)
        self.layout.addLayout(bibtex_layout)
        
        # Add some spacing between the BibTeX selection and the tabs
        self.layout.addSpacing(20)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.bib'):
                self.bibtex_file_path.setText(file_path)
                break

    def browse_bibtex_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select BibTeX file", "", "BibTeX Files (*.bib)")
        if file_path:
            self.bibtex_file_path.setText(file_path)

    def update_bibtex_path(self, path):
        self.search_tab.set_bibtex_path(path)
        self.combined_tab.set_bibtex_path(path)
        self.cleaner_tab.set_bibtex_path(path)

    def load_settings(self):
        self.restoreGeometry(self.settings.value("geometry", self.saveGeometry()))
        self.restoreState(self.settings.value("windowState", self.saveState()))

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = ReferenceManagerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()