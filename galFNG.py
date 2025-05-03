import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QTextEdit, QFileDialog, QComboBox, 
                            QLabel, QFrame, QHBoxLayout, QMenuBar, QMenu)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont, QPalette, QColor

class FileNameGrabber(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_file = "nmsettings.json"
        self.load_settings()
        
        self.setWindowTitle(self.translate("galFNG - File Name Grabber"))
        self.setGeometry(100, 100, 800, 600)
        
        # Создаем меню
        self.create_menu()
        
        # Устанавливаем темную тему Windows 11
        self.setStyleSheet("""
            QMainWindow {
                background-color: #202020;
            }
            QMenuBar {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMenuBar::item {
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #3b3b3b;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #4a4a4a;
            }
            QMenu::item:selected {
                background-color: #3b3b3b;
            }
            QPushButton {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #2b2b2b;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QTextEdit {
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                padding: 8px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                font-size: 14px;
                color: #ffffff;
            }
            QFrame#dropArea {
                background-color: #2b2b2b;
                border: 2px dashed #4a4a4a;
                border-radius: 8px;
            }
            QFrame#dropArea:hover {
                border: 2px dashed #5a5a5a;
                background-color: #3b3b3b;
            }
        """)
        
        # Создаем центральный виджет и основной layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Создаем область для drag-and-drop
        self.drop_area = QFrame()
        self.drop_area.setObjectName("dropArea")
        self.drop_area.setFrameShape(QFrame.Shape.Box)
        self.drop_area.setMinimumHeight(100)
        drop_layout = QVBoxLayout(self.drop_area)
        
        self.drop_label = QLabel(self.translate("Drag and drop folder here or click to select"))
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(self.drop_label)
        
        # Делаем область кликабельной
        self.drop_area.mousePressEvent = self.select_folder
        layout.addWidget(self.drop_area)
        
        # Горизонтальный layout для разделителя
        separator_layout = QHBoxLayout()
        
        # Выпадающий список для выбора разделителя
        self.separator_label = QLabel(self.translate("Separator:"))
        separator_layout.addWidget(self.separator_label)
        
        self.separator_combo = QComboBox()
        self.separator_combo.addItems([
            self.translate("Comma"),
            self.translate("Space"),
            self.translate("New line")
        ])
        self.separator_combo.currentTextChanged.connect(self.update_file_list)
        separator_layout.addWidget(self.separator_combo)
        separator_layout.addStretch()
        
        layout.addLayout(separator_layout)
        
        # Текстовое поле для отображения результатов
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setMinimumHeight(200)
        layout.addWidget(self.text_edit)
        
        # Кнопка копирования
        self.copy_btn = QPushButton(self.translate("Copy to clipboard"))
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(self.copy_btn)
        
        self.current_folder = ""
        
        # Включаем поддержку drag-and-drop
        self.setAcceptDrops(True)
        self.drop_area.setAcceptDrops(True)
        
    def create_menu(self):
        menubar = self.menuBar()
        
        # Меню настроек
        settings_menu = menubar.addMenu(self.translate("Settings"))
        
        # Подменю языка
        language_menu = settings_menu.addMenu(self.translate("Language"))
        self.language_actions = {}
        
        for lang in ["Русский", "English"]:
            action = language_menu.addAction(lang)
            action.setCheckable(True)
            action.setChecked(lang == self.settings["language"])
            action.triggered.connect(lambda checked, l=lang: self.change_language(l))
            self.language_actions[lang] = action
            
    def load_settings(self):
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                self.settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = {"language": "Русский"}
            self.save_settings()
            
    def save_settings(self):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)
            
    def change_language(self, language):
        self.settings["language"] = language
        self.save_settings()
        
        # Обновляем все тексты в интерфейсе
        self.setWindowTitle(self.translate("galFNG - File Name Grabber"))
        self.drop_label.setText(self.translate("Drag and drop folder here or click to select"))
        self.separator_label.setText(self.translate("Separator:"))
        self.separator_combo.clear()
        self.separator_combo.addItems([
            self.translate("Comma"),
            self.translate("Space"),
            self.translate("New line")
        ])
        self.copy_btn.setText(self.translate("Copy to clipboard"))
        
        # Обновляем меню
        self.menuBar().clear()
        self.create_menu()
        
        # Обновляем текст выбранной папки, если она есть
        if self.current_folder:
            folder_name = os.path.basename(self.current_folder)
            self.drop_label.setText(f"{self.translate('Selected folder')}: {folder_name}")
            
    def translate(self, text):
        translations = {
            "Русский": {
                "galFNG - File Name Grabber": "galFNG - Сборщик названий файлов",
                "Settings": "Настройки",
                "Language": "Язык",
                "Drag and drop folder here or click to select": "Перетащите папку сюда или нажмите для выбора",
                "Separator": "Разделитель",
                "Comma": "Запятая",
                "Space": "Пробел",
                "New line": "Абзац",
                "Copy to clipboard": "Копировать в буфер обмена",
                "Selected folder": "Выбрана папка"
            },
            "English": {
                "galFNG - File Name Grabber": "galFNG - File Name Grabber",
                "Settings": "Settings",
                "Language": "Language",
                "Drag and drop folder here or click to select": "Drag and drop folder here or click to select",
                "Separator": "Separator",
                "Comma": "Comma",
                "Space": "Space",
                "New line": "New line",
                "Copy to clipboard": "Copy to clipboard",
                "Selected folder": "Selected folder"
            }
        }
        return translations[self.settings["language"]].get(text, text)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if os.path.isdir(path):
                self.set_folder(path)
                
    def select_folder(self, event=None):
        folder = QFileDialog.getExistingDirectory(self, self.translate("Select folder"))
        if folder:
            self.set_folder(folder)
            
    def set_folder(self, folder):
        self.current_folder = folder
        folder_name = os.path.basename(folder)
        self.drop_label.setText(f"{self.translate('Selected folder')}: {folder_name}")
        self.update_file_list()
            
    def update_file_list(self):
        if not self.current_folder:
            return
            
        files = os.listdir(self.current_folder)
        current_text = self.separator_combo.currentText()
        if not current_text:
            return
            
        separator = {
            self.translate("Comma"): ", ",
            self.translate("Space"): " ",
            self.translate("New line"): "\n"
        }[current_text]
        
        self.text_edit.setText(separator.join(files))
        
    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.text_edit.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileNameGrabber()
    window.show()
    sys.exit(app.exec()) 