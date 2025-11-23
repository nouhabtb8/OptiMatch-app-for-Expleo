from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QMessageBox, QFrame, QHBoxLayout, QSizePolicy, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QPropertyAnimation, QSize
from PyQt5.QtGui import QPixmap, QIcon
import sqlite3
from requirement_manager import RequirementManager
from comparison_window import ComparisonWindow
from word_inserter import format_of_word_document
from excel_inserter import add_excel_files_to_database
from projects_deleter import Deleting_projects
from main_menu import MainMenuWindow



class InsertionWindow(QWidget):
    def __init__(self, manager=None):
        super().__init__()
        self.setWindowTitle("Insertion des exigences")
        self.setFixedSize(700, 600)

        self.manager = manager if manager is not None else RequirementManager()
        self.conn = sqlite3.connect("global.db")
        self.cursor = self.conn.cursor()

        
        layout = QVBoxLayout()
        layout.setSpacing(22)
        layout.addSpacing(30)
        self.setLayout(layout)

        
        self.logo = QLabel()
        pixmap = QPixmap("logoexpleo.png")
        self.logo.setPixmap(pixmap.scaledToWidth(120, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)
        
        self.title = QLabel("Insertion des exigences")
        self.title.setObjectName("TitleLabel")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        layout.addSpacing(8)

        self.label_info = QLabel("Entrer l’ID de l'exigence :")
        layout.addWidget(self.label_info)

        
        input_layout = QHBoxLayout()
        input_layout.setSpacing(0)
        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("Ex: QQQ-0000000 Z")
        input_layout.addWidget(self.input_id)
        layout.addLayout(input_layout)

        
        self.btn_insert = QPushButton("Comparer")
        self.btn_insert.clicked.connect(self.insert_by_id)
        layout.addWidget(self.btn_insert)

        
        layout.addSpacing(10)

        
        self.btn_back = QPushButton("Retour au menu")
        self.btn_back.clicked.connect(self.return_to_menu)
        layout.addWidget(self.btn_back)

        layout.addSpacing(8)
        layout.addStretch()
        # Footer "Powered by Expleo"
        self.footer = QLabel("Powered by Expleo")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setStyleSheet("color: #aaa; font-size: 13px; margin-top: 16px;")
        layout.addWidget(self.footer)

        # style QSS 
        try:
            with open("expleostyle.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Erreur chargement QSS : {e}")
        # Animation fade-in
        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(250)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()






    def insert_by_id(self):
        req_id = self.input_id.text().strip()

        if not req_id:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un ID d'une exigence.")
            return

        self.cursor.execute("SELECT themes FROM requirements WHERE id = ?", (req_id,))
        row = self.cursor.fetchone()

        if not row:
            QMessageBox.warning(self, "Non trouvé", f"L'ID {req_id} n'existe pas dans la base de données.")
            return

        themes_text = row[0].strip()
        themes = [line.split(" AND ") for line in themes_text.splitlines()] if themes_text else []

        # --- Vérification si le même ID exact est déjà inséré ---
        already_inserted = any(req["id"] == req_id for req in self.manager.get_all_requirements())
        if already_inserted:
            QMessageBox.warning(self, "Exigence déjà insérée", f"L'ID {req_id} a déjà été inséré.")
            return

        # --- Vérification si une autre version du même requirement est déjà insérée ---
        req_id_root = req_id[:11]  # exemple : "REQ-1234567"
        for existing in self.manager.get_all_requirements():
            existing_root = existing["id"][:11]
            if existing_root == req_id_root and existing["id"] != req_id:
                
                self.cursor.execute("SELECT source FROM requirements WHERE id = ?", (existing["id"],))
                row = self.cursor.fetchone()
                source_info = row[0] if row else "(source inconnue)"

                QMessageBox.warning(
                    self, "Conflit de version",
                    f"Une autre version de l'exigence ({existing['id']}) est déjà insérée (source : {source_info})."
                )
                return
            

        self.manager.add_requirement(req_id, themes)
        self.open_comparison_window()



    def add_word_doc(self):
     format_of_word_document(self)


    def add_excel_file(self):
     add_excel_files_to_database(self)


    def open_project_cleaner(self):
     self.cleaner_window = Deleting_projects(self)
     self.cleaner_window.show()
 
 
    

    def open_comparison_window(self):
        self.comp_window = ComparisonWindow(self.manager)
        self.comp_window.show()
        self.close()

    def return_to_menu(self):
        from main_menu import MainMenuWindow
        self.menu = MainMenuWindow(self.manager)
        self.menu.show()
        self.close()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()
