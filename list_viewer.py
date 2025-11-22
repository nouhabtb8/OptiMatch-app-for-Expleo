from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QMessageBox, QSizePolicy
from PyQt5.QtCore import Qt, QPropertyAnimation, QSize
from PyQt5.QtGui import QPixmap, QIcon
import sqlite3

class ListViewerWindow(QWidget):
    def __init__(self, manager, parent_window=None):
        super().__init__()
        self.setWindowTitle("Liste des exigences")
        self.setFixedSize(800, 600)
        self.manager = manager
        self.parent_window = parent_window

        self.conn = sqlite3.connect("global.db")
        self.cursor = self.conn.cursor()

        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.addSpacing(24)
        self.setLayout(layout)

        
        self.logo = QLabel()
        pixmap = QPixmap("logoexpleo.png")
        self.logo.setPixmap(pixmap.scaledToWidth(120, Qt.SmoothTransformation))
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)
       
        self.title = QLabel("Liste des exigences")
        self.title.setObjectName("TitleLabel")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        layout.addSpacing(10)

        self.label = QLabel("Voici les exigences actuellement insérés :")
        layout.addWidget(self.label)

        from PyQt5.QtWidgets import QListWidgetItem
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(200)
        self.list_widget.setMaximumHeight(340)
        layout.addWidget(self.list_widget)
        layout.addSpacing(10)

        layout.addSpacing(12)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        self.btn_delete = QPushButton("Supprimer")
        self.btn_delete.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.btn_delete)

        self.btn_back = QPushButton("Retour au menu")
        self.btn_back.clicked.connect(self.return_to_menu)
        btn_layout.addWidget(self.btn_back)

        layout.addLayout(btn_layout)
        layout.addSpacing(10)
        layout.addStretch()
        

        self.footer = QLabel("Powered by Expleo")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setStyleSheet("color: #aaa; font-size: 13px; margin-top: 16px;")
        layout.addWidget(self.footer)

        
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

        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        from PyQt5.QtWidgets import QListWidgetItem
        for req in self.manager.get_all_requirements():
            req_id = req["id"]
            timestamp = req["timestamp"]
            theme_lines = [" AND ".join(group) for group in req["themes"]]

           
            self.cursor.execute("SELECT source FROM requirements WHERE id = ?", (req_id,))
            row = self.cursor.fetchone()
            source = row[0] if row else "(inconnu)"

            
            
            item = QListWidgetItem(f"{req_id} | Date: {timestamp} | Source: {source}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)

            
            for line in theme_lines:
                sub_item = QListWidgetItem(f"    ▶ {line}")
                sub_item.setFlags(sub_item.flags() & ~Qt.ItemIsUserCheckable)
                self.list_widget.addItem(sub_item)

            self.list_widget.addItem("")  
            

    def delete_selected(self):
        checked_indices = [i for i in range(self.list_widget.count())
                          if self.list_widget.item(i).flags() & Qt.ItemIsUserCheckable and self.list_widget.item(i).checkState() == Qt.Checked]
        if not checked_indices:
            QMessageBox.warning(self, "Erreur", "Veuillez cocher au moins une exigence à supprimer.")
            return

        # Confirmation avant suppression
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment supprimer la sélection de(s) exigence(s) cochée(s) ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        for idx in sorted(checked_indices, reverse=True):
            req_text = self.list_widget.item(idx).text().split("|")[0].strip()
            all_reqs = self.manager.get_all_requirements()
            for real_index, req in enumerate(all_reqs):
                if req["id"] == req_text:
                    self.manager.delete_requirement(real_index)
                    break
        self.refresh_list()
        if self.parent_window and hasattr(self.parent_window, 'update_display'):
            self.parent_window.update_display()

    def get_real_requirement_index(self, visual_index):
        count = -1
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i).text()
            if item.strip().startswith("REQ-"):
                count += 1
            if i == visual_index:
                return count
        return -1

    def return_to_menu(self):
        from main_menu import MainMenuWindow
        if self.parent_window is not None:
            try:
                self.parent_window.close()
            except Exception:
                pass
        self.menu = MainMenuWindow(self.manager)
        self.menu.show()
        self.close()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()
