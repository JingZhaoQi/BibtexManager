from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtWidgets import QMenu, QApplication,QTextEdit
from PyQt6.QtCore import QTranslator, QLocale, QSettings

def load_stylesheet(dark_mode):
    scrollbar_style = """
        QScrollBar:vertical {
            border: none;
            background: #F0F0F0;
            width: 10px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #BCBCBC;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::add-line:vertical {
            height: 0px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }
        QScrollBar::sub-line:vertical {
            height: 0px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
        QScrollBar:horizontal {
            border: none;
            background: #F0F0F0;
            height: 10px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:horizontal {
            background: #BCBCBC;
            min-width: 20px;
            border-radius: 5px;
        }
        QScrollBar::add-line:horizontal {
            width: 0px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }
        QScrollBar::sub-line:horizontal {
            width: 0px;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }
    """

    base_style = """
    QMainWindow, QWidget {
        font-family: Arial;
    }
    QTabWidget::pane {
        border-top: 2px solid;
    }
    QTabBar::tab {
        padding: 8px 20px;
        border: 1px solid;
        border-bottom: none;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        border-bottom: 2px solid #007AFF;
    }
    QTabBar::tab:!selected {
        margin-top: 2px;
    }
    QPushButton {
        padding: 8px 16px;
        border-radius: 4px;
        border: none;
    }
    QLineEdit, QTextEdit, QPlainTextEdit {
        padding: 8px;
        border: 1px solid;
        border-radius: 4px;
    }
    """

    if dark_mode:
        return scrollbar_style + base_style + """
        QMainWindow, QWidget {
            background-color: #2E2E2E;
            color: #FFFFFF;
        }
        QMenuBar {
            background-color: #3A3A3A;
            color: #FFFFFF;
        }
        QMenuBar::item:selected {
            background-color: #4A4A4A;
        }
        QMenu {
            background-color: #3A3A3A;
            color: #FFFFFF;
            border: 1px solid #555555;
        }
        QMenu::item:selected {
            background-color: #4A4A4A;
        }
        QTabWidget::pane {
            border-color: #555555;
            background-color: #3A3A3A;
        }
        QTabBar::tab {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3A3A3A, stop:1 #2E2E2E);
            color: #FFFFFF;
            border-color: #555555;
        }
        QTabBar::tab:selected {
            background-color: #3A3A3A;
        }
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0D6EFD, stop:1 #0B5ED7);
            color: white;
        }
        QPushButton:pressed {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0B5ED7, stop:1 #094BBA);
        }
        QPushButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0B5ED7, stop:1 #0D6EFD);
        }
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #3A3A3A;
            color: #FFFFFF;
            border-color: #555555;
        }
        """
    else:
        return scrollbar_style + base_style + """
        QMainWindow, QWidget {
            background-color: #F0F0F0;
            color: #000000;
        }
        QMenuBar {
            background-color: #E0E0E0;
        }
        QMenuBar::item:selected {
            background-color: #D0D0D0;
        }
        QMenu {
            background-color: #FFFFFF;
            border: 1px solid #D0D0D0;
        }
        QMenu::item:selected {
            background-color: #E0E0E0;
        }
        QTabWidget::pane {
            border-color: #D0D0D0;
            background-color: white;
        }
        QTabBar::tab {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F0F0F0, stop:1 #E0E0E0);
            color: #000000;
            border-color: #D0D0D0;
        }
        QTabBar::tab:selected {
            background-color: white;
        }
        QPushButton {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #007AFF, stop:1 #0056B3);
            color: white;
        }
        QPushButton:pressed {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0056B3, stop:1 #003D80);
        }
        QPushButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0056B3, stop:1 #007AFF);
        }
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: white;
            color: #000000;
            border-color: #D0D0D0;
        }
        """

def apply_stylesheet(window, dark_mode):
    stylesheet = load_stylesheet(dark_mode)
    window.setStyleSheet(stylesheet)
    
    # Force update of all widgets
    app = QApplication.instance()
    if app:
        for widget in app.allWidgets():
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

    # 更新 CustomTextEdit 的暗色模式
    for widget in window.findChildren(QTextEdit):
        if hasattr(widget, 'set_dark_mode'):
            widget.set_dark_mode(dark_mode)