from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel

from PyQt5.QtCore import Qt

class ProjectManagementChoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Projets")
        self.setFixedSize(600, 400)
        # Barre de titre : minimise autorisée, pas de bouton d'aide
        flags = self.windowFlags()
        flags = (flags | Qt.WindowMinimizeButtonHint) & ~Qt.WindowContextHelpButtonHint
        self.setWindowFlags(flags)
        from PyQt5.QtGui import QPixmap, QIcon
        from PyQt5.QtCore import QSize
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.addSpacing(24)
        self.setLayout(layout)
        # Logo Expleo
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("logo_expleo.png").scaledToWidth(100))
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)
        # Titre stylisé
        self.title = QLabel("Gestion des Projets")
        self.title.setObjectName("TitleLabel")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        layout.addSpacing(10)
        label = QLabel("Que souhaitez-vous faire ?")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        layout.addSpacing(8)
        self.btn_add = QPushButton("Ajouter projet(s)")
        self.btn_delete = QPushButton("Supprimer projet(s)")
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_delete)
        layout.addSpacing(10)
        layout.addStretch()
        # Footer
        self.footer = QLabel("Powered by Expleo")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setStyleSheet("color: #aaa; font-size: 13px; margin-top: 16px;")
        layout.addWidget(self.footer)
        # QSS global
        try:
            with open("expleo_style.qss", "r") as f:
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
        self.btn_add.clicked.connect(self.accept_add)
        self.btn_delete.clicked.connect(self.accept_delete)
        self.choice = None

    def accept_add(self):
        self.choice = 'add'
        self.accept()

    def accept_delete(self):
        self.choice = 'delete'
        self.accept()
