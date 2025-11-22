# excel_inserter.py

import os
import re
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication, QDialog, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class LoadingDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Veuillez patienter")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(300, 100)
        layout = QVBoxLayout()
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

def build_column_name_from_file(file_path):
    # Nom de base sans extension
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    # Cas versionné : _35 ou V35 uniquement
    # dollar mean looking in the end of chaine
    if re.search(r'(_\d+|V\d+)$', base_name):
        return base_name.replace('.', 'dot').replace('-', 'hyphen')

    try:
        # Lecture de la version depuis Heading!A2
        version = pd.read_excel(file_path, sheet_name="Heading", usecols="A", nrows=2, header=None).iloc[1, 0]
        version = str(version).strip().replace(" ", "_")
        if version and re.search(r'\d', version):
            return f"{base_name}_{version}".replace('.', 'dot').replace('-', 'hyphen')
    except Exception as e:
        print(f"Impossible de lire la version depuis {file_path} : {e}")

    # Si pas de version lisible → utiliser base
    return base_name.replace('.', 'dot').replace('-', 'hyphen')

def add_excel_files_to_database(parent=None):
    files, _ = QFileDialog.getOpenFileNames(parent, "Sélectionner un ou plusieurs fichiers Excel",
                                            "", "Fichiers Excel (*.xls *.xlsx *.xlsm)")
    if not files:
        return

    dialog = LoadingDialog("Insertion de fichier Excel...", parent)
    dialog.show()
    QApplication.processEvents()

    try:
        conn = sqlite3.connect("global.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS projects (nom_cf TEXT PRIMARY KEY)''')

        for path in files:
            try:
                df = pd.read_excel(path, sheet_name="EC", header=10)
            except Exception as e:
                QMessageBox.warning(parent, "Erreur de lecture", f"Impossible de lire {os.path.basename(path)}.\n{e}")
                continue

            columns = list(df.columns)
            col_nom = 'Nom CF /\nNom CO PLM (CF_CO)'

            if col_nom not in columns:
                QMessageBox.warning(parent, "Colonne manquante",
                                    f"La colonne '{col_nom}' est introuvable dans {os.path.basename(path)}")
                continue

            try:
                idx_project = columns.index("Project comment")
                col_app = columns[idx_project + 1]
            except (ValueError, IndexError):
                QMessageBox.warning(parent, "Colonne manquante",
                                    f"Impossible de trouver la colonne après 'Project comment' dans {os.path.basename(path)}")
                continue

            # Nom dynamique avec gestion de version
            col_db = build_column_name_from_file(path)

            try:
                cursor.execute(f'ALTER TABLE projects ADD COLUMN "{col_db}" TEXT')
            except sqlite3.OperationalError:
                pass  # déjà existante

            noms_cf = df[col_nom].astype(str).str.strip()
            valeurs = df[col_app].astype(str).str.strip()

            for nom_cf, valeur in zip(noms_cf, valeurs):
                cursor.execute(f'''
                    INSERT INTO projects (nom_cf, "{col_db}") VALUES (?, ?)
                    ON CONFLICT(nom_cf) DO UPDATE SET "{col_db}" = excluded."{col_db}"
                ''', (nom_cf, valeur))

        conn.commit()
        conn.close()

        QMessageBox.information(parent, "Terminé", "Fichier(s) Excel ajouté(s) à la base avec succès.")
    
    finally:
        dialog.close()
