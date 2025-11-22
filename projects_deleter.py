import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QMessageBox, QListWidgetItem, QAbstractItemView
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import Qt

class Deleting_projects(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Suppression des projets")
        self.setFixedSize(550, 550)
        
        flags = self.windowFlags()
        flags = (flags | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint) & ~Qt.WindowContextHelpButtonHint
        self.setWindowFlags(flags)

        self.conn = sqlite3.connect("global.db")
        self.cursor = self.conn.cursor()

        from PyQt5.QtGui import QPixmap, QIcon
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.addSpacing(24)
        self.setLayout(layout)
        
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("logoexpleo.png").scaledToWidth(100))
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)
        
        
        self.title = QLabel("Suppression des projets")
        self.title.setObjectName("TitleLabel")
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)
        layout.addSpacing(10)
        self.label = QLabel("Sélectionnez le(s) projet(s) à supprimer :")
        layout.addWidget(self.label)
        from PyQt5.QtWidgets import QScrollBar
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.list_widget)
        layout.addSpacing(12)
        self.btn_delete = QPushButton("Supprimer le(s) projet(s) sélectionné(s)")
        self.btn_delete.clicked.connect(self.delete_selected_projects)
        layout.addWidget(self.btn_delete)
        layout.addSpacing(10)
        layout.addStretch()
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
        from PyQt5.QtCore import QPropertyAnimation
        self.setWindowOpacity(0.0)
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(250)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()
        self.load_project_columns()

    def load_project_columns(self):
        self.list_widget.clear()
        self.cursor.execute("PRAGMA table_info(projects)")
        all_columns = [col[1] for col in self.cursor.fetchall()]
        self.project_columns = [col for col in all_columns if col not in ("nom_cf", "id")]

        for col in self.project_columns:
            item = QListWidgetItem(col)
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)

    def delete_selected_projects(self):
        from PyQt5.QtWidgets import QInputDialog
        import smtplib
        from email.mime.text import MIMEText
        import configparser

        selected_columns = [
            self.list_widget.item(i).text()
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == Qt.Checked
        ]

        if not selected_columns:
            QMessageBox.information(self, "Aucun projet sélectionné", "Veuillez cocher un projet.")
            return

        # Demander nom, prénom et email utilisateur
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox
        class UserInfoDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Confirmation de suppression")
                layout = QVBoxLayout(self)
                self.nom_edit = QLineEdit()
                self.nom_edit.setPlaceholderText("Nom")
                self.prenom_edit = QLineEdit()
                self.prenom_edit.setPlaceholderText("Prénom")
                self.email_edit = QLineEdit()
                self.email_edit.setPlaceholderText("Email")
                layout.addWidget(QLabel("Entrez vos informations pour demander la suppression :"))
                layout.addWidget(self.nom_edit)
                layout.addWidget(self.prenom_edit)
                layout.addWidget(self.email_edit)
                self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                self.buttons.accepted.connect(self.accept)
                self.buttons.rejected.connect(self.reject)
                layout.addWidget(self.buttons)
            def get_info(self):
                return self.nom_edit.text().strip(), self.prenom_edit.text().strip(), self.email_edit.text().strip()
        info_dialog = UserInfoDialog(self)
        if info_dialog.exec_() != QDialog.Accepted:
            QMessageBox.warning(self, "Annulé", "Suppression annulée.")
            return
        nom, prenom, email = info_dialog.get_info()
        if not nom or not prenom or not email:
            QMessageBox.warning(self, "Erreur", "Tous les champs sont obligatoires.")
            return

        # Envoyer un mail à l'admin
        try:
            config = configparser.ConfigParser()
            config.read("config.ini")
            smtp_server = config.get("EMAIL", "smtp_server")
            smtp_port = config.getint("EMAIL", "smtp_port")
            sender_email = config.get("EMAIL", "sender_email")
            sender_password = config.get("EMAIL", "sender_password")
            use_tls = config.get("EMAIL", "use_tls") == "yes"
            admin_email = config.get("EMAIL", "admin_email")
            subject = "Demande de suppression de projet(s)"
            body = f"L'utilisateur {nom} {prenom} propriétaire de l'email {email} souhaite supprimer le(s) projet(s) suivant(s) à cause de publication d'une nouvelle version:\n" + ", ".join(selected_columns)
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = admin_email

            server = smtplib.SMTP(smtp_server, smtp_port)
            if use_tls:
                server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [admin_email], msg.as_string())
            server.quit()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'envoi de l'email à l'admin : {e}")
            return

        QMessageBox.information(self, "Demande envoyée", "Votre demande de suppression a été envoyée à l'administrateur. Veuillez attendre de recevoir un code de validation.")

        # Demander le code secret
        code, ok = QInputDialog.getText(self, "Validation admin", "Entrez le code reçu de l'administrateur pour valider la suppression :")
        if not ok or not code:
            QMessageBox.warning(self, "Annulé", "Suppression annulée.")
            return

        # Vérifier le code 
        CODE_ATTENDU = "2025"
        if code != CODE_ATTENDU:
            QMessageBox.critical(self, "Erreur", "Code de validation incorrect. Suppression annulée.")
            return

        # Supprimer colonne
        try:
            if self._supports_drop_column():
                for col in selected_columns:
                    self.cursor.execute(f'ALTER TABLE projects DROP COLUMN "{col}"')
            else:
                self._rebuild_table_without_columns(selected_columns)
            self.conn.commit()
            QMessageBox.information(self, "Succès", "Colonne(s) supprimée(s) avec succès.")
            self.load_project_columns()

            # Envoyer un mail de confirmation à l'admin
            try:
                config = configparser.ConfigParser()
                config.read("config.ini")
                smtp_server = config.get("EMAIL", "smtp_server")
                smtp_port = config.getint("EMAIL", "smtp_port")
                sender_email = config.get("EMAIL", "sender_email")
                sender_password = config.get("EMAIL", "sender_password")
                use_tls = config.get("EMAIL", "use_tls") == "yes"
                admin_email = config.get("EMAIL", "admin_email")
                subject = "Confirmation de suppression de projet(s)"
                body = f"L'utilisateur {nom} {prenom} a effectivement supprimé le(s) projet(s) suivant(s) :\n" + ", ".join(selected_columns)
                msg = MIMEText(body)
                msg['Subject'] = subject
                msg['From'] = sender_email
                msg['To'] = admin_email

                server = smtplib.SMTP(smtp_server, smtp_port)
                if use_tls:
                    server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, [admin_email], msg.as_string())
                server.quit()
            except Exception as e:
                QMessageBox.warning(self, "Alerte", f"Suppression faite, mais erreur lors de l'envoi de l'email de confirmation à l'admin : {e}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue :\n{e}")

    def _supports_drop_column(self):
        version = sqlite3.sqlite_version_info
        return version >= (3, 35, 0)

    def _rebuild_table_without_columns(self, columns_to_remove):
        self.cursor.execute("PRAGMA table_info(projects)")
        all_columns = [col[1] for col in self.cursor.fetchall()]
        keep_columns = [col for col in all_columns if col not in columns_to_remove]

        
        cols_str = ", ".join(f'"{col}"' for col in keep_columns)
        self.cursor.execute(f"CREATE TABLE temp_projects AS SELECT {cols_str} FROM projects")
        self.cursor.execute("DROP TABLE projects")
        self.cursor.execute("ALTER TABLE temp_projects RENAME TO projects")

    def closeEvent(self, event):
        self.conn.close()
        event.accept()
