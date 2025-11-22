import sqlite3
from PyQt5.QtWidgets import QMessageBox, QWidget, QTextEdit, QVBoxLayout, QLineEdit, QLabel, QPushButton
from PyQt5.QtCore import Qt, QSize


result_window = None
summary_window = None


class ApplicabilityResultWindow(QWidget):
    def __init__(self, results_by_project, manager):
        super().__init__()
        self.manager = manager
        self.setWindowTitle("Résultat par projet")
        self.setFixedSize(800, 600)
        self.move(0, 100)
        self.results_by_project = results_by_project
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.addSpacing(24)
        self.setLayout(layout)
        
        self.logo = QLabel()
        from PyQt5.QtGui import QPixmap, QIcon
        self.logo.setPixmap(QPixmap("logoexpleo.png").scaledToWidth(120))
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)
        
        self.title = QLabel("Résultat par projet")
        self.title.setObjectName("TitleLabel")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        layout.addSpacing(10)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Rechercher un projet")
        self.search_bar.textChanged.connect(self.update_display)
        layout.addWidget(self.search_bar)
        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        layout.addWidget(self.result_view)
        layout.addSpacing(12)
        from PyQt5.QtWidgets import QPushButton
        self.btn_back = QPushButton("Retour au menu")
        self.btn_back.clicked.connect(self.return_to_menu)
        layout.addWidget(self.btn_back)
        layout.addSpacing(10)
        layout.addStretch()
        # Footer
        self.footer = QLabel("Powered by Expleo")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setStyleSheet("color: #aaa; font-size: 13px; margin-top: 16px;")
        layout.addWidget(self.footer)
        # QSS global
        try:
            with open("expleostyle.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Erreur chargement QSS : {e}")
        # Animation fade-in
        from PyQt5.QtCore import QPropertyAnimation
        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(250)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()
        self.update_display()

    def update_display(self):
        search = self.search_bar.text().lower()
        self.result_view.clear()
        for project, result in self.results_by_project.items():
            
            if search in project.lower():
            
                self.result_view.append(f'<span style="font-size:8pt; font-weight:bold;">[ {project} ]</span><br>')
                self.result_view.append(" Combinaisons appliquées :")
                self.result_view.append("\n".join("  • " + c for c in result["applied"]) or "  (aucune)")
                self.result_view.append("\n Combinaisons non appliquées :")
                self.result_view.append("\n".join("  • " + c for c in result["not_applied"]) or "  (aucune)")
                self.result_view.append("\n Combinaisons NULL :")
                self.result_view.append("\n".join("  • " + c for c in result["not_found"]) or "  (aucune)")
                self.result_view.append("")  

        self.show()

    def return_to_menu(self):
        from main_menu import MainMenuWindow
        global summary_window
        if summary_window is not None and summary_window is not self:
            summary_window.close()
            summary_window = None
        self.menu = MainMenuWindow(self.manager)
        self.menu.show()
        self.close()


class GeneralApplicabilityWindow(QWidget):
    def __init__(self, global_applied, manager):
        super().__init__()
        self.manager = manager
        self.setWindowTitle("Liste globale")
        self.setFixedSize(600, 600)
        self.move(850, 100)
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.addSpacing(24)
        self.setLayout(layout)
       
        self.logo = QLabel()
        from PyQt5.QtGui import QPixmap, QIcon
        self.logo.setPixmap(QPixmap("logo_expleo.png").scaledToWidth(120))
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)
        
        self.title = QLabel("Résumé global")
        self.title.setObjectName("TitleLabel")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        layout.addSpacing(10)
        self.result_view = QTextEdit()
        self.result_view.setReadOnly(True)
        layout.addWidget(self.result_view)
        layout.addSpacing(12)
        from PyQt5.QtWidgets import QPushButton
        self.btn_back = QPushButton("Retour au menu")
        self.btn_back.clicked.connect(self.return_to_menu)
        layout.addWidget(self.btn_back)
        layout.addSpacing(10)
        layout.addStretch()
        # Footer
        self.footer = QLabel("Powered by Expleo")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setStyleSheet("color: #aaa; font-size: 13px; margin-top: 16px;")
        layout.addWidget(self.footer)
        # Style QSS 
        try:
            with open("expleostyle.qss", "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Erreur chargement QSS : {e}")
        # Animation fade-in
        from PyQt5.QtCore import QPropertyAnimation
        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(250)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()
        self.result_view.append(" Appliquée dans tous les projets :")
        if global_applied:
            self.result_view.append("\n".join("  • " + c for c in global_applied))
        else:
            self.result_view.append("  (aucune)")
        self.show()

    def return_to_menu(self):
        from main_menu import MainMenuWindow
        global result_window
        if result_window is not None and result_window is not self:
            result_window.close()
            result_window = None
        self.menu = MainMenuWindow(self.manager)
        self.menu.show()
        self.close()


def check_applicability(combinations, manager=None):
    global result_window, summary_window

    try:
        conn = sqlite3.connect("global.db")
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(projects)")
        all_columns = [col[1] for col in cursor.fetchall()]
        excluded = {"nom_cf", "id"}
        project_columns = [col for col in all_columns if col not in excluded]

        
        if not project_columns:
            QMessageBox.warning(None, "Aucun projet", "Il n'y a aucun projet dans la base de données à comparer.")
            return None

        results_by_project = {}
        combo_tracking = {combo: {"applied": [], "not_applied": [], "not_found": []} for combo in combinations}

        for project_col in project_columns:
            cursor.execute(f'SELECT nom_cf, "{project_col}" FROM projects')
            rows = cursor.fetchall()
            applicability_map = {
                row[0].strip(): str(row[1]).strip().upper() if row[1] is not None else "NULL"
                for row in rows
            }

            applied = []
            not_applied = []
            not_found = []

            for combo in combinations:
                themes = [t.strip() for t in combo.split("AND")]
                status = [applicability_map.get(t, "NULL") for t in themes]

                if "NULL" in status:
                    not_found.append(combo)
                    combo_tracking[combo]["not_found"].append(project_col)
                elif all(s in ("S", "O") for s in status):
                    applied.append(combo)
                    combo_tracking[combo]["applied"].append(project_col)
                else:
                    not_applied.append(combo)
                    combo_tracking[combo]["not_applied"].append(project_col)

            results_by_project[project_col] = {
                "applied": applied,
                "not_applied": not_applied,
                "not_found": not_found
            }

        
        fully_applied = []
        for combo, data in combo_tracking.items():
            if len(data["applied"]) == len(project_columns):
                fully_applied.append(combo)

        
        result_window = ApplicabilityResultWindow(results_by_project, manager)
        summary_window = GeneralApplicabilityWindow(fully_applied, manager)

    except Exception as e:
        print(" Erreur :", e)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Erreur lors de la vérification de l'applicabilité")
        msg.setInformativeText(str(e))
        msg.setWindowTitle("Erreur")
        msg.exec_()

    finally:
        conn.close()
