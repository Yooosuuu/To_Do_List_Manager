from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Classe pour afficher les détails d'une tâche
class TaskDetailsDialog(QDialog):
    def __init__(self, task_info, subtasks, parent=None):
        """
        task_info : tuple (id, task, priority, status, description, progress, duration, deadline)
        subtasks : liste de tuples (id, description, done)
        """
        super().__init__(parent)
        icon = QIcon("path/to/icon.png")
        self.setWindowTitle("Détails de la Tâche")
        self.setWindowIcon(QIcon("icon/loupe.png"))
        self.setup_ui(task_info, subtasks)

    def setup_ui(self, task_info, subtasks):
        layout = QVBoxLayout(self)
        
        # Création du contenu HTML avec CSS pour un affichage plus joli
        details_html = f"""
        <style>
            h2 {{
            color: #ebebeb;
            font-family: Arial, sans-serif;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
            }}
            h3 {{
            color: #ebebeb;
            font-family: Arial, sans-serif;
            margin-top: 20px;
            margin-bottom: 5px;
            }}
            p {{
            font-family: Arial, sans-serif;
            color: #c2c2c2;
            margin: 5px 0;
            }}
            b {{
            color: #ebebeb;
            }}
            ul {{
            list-style-type: none;
            padding: 0;
            }}
            li {{
            font-family: Arial, sans-serif;
            color: #c2c2c2;
            margin: 5px 0;
            }}
            li::before {{
            content: "\\2022";
            color: #3498db;
            font-weight: bold;
            display: inline-block;
            width: 1em;
            margin-left: -1em;
            }}
            .check {{
            color: green;
            font-weight: bold;
            }}
            .uncheck {{
            color: red;
            font-weight: bold;
            }}
            hr {{
            border: 0;
            height: 1px;
            background: #ebebeb;
            margin: 20px 0;
            }}
        </style>
        <h2>{task_info[1]}</h2>
        <p><b>Priorité :</b> {task_info[2]}</p>
        <p><b>Statut :</b> {task_info[3]}</p>
        <p><b>Description :</b> {task_info[4] if task_info[4] else 'Aucune'}</p>
        <p><b>Avancement :</b> {task_info[5]}</p>
        <p><b>Durée :</b> {task_info[6]}</p>
        <p><b>Deadline :</b> {task_info[7] if task_info[7] else 'Aucune'}</p>
        <hr>
        <h3>Sous-tâches :</h3>
        """
        if subtasks:
            details_html += "<ul>"
            for sub in subtasks:
                # Utilise une coche pour indiquer l'état de la sous-tâche
                check = f"<span class='check'>&#10004;</span>" if sub[2] else f"<span class='uncheck'>&#10008;</span>"
                details_html += f"<li>{check} {sub[1]}</li>"
            details_html += "</ul>"
        else:
            details_html += "<p>Aucune sous-tâche</p>"

        label = QLabel(details_html, self)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)  # Ensure the QLabel renders HTML
        layout.addWidget(label)

        # Bouton OK pour fermer la fenêtre
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
