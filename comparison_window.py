from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout, QScrollArea
from PyQt5.QtCore import Qt, QPropertyAnimation, QSize
from PyQt5.QtGui import QPixmap, QIcon
from list_viewer import ListViewerWindow
from applicability_checker import check_applicability  

class ComparisonWindow(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.applicability_window = None
        self.list_viewer_window = None
        self.setWindowTitle("Comparaison des exigences")
        self.setFixedSize(800, 600)
        self.manager = manager

        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.addSpacing(24)
        self.setLayout(layout)

        # Logo Expleo
        self.logo = QLabel()
        pixmap = QPixmap("logoexpleo.png")
        self.logo.setPixmap(pixmap.scaledToWidth(120, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)
       
        self.title = QLabel("Comparaison des exigences")
        self.title.setObjectName("TitleLabel")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        layout.addSpacing(10)

        self.label_last = QLabel(" Dernier résultat :")
        layout.addWidget(self.label_last)

        self.scroll_last = QScrollArea()
        self.last_result_view = QTextEdit()
        self.last_result_view.setReadOnly(True)
        self.last_result_view.setMinimumHeight(120)
        self.scroll_last.setWidgetResizable(True)
        self.scroll_last.setWidget(self.last_result_view)
        layout.addWidget(self.scroll_last)

        self.label_new = QLabel(" Nouveau résultat :")
        layout.addWidget(self.label_new)

        self.scroll_new = QScrollArea()
        self.new_result_view = QTextEdit()
        self.new_result_view.setReadOnly(True)
        self.new_result_view.setMinimumHeight(120)
        self.scroll_new.setWidgetResizable(True)
        self.scroll_new.setWidget(self.new_result_view)
        layout.addWidget(self.scroll_new)

        layout.addSpacing(12)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        self.btn_back = QPushButton("Retour au menu")
        self.btn_back.clicked.connect(self.return_to_menu)
        btn_layout.addWidget(self.btn_back)

        self.btn_continue = QPushButton("Continuer")
        self.btn_continue.clicked.connect(self.go_back_to_insert)
        btn_layout.addWidget(self.btn_continue)

        self.btn_list = QPushButton("Voir la liste des exigences")
        self.btn_list.clicked.connect(self.show_list)
        btn_layout.addWidget(self.btn_list)

        layout.addLayout(btn_layout)
        layout.addSpacing(10)
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

        self.update_display()

    def update_display(self):
        self.manager.rebuild_history()  
        history = self.manager.history
        requirements = self.manager.get_all_requirements()

        if not history or not requirements:
            self.last_result_view.setText("")
            self.new_result_view.setText("")
            self.label_last.setText(" Dernier résultat (0 combinaison(s)) :")
            self.label_new.setText(" Nouveau résultat (0 combinaison(s)) :")
            self.current_combinations = []
            return

        non_empty_requirements = [req for req in requirements if req["themes"]]

        # Affichage du dernier résultat
        if len(non_empty_requirements) == 2:
            first_req_themes = non_empty_requirements[0]["themes"]
            lines = [" AND ".join(group) for group in first_req_themes]
            self.last_result_view.setText("\n".join(lines) if lines else "")
            self.label_last.setText(f" Dernier résultat ({len(lines)} combinaison(s)) :")
        elif len(history) > 1:
            previous_result = list(dict.fromkeys(history[-2]))
            self.last_result_view.setText("\n".join(previous_result) if previous_result else "")
            self.label_last.setText(f" Dernier résultat ({len(previous_result)} combinaison(s)) :")
        else:
            self.last_result_view.setText("")
            self.label_last.setText(" Dernier résultat (0 combinaison(s)) :")

        # Affichage du nouveau résultat
        if len(non_empty_requirements) == 1:
            first_req_themes = non_empty_requirements[0]["themes"]
            combinations = [" AND ".join(group) for group in first_req_themes]
            self.new_result_view.setText("\n".join(combinations) if combinations else "")
            self.label_new.setText(f" Nouveau résultat ({len(combinations)} combinaison(s)) :")
            self.current_combinations = combinations
        elif len(non_empty_requirements) >= 2 and history:
            current_result = list(dict.fromkeys(history[-1])) if history[-1] else []
            self.new_result_view.setText("\n".join(current_result) if current_result else "")
            self.label_new.setText(f" Nouveau résultat ({len(current_result)} combinaison(s)) :")
            self.current_combinations = current_result
        else:
            self.new_result_view.setText("")
            self.label_new.setText(" Nouveau résultat (0 combinaison(s)) :")
            self.current_combinations = []

    def return_to_menu(self):
        from main_menu import MainMenuWindow
        
        if hasattr(self, 'list_viewer_window') and self.list_viewer_window is not None:
            try:
                self.list_viewer_window.close()
            except Exception:
                pass
            self.list_viewer_window = None
        self.menu = MainMenuWindow(self.manager)
        self.menu.show()
        self.close()

    def show_list(self):
        from list_viewer import ListViewerWindow
        self.list_viewer_window = ListViewerWindow(self.manager, parent_window=self)
        
        x = self.x() + self.width() + 10
        y = self.y()
        self.list_viewer_window.setFixedSize(700, 600)
        self.list_viewer_window.move(x, y)
        self.list_viewer_window.show()

    def go_back_to_insert(self):
        from Insertion_window import InsertionWindow
        self.insert_window = InsertionWindow()
        self.insert_window.manager = self.manager
        self.insert_window.show()
        self.close()

    def reset_all(self):
        from Insertion_window import InsertionWindow
        new_manager = type(self.manager)()
        self.insert_window = InsertionWindow()
        self.insert_window.manager = new_manager
        self.insert_window.show()
        self.close()
