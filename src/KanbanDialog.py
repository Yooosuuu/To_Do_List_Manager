from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QDialogButtonBox, QLabel, QListWidget, QListWidgetItem, QMenu
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtGui import QColor, QIcon, QAction

from TaskDetailsDialog import TaskDetailsDialog
from utils import resource_path

# Classe pour afficher le tableau Kanban
class KanbanDialog(QDialog):
    COLUMNS = ["Non commencé", "En cours", "Bientôt fini", "Terminé"]

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Kanban Board")
        self.setWindowIcon(QIcon(resource_path("icon/kanban.png")))
        self.setup_ui()
        self.load_tasks()
        self.setGeometry(200, 300, 1200, 300)

        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        self.columns_layout = QHBoxLayout()

        self.lists = {}
        for col in self.COLUMNS:
            vbox = QVBoxLayout()
            label = QLabel(col, self)
            vbox.addWidget(label)
            list_widget = QListWidget(self)
            list_widget.setObjectName(col)
            list_widget.itemDoubleClicked.connect(self.show_task_details)  # 🆕 Lien avec le double-clic
            vbox.addWidget(list_widget)
            self.lists[col] = list_widget
            self.columns_layout.addLayout(vbox)

        main_layout.addLayout(self.columns_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        button_box.accepted.connect(self.accept)
        main_layout.addWidget(button_box)

    def show_task_details(self, item):
        """ Affiche la boîte de dialogue des détails d'une tâche lors d'un double-clic """
        task_id = item.data(Qt.ItemDataRole.UserRole)
        task_info = self.db.get_task_by_id(task_id)
        if task_info:
            subtasks = self.db.get_subtasks(task_id)
            details_dialog = TaskDetailsDialog(task_info, subtasks, self)
            details_dialog.exec()
            
    def refresh(self):
        """ Rafraîchit le tableau Kanban """
        self.load_tasks()

    def load_tasks(self):
        # Efface toutes les listes
        colors = {
            "Faible": "#A3BE8C",  # Vert doux
            "Normale": "#EBCB8B",  # Jaune pastel
            "Haute": "#BF616A",    # Rouge atténué
            "Terminée": "#88C0D0"  # Bleu clair
        }
        for lw in self.lists.values():
            lw.clear()
        tasks = self.db.sort_tasks()
        for task in tasks:
            # task: (id, task, priority, status, description, progress, duration, deadline)
            progress = task[5]
            if progress != "Terminé":
                text = f"{task[1]} (Priorité : {task[2]})"
            else:
                text = task[1]
            item = QListWidgetItem(text)
            # Stocker l'ID dans l'item
            item.setData(Qt.ItemDataRole.UserRole, task[0])
            if task[2] in colors:
                if progress != "Terminé":
                    item.setForeground(QColor(colors[task[2]]))
                else:
                    item.setForeground(QColor(colors["Terminée"]))
            # Ajouter l'item dans la bonne colonne selon progress
            if progress in self.COLUMNS:
                self.lists[progress].addItem(item)
            else:
                # Si progress n'est pas reconnu, on l'ajoute dans "Non commencé" par défaut
                self.lists["Non commencé"].addItem(item)