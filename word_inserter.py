import os
import re
import sqlite3
from datetime import datetime
from docx import Document


from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

from PyQt5.QtWidgets import (
    QFileDialog, QMessageBox, QApplication, QDialog, QLabel, QVBoxLayout
)
from PyQt5.QtCore import Qt
from requirement_researcher import (
    extract_themes_old_format,
    extract_themes_from_diversity_expression
)


def normalize_id(raw_id):
    return re.sub(r'\s+', ' ', raw_id.strip())



def iter_block_items(parent):
    """Parcourt le document dans l’ordre réel (paragraphes et tableaux)."""
    for child in parent.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def extract_lines_from_docx(path):
    from docx import Document
    doc = Document(path)
    blocks = list(iter_block_items(doc))
    lines = []
    found_heading = False

    for block in blocks:
        if isinstance(block, Paragraph):
            text = block.text.strip()
            if not found_heading and "purpose and scope of application" in text.lower():
                found_heading = True
                print(" 'PURPOSE AND SCOPE OF APPLICATION' détecté")
            continue

        if found_heading and isinstance(block, Table):
            for row in block.rows:
                for cell in row.cells:
                    for part in cell.text.splitlines():
                        clean = part.replace('\xa0', ' ').strip()
                        if clean:
                            lines.append(clean)

    if not found_heading:
        print(" 'PURPOSE AND SCOPE OF APPLICATION' non trouvé, extraction annulée.")

    return lines



def init_db():
    conn = sqlite3.connect("global.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requirements (
        id TEXT PRIMARY KEY,
        themes TEXT,
        timestamp TEXT,
        source TEXT,
        occurrences INTEGER DEFAULT 1
    )
    """)
    conn.commit()
    return conn, cursor

def insert_requirement(req_id, full_text, extractor, source_name, cursor, seen_ids):
    req_id = normalize_id(req_id)
    if req_id in seen_ids:
        return
    seen_ids.add(req_id)

    print(f"\n Insertion en cours : {req_id}")
    try:
        themes_groups = extractor(full_text)
    except Exception as e:
        print(f" Erreur d'extraction pour {req_id} : {e}")
        themes_groups = []

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    if not themes_groups:
        print(f" {req_id} → aucun groupe extrait")
    else:
        print(f" {req_id} → {len(themes_groups)} groupe(s) extrait(s)")

    formatted_themes = "\n".join([" AND ".join(group) for group in themes_groups])

    try:
        cursor.execute("""
            INSERT INTO requirements (id, themes, timestamp, source, occurrences)
            VALUES (?, ?, ?, ?, 1)
        """, (req_id, formatted_themes, timestamp, source_name))
        print(f" {req_id} inséré dans la base")
    except sqlite3.IntegrityError:
        print(f" {req_id} déjà présent — mise à jour occurrences et source")
        cursor.execute("SELECT source FROM requirements WHERE id = ?", (req_id,))
        row = cursor.fetchone()
        if row:
            old_source = row[0]
            new_source = old_source
            if source_name not in old_source:
                new_source = f"{old_source}, {source_name}"
            cursor.execute("""
                UPDATE requirements
                SET occurrences = 2,
                    source = ?
                WHERE id = ?
            """, (new_source, req_id))


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

def format_of_word_document(parent):
    path, _ = QFileDialog.getOpenFileName(parent, "Sélectionner un fichier Word", "", "Documents Word (*.docx)")
    if not path:
        return

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("Choix du format")
    msg.setText("Quel est le format du document Word sélectionné ?")
    btn_old = msg.addButton("Ancien format", QMessageBox.YesRole)
    btn_new = msg.addButton("Nouveau format", QMessageBox.NoRole)
    msg.exec_()

    if msg.clickedButton() == btn_old:
        extractor = extract_themes_old_format
    elif msg.clickedButton() == btn_new:
        extractor = extract_themes_from_diversity_expression
    else:
        return

    dialog = LoadingDialog("Insertion du document Word...", parent)
    dialog.show()
    QApplication.processEvents()

    try:
        conn = sqlite3.connect("global.db")
        cursor = conn.cursor()

        lines = extract_lines_from_docx(path)
        source_name = os.path.basename(path)
        seen_ids = set()
        current_id = None
        current_text = []

        for line in lines:
            match = re.search(r'REQ[-]?\d{7}[\s]*[A-Z]\b', line)
            if match:
                raw_id = match.group(0).strip().replace("_", " ")
                if current_id and current_text:
                    full_text = "\n".join(current_text)
                    insert_requirement(current_id, full_text, extractor, source_name, cursor, seen_ids)
                current_id = normalize_id(raw_id)
                current_text = [line]
            elif current_id:
                current_text.append(line)

        if current_id and current_text:
            full_text = "\n".join(current_text)
            insert_requirement(current_id, full_text, extractor, source_name, cursor, seen_ids)

        conn.commit()
        conn.close()

        QMessageBox.information(parent, "Succès", "Les exigences ont été ajoutés à la base de données.")
    finally:
        dialog.close()
