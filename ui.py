from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QLineEdit, QMessageBox, QComboBox, QLabel,
    QMenu, QInputDialog
)
from PyQt6.QtGui import QColor, QAction
from PyQt6.QtCore import Qt

from database import Database

class TaskManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestionnaire de Tâches")
        self.setGeometry(100, 100, 500, 700)

        self.db = Database()

        self.layout = QVBoxLayout()

        # Champ de saisie pour la tâche
        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Ajouter une nouvelle tâche")
        self.layout.addWidget(self.task_input)

        # Sélecteur de priorité
        self.priority_selector = QComboBox(self)
        self.priority_selector.addItems(["Faible", "Normale", "Haute"])
        self.layout.addWidget(self.priority_selector)

        # Bouton pour ajouter une tâche
        self.add_button = QPushButton("Ajouter Tâche", self)
        self.add_button.clicked.connect(self.add_task)
        self.layout.addWidget(self.add_button)

        # Liste des tâches actives
        self.layout.addWidget(QLabel("Tâches en cours :"))
        self.task_list = QListWidget(self)
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        self.layout.addWidget(self.task_list)
        
        # Liste des tâches terminées
        self.layout.addWidget(QLabel("Tâches terminées :"))
        self.completed_list = QListWidget(self)
        self.completed_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.completed_list.customContextMenuRequested.connect(self.show_context_menu_completed)
        self.layout.addWidget(self.completed_list)
        
        # Bouton pour vider les tâches terminées
        self.clear_completed_button = QPushButton("Vider les tâches terminées", self)
        self.clear_completed_button.clicked.connect(self.clear_completed_tasks)
        self.layout.addWidget(self.clear_completed_button)

        # Bouton pour supprimer une tâche(active)
        self.delete_button = QPushButton("Supprimer Tâche", self)
        self.delete_button.clicked.connect(self.delete_task)
        self.layout.addWidget(self.delete_button)

        self.setLayout(self.layout)

        self.load_tasks()

    def load_tasks(self):
        self.task_list.clear()
        self.completed_list.clear()
        color = {
            "Faible": "lightgreen",
            "Normale": "yellow",
            "Haute": "red",
            "Terminée": "lightgray"
        }
        for task in self.db.get_tasks():
            task_id = task[0]
            task_text = task[1]
            task_priority = task[2]
            task_status = task[3]

            display_text = f"{task_text} (Priorité : {task_priority})"
            if task_status == "Terminée":
                self.completed_list.addItem(display_text)
                item_widget = self.completed_list.item(self.completed_list.count() - 1)
                item_widget.setData(Qt.ItemDataRole.UserRole, task_id)
                item_widget.setForeground(QColor(color["Terminée"]))
            else:
                self.task_list.addItem(display_text)
                item_widget = self.task_list.item(self.task_list.count() - 1)
                item_widget.setData(Qt.ItemDataRole.UserRole, task_id)
                if task_priority in color:
                    item_widget.setForeground(QColor(color[task_priority]))

    def add_task(self):
        task_text = self.task_input.text().strip()
        priority = self.priority_selector.currentText()
        if task_text:
            self.db.add_task(task_text, priority)
            self.task_input.clear()
            self.load_tasks()
        else:
            QMessageBox.warning(self, "Erreur", "La tâche ne peut pas être vide !")

    def delete_task(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            # Récupérer l'ID stocké dans UserRole
            task_id = selected_item.data(Qt.ItemDataRole.UserRole)
            self.db.delete_task(task_id)
            self.load_tasks()
        else:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une tâche à supprimer !")
    
    def clear_completed_tasks(self):
        self.db.clear_completed()
        self.load_tasks()

    def show_context_menu(self, pos):
        context_menu = QMenu(self)
        selected_item = self.task_list.itemAt(pos)
        if selected_item:
            task_id = selected_item.data(Qt.ItemDataRole.UserRole)
            
            # Action pour modifier la tâche
            edit_action = QAction("Modifier", self)
            edit_action.triggered.connect(lambda: self.edit_task(task_id))
            context_menu.addAction(edit_action)

            # Action pour marquer comme terminée
            complete_action = QAction("Marquer comme terminée", self)
            complete_action.triggered.connect(lambda: self.mark_completed(task_id))
            context_menu.addAction(complete_action)

            # Action pour modifier la priorité
            priority_action = QAction("Modifier Priorité", self)
            priority_action.triggered.connect(lambda: self.change_priority(task_id))
            context_menu.addAction(priority_action)
            
            # Action pour supprimer la tâche
            delete_action = QAction("Supprimer", self)
            delete_action.triggered.connect(lambda: self.delete_task())
            context_menu.addAction(delete_action)

            context_menu.exec(self.task_list.mapToGlobal(pos))
            
    def show_context_menu_completed(self, pos):
        context_menu = QMenu(self)
        selected_item = self.completed_list.itemAt(pos)
        if selected_item:
            task_id = selected_item.data(Qt.ItemDataRole.UserRole)
            delete_action = QAction("Supprimer", self)
            delete_action.triggered.connect(lambda: self.delete_completed_task(task_id))
            context_menu.addAction(delete_action)
            context_menu.exec(self.completed_list.mapToGlobal(pos))
            
    def delete_completed_task(self, task_id):
        self.db.delete_task(task_id)
        self.load_tasks()

    def edit_task(self, task_id):
        # Chercher l'item correspondant à task_id pour pré-remplir le texte
        current_text = ""
        for index in range(self.task_list.count()):
            item = self.task_list.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == task_id:
                # Extraire uniquement le texte de la tâche (avant le " (Priorité :")
                current_text = item.text().split(" (Priorité :")[0]
                break
        new_text, ok = QInputDialog.getText(self, "Modifier la tâche", "Nouvelle tâche :", text=current_text)
        if ok and new_text:
            self.db.update_task_text(task_id, new_text)
            self.load_tasks()

    def mark_completed(self, task_id):
        # On peut par exemple modifier le statut de la tâche
        self.db.update_task_status(task_id, "Terminée")
        self.load_tasks()

    def change_priority(self, task_id):
        priority, ok = QInputDialog.getItem(self, "Modifier Priorité", "Choisir la priorité :", ["Faible", "Normale", "Haute"], editable=False)
        if ok:
            self.db.update_priority(task_id, priority)
            self.load_tasks()

    def closeEvent(self, event):
        self.db.close()
        event.accept()
