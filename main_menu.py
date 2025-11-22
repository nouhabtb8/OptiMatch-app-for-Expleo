from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation
from PyQt5.QtGui import QPixmap, QIcon

class MainMenuWindow(QDialog):

    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("Menu Principal")
        self.setFixedSize(900, 700)
        
        flags = self.windowFlags()
        flags = (flags | Qt.WindowMinimizeButtonHint) & ~Qt.WindowContextHelpButtonHint
        self.setWindowFlags(flags)
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.addSpacing(30)

        # Logo Expleo
        self.logo = QLabel()
        pixmap = QPixmap("logoexpleo.png")
        self.logo.setPixmap(pixmap.scaledToWidth(180, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)
       
        self.title = QLabel("Menu Principal")
        self.title.setObjectName("TitleLabel")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        layout.addSpacing(10)

        label = QLabel("Bienvenue sur l'application OptiMatch ! Choisissez une action :")
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Boutons du menu principal
        self.btn_insertion = QPushButton("Insertion des exigences")
        self.btn_comparison = QPushButton("Comparaison des exigences")
        self.btn_list_requirements = QPushButton("Liste des exigences")
        self.btn_comparison_projects = QPushButton("Comparaison avec projets")
        self.btn_db_modification = QPushButton("Modification de base de données")

        for btn in [self.btn_insertion, self.btn_comparison, self.btn_list_requirements, self.btn_comparison_projects, self.btn_db_modification]:
            btn.setMinimumHeight(48)
            layout.addWidget(btn)
            layout.addSpacing(8)

        # Footer "Powered by Expleo"
        layout.addStretch()
        self.footer = QLabel("Powered by Expleo")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setStyleSheet("color: #aaa; font-size: 13px; margin-top: 16px;")
        layout.addWidget(self.footer)

        self.setLayout(layout)

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


        # Connexion des boutons
        self.btn_insertion.clicked.connect(self.open_insertion_window)
        self.btn_comparison.clicked.connect(self.open_comparison_window)
        self.btn_list_requirements.clicked.connect(self.open_list_window)
        self.btn_comparison_projects.clicked.connect(self.open_comparison_projects_window)
        

        # Sous-menu pour modification de base de données
        self.db_modif_dialog = None
        self.btn_db_modification.clicked.connect(self.open_db_modification_menu)

    def open_insertion_window(self):
        from Insertion_window import InsertionWindow
        self.insertion_window = InsertionWindow(self.manager)
        self.insertion_window.show()
        self.close()

    def open_comparison_window(self):
        from comparison_window import ComparisonWindow
        self.comparison_window = ComparisonWindow(self.manager)
        self.comparison_window.show()
        self.close()

    def open_list_window(self):
        from list_viewer import ListViewerWindow
        self.list_window = ListViewerWindow(self.manager)
        self.list_window.show()
        self.close()

    def open_comparison_projects_window(self):
        from applicability_checker import check_applicability
        from PyQt5.QtWidgets import QMessageBox
        
        self.manager.rebuild_history()  # S'assurer que l'historique est à jour
        history = self.manager.history
        requirements = self.manager.get_all_requirements() if hasattr(self.manager, 'get_all_requirements') else []
        current_combinations = []

        non_empty_requirements = [req for req in requirements if req.get("themes")]
        if len(non_empty_requirements) == 1:
            
            themes = non_empty_requirements[0]["themes"]
            current_combinations = [" AND ".join(group) for group in themes]
        elif len(non_empty_requirements) >= 2 and history:
            
            last_result = list(dict.fromkeys(history[-1])) if history[-1] else []
            current_combinations = last_result
        
        if current_combinations and len(current_combinations) >= 1:
            res = check_applicability(current_combinations, self.manager)
            if res is not None:
                self.close()
        else:
            QMessageBox.warning(self, "Aucune exigence", "Aucune exigence à comparer avec les projets.")
           

    def open_db_modification_menu(self):
        self.db_modif_dialog = DBModificationMenu(self.manager)
        self.db_modif_dialog.show()
        self.close()

class DBModificationMenu(QDialog):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.setWindowTitle("Modification de la base de données")
        self.setFixedSize(800, 600)
        
        flags = self.windowFlags()
        flags = (flags | Qt.WindowMinimizeButtonHint) & ~Qt.WindowContextHelpButtonHint
        self.setWindowFlags(flags)
        from PyQt5.QtGui import QPixmap, QIcon
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.addSpacing(24)
        self.setLayout(layout)
        # Logo Expleo
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("logoexpleo.png").scaledToWidth(120))
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)
        
        self.title = QLabel("Modification de la base de données")
        self.title.setObjectName("TitleLabel")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        layout.addSpacing(10)
        label = QLabel("Choisissez une opération de modification :")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addSpacing(8)
        self.btn_word = QPushButton("Gestion Exigences (ajout Word)")
        self.btn_project = QPushButton("Gestion Projets (ajout Excel/ suppression)")
        layout.addWidget(self.btn_word)
        layout.addWidget(self.btn_project)
        layout.addSpacing(10)
        layout.addStretch()
        # Bouton Retour au menu
        self.btn_back = QPushButton("Retour au menu")
        self.btn_back.clicked.connect(self.return_to_menu)
        layout.addWidget(self.btn_back)
        # Footer
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
        
        self.btn_word.clicked.connect(self.handle_word)
        self.btn_project.clicked.connect(self.handle_project)

    def return_to_menu(self):
        from main_menu import MainMenuWindow
        
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'Deleting_projects':
                widget.close()
        self.menu = MainMenuWindow(self.manager)
        self.menu.show()
        self.close()

    def handle_word(self):
        from word_inserter import format_of_word_document
        format_of_word_document(self)

    def handle_project(self):
        from project_management_choice_dialog import ProjectManagementChoiceDialog
        dialog = ProjectManagementChoiceDialog(self)
        if dialog.exec_() == dialog.Accepted:
            if dialog.choice == 'add':
                from excel_inserter import add_excel_files_to_database
                add_excel_files_to_database(self)
            elif dialog.choice == 'delete':
                from projects_deleter import Deleting_projects
                self.delete_window = Deleting_projects(None)
                self.delete_window.setWindowModality(False)
                self.delete_window.show()
