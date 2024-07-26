from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTextEdit, QFileDialog, QMessageBox, QDialog)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer 
import pyperclip
import search_module
import os


class CopyableMessageBox(QDialog):
    def __init__(self, title, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        
        text_edit = QTextEdit(self)
        text_edit.setPlainText(text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        button_layout = QHBoxLayout()
        copy_button = QPushButton("Copy", self)
        copy_button.clicked.connect(lambda: pyperclip.copy(text))
        button_layout.addWidget(copy_button)
        
        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

        
class BaseTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.bibtex_file_path = ""
        self.result_text = None
        self.copy_button = None

    def set_bibtex_path(self, path):
        self.bibtex_file_path = path

    def setup_copy_button(self):
        self.copy_button = QPushButton("Copy Result")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        return self.copy_button

    def copy_to_clipboard(self):
        if self.result_text and self.copy_button:
            content = self.result_text.toPlainText()
            pyperclip.copy(content)
            self.copy_button.setText("Copied to clipboard")
            self.copy_button.setEnabled(False)
            QTimer.singleShot(1000, self.reset_copy_button)

    def reset_copy_button(self):
        if self.copy_button:
            self.copy_button.setText("Copy Result")
            self.copy_button.setEnabled(True)


    def show_custom_message(self, title, message):
        dialog = CopyableMessageBox(title, message, self)
        dialog.exec()

    def add_to_bibtex_file(self):
        content = self.result_text.toPlainText()

        if not content:
            self.show_custom_message("Error", "No BibTeX entries to add.")
            return

        if self.bibtex_file_path:
            try:
                existing_content = ""
                if os.path.exists(self.bibtex_file_path):
                    with open(self.bibtex_file_path, 'r') as file:
                        existing_content = file.read()
                
                updated_bib, added_entries, skipped_entries = search_module.update_bibtex_file(content, existing_content)
                
                # 只有在成功更新后才写入文件
                if updated_bib:
                    with open(self.bibtex_file_path, 'w') as file:
                        file.write(updated_bib)
                
                    message = ""
                    if added_entries:
                        message += f"Added {len(added_entries)} new entries: {', '.join(added_entries)}\n"
                    if skipped_entries:
                        message += f"Skipped {len(skipped_entries)} existing entries: {', '.join(skipped_entries)}\n"
                
                    if message:
                        self.show_custom_message("BibTeX Update Result", message)
                    else:
                        self.show_custom_message("No Changes", "No new entries were added.")
                else:
                    self.show_custom_message("Error", "Failed to update BibTeX file. No changes were made.")
                
            except IOError as e:
                self.show_custom_message("Error", f"Failed to read or write to BibTeX file: {e}")
            except Exception as e:
                self.show_custom_message("Error", f"An unexpected error occurred: {e}")
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save BibTeX", "", "BibTeX Files (*.bib)")
            if file_path:
                try:
                    with open(file_path, 'w') as file:
                        file.write(content)
                    self.show_custom_message("Export", "BibTeX saved successfully!")
                    self.parent.bibtex_file_path.setText(file_path)
                except IOError as e:
                    self.show_custom_message("Error", f"Failed to write to BibTeX file: {e}")


    def show_custom_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
