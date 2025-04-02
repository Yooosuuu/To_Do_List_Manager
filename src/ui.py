from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QLineEdit, QMessageBox, QComboBox, QLabel,
    QMenu, QInputDialog, QApplication, QDialog, QFormLayout, QDialogButtonBox, QListWidgetItem, QHBoxLayout
)
from PyQt6.QtGui import QColor, QAction, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QEvent

from database import Database

class EditTaskDialog(QDialog):
    def __init__(self, task_details, db, parent=None):
        """
        task_details est un tuple : (id, task, priority, status, description, progress, duration)
        db est l'instance de Database pour récupérer et mettre à jour les sous-tâches.
        """
        super().__init__(parent)
        self.setWindowTitle("Modifier la tâche")
        self.task_details = task_details
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        self.layout = QFormLayout(self)

        self.task_edit = QLineEdit(self)
        self.task_edit.setText(self.task_details[1])
        self.layout.addRow("Tâche:", self.task_edit)

        self.priority_combo = QComboBox(self)
        self.priority_combo.addItems(["Faible", "Normale", "Haute"])
        index = self.priority_combo.findText(self.task_details[2])
        if index != -1:
            self.priority_combo.setCurrentIndex(index)
        self.layout.addRow("Priorité:", self.priority_combo)

        self.description_edit = QLineEdit(self)
        self.description_edit.setText(self.task_details[4] if self.task_details[4] else "")
        self.layout.addRow("Description:", self.description_edit)

        self.progress_combo = QComboBox(self)
        self.progress_combo.addItems(["Non commencé", "En cours", "Bientôt fini", "Terminé"])
        index = self.progress_combo.findText(self.task_details[5])
        if index != -1:
            self.progress_combo.setCurrentIndex(index)
        self.layout.addRow("Avancement:", self.progress_combo)

        self.duration_combo = QComboBox(self)
        self.duration_combo.addItems(["0-1h", "1-2h", "2-4h", "4-8h", "8-12h", "12-24h", "+24h"])
        index = self.duration_combo.findText(self.task_details[6])
        if index != -1:
            self.duration_combo.setCurrentIndex(index)
        self.layout.addRow("Durée:", self.duration_combo)

        # Sous-tâches
        self.subtask_list = QListWidget(self)
        self.load_subtasks()
        self.layout.addRow("Sous-tâches:", self.subtask_list)

        # Zone pour ajouter une nouvelle sous-tâche
        self.new_subtask_edit = QLineEdit(self)
        self.new_subtask_edit.setPlaceholderText("Ajouter une sous-tâche")
        self.new_subtask_edit.returnPressed.connect(self.add_subtask)
        # Bouton pour ajouter la sous-tâche
        self.add_subtask_button = QPushButton("Ajouter", self)
        self.add_subtask_button.clicked.connect(self.add_subtask)
        subtask_layout = QHBoxLayout()
        subtask_layout.addWidget(self.new_subtask_edit)
        subtask_layout.addWidget(self.add_subtask_button)
        self.layout.addRow("Nouvelle sous-tâche:", subtask_layout)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        # Gestion du clic sur les items pour changer l'état
        self.subtask_list.itemChanged.connect(self.subtask_state_changed)

    def load_subtasks(self):
        self.subtask_list.clear()
        task_id = self.task_details[0]
        subtasks = self.db.get_subtasks(task_id)
        for sub in subtasks:
            # sub est un tuple : (id, description, done)
            item = QListWidgetItem(sub[1])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if sub[2] else Qt.CheckState.Unchecked)
            # Stocker l'ID de la sous-tâche dans l'item
            item.setData(Qt.ItemDataRole.UserRole, sub[0])
            self.subtask_list.addItem(item)

    def add_subtask(self):
        description = self.new_subtask_edit.text().strip()
        if description:
            task_id = self.task_details[0]
            self.db.add_subtask(task_id, description)
            self.new_subtask_edit.clear()
            self.load_subtasks()

    def subtask_state_changed(self, item):
        subtask_id = item.data(Qt.ItemDataRole.UserRole)
        done = item.checkState() == Qt.CheckState.Checked
        self.db.update_subtask_status(subtask_id, done)

    def get_data(self):
        return {
            "task": self.task_edit.text().strip(),
            "priority": self.priority_combo.currentText(),
            "description": self.description_edit.text().strip(),
            "progress": self.progress_combo.currentText(),
            "duration": self.duration_combo.currentText()
        }

class TaskDetailsDialog(QDialog):
    def __init__(self, task_info, subtasks, parent=None):
        """
        task_info : tuple (id, task, priority, status, description, progress, duration)
        subtasks : liste de tuples (id, description, done)
        """
        super().__init__(parent)
        self.setWindowTitle("Détails de la Tâche")
        self.setup_ui(task_info, subtasks)

    def setup_ui(self, task_info, subtasks):
        layout = QVBoxLayout(self)
        
        # Création du contenu HTML pour un affichage plus joli
        details_html = f"""
        <h2>{task_info[1]}</h2>
        <p><b>Priorité :</b> {task_info[2]}</p>
        <p><b>Statut :</b> {task_info[3]}</p>
        <p><b>Description :</b> {task_info[4] if task_info[4] else 'Aucune'}</p>
        <p><b>Avancement :</b> {task_info[5]}</p>
        <p><b>Durée :</b> {task_info[6]}</p>
        <hr>
        <h3>Sous-tâches :</h3>
        """
        if subtasks:
            details_html += "<ul>"
            for sub in subtasks:
                # Utilise une coche pour indiquer l'état de la sous-tâche
                check = "&#10004;" if sub[2] else "&#10008;"
                details_html += f"<li>{check} {sub[1]}</li>"
            details_html += "</ul>"
        else:
            details_html += "<p>Aucune sous-tâche</p>"

        label = QLabel(details_html, self)
        label.setWordWrap(True)
        layout.addWidget(label)

        # Bouton OK pour fermer la fenêtre
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

class TaskManager(QWidget):
    def __init__(self):
        super().__init__()
        self.zoom = 14
        self.setWindowTitle("Gestionnaire de Tâches")
        self.setGeometry(100, 100, 500, 700)

        self.db = Database()

        self.layout = QVBoxLayout()

        # Champ de saisie pour la tâche
        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Ajouter une nouvelle tâche")
        self.task_input.returnPressed.connect(self.add_task)  # Ajout avec la touche Enter
        self.layout.addWidget(self.task_input)

        # Sélecteur de priorité
        self.priority_selector = QComboBox(self)
        self.priority_selector.addItems(["Faible", "Normale", "Haute"])
        self.layout.addWidget(self.priority_selector)

        # Bouton pour ajouter une tâche
        self.add_button = QPushButton("Ajouter Tâche", self)
        self.add_button.clicked.connect(self.add_task)
        self.layout.addWidget(self.add_button)
        
        # Bouton pour trier les tâches
        self.sort_button = QPushButton("Trier Tâches", self)
        self.sort_button.clicked.connect(self.sort_tasks)
        self.layout.addWidget(self.sort_button)

        # Liste des tâches actives
        self.layout.addWidget(QLabel("Tâches en cours :"))
        self.task_list = QListWidget(self)
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        self.task_list.itemClicked.connect(self.show_task_details)
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

        # Bouton pour supprimer une tâche (active)
        self.delete_button = QPushButton("Supprimer Tâche", self)
        self.delete_button.clicked.connect(self.delete_task)
        self.layout.addWidget(self.delete_button)
        
        self.setMouseTracking(True)
        self.setLayout(self.layout)
        self.load_tasks()

        # Raccourcis clavier
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self, activated=self.delete_task)
        QShortcut(QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_Return), self, activated=self.mark_selected_task_completed)

    def load_tasks(self, sort=True):
        self.task_list.clear()
        self.completed_list.clear()
        color = {
            "Faible": "lightgreen",
            "Normale": "yellow",
            "Haute": "red",
            "Terminée": "lightgray"
        }
        if sort:
            tasks = self.db.sort_tasks()
        else:
            tasks = self.db.get_tasks()
        for task in tasks:
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
            self.sort_tasks()
        else:
            QMessageBox.warning(self, "Erreur", "La tâche ne peut pas être vide !")

    def delete_task(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            task_id = selected_item.data(Qt.ItemDataRole.UserRole)
            self.db.delete_task(task_id)
            self.load_tasks()
        else:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une tâche à supprimer !")
            
    def sort_tasks(self):
        self.load_tasks(sort=True)        
    
    def clear_completed_tasks(self):
        self.db.clear_completed()
        self.load_tasks()

    def show_context_menu(self, pos):
        context_menu = QMenu(self)
        selected_item = self.task_list.itemAt(pos)
        if selected_item:
            task_id = selected_item.data(Qt.ItemDataRole.UserRole)
            
            edit_action = QAction("Modifier", self)
            edit_action.triggered.connect(lambda: self.edit_task(task_id))
            context_menu.addAction(edit_action)

            complete_action = QAction("Marquer comme terminée", self)
            complete_action.triggered.connect(lambda: self.mark_task_completed(task_id))
            context_menu.addAction(complete_action)
            
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
        task_details = self.db.get_task(task_id)
        if task_details:
            # On passe l'instance de la db à la dialog pour gérer les sous-tâches
            dialog = EditTaskDialog(task_details, self.db, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if data["task"]:
                    self.db.update_task_details(task_id,
                                                data["task"],
                                                data["priority"],
                                                data["description"],
                                                data["progress"],
                                                data["duration"])
                    self.load_tasks()
                else:
                    QMessageBox.warning(self, "Erreur", "Le texte de la tâche ne peut pas être vide !")

    def show_task_details(self, item):
        # item est un QListWidgetItem
        task_id = item.data(Qt.ItemDataRole.UserRole)
        task_info = self.db.get_task_by_id(task_id)
        if task_info:
            # Récupérer les sous-tâches associées
            subtasks = self.db.get_subtasks(task_id)
            details_dialog = TaskDetailsDialog(task_info, subtasks, self)
            details_dialog.exec()


    def mark_task_completed(self, task_id):
        self.db.update_task_status(task_id, "Terminée")
        self.load_tasks()

    def mark_selected_task_completed(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            task_id = selected_item.data(Qt.ItemDataRole.UserRole)
            self.mark_task_completed(task_id)
        else:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une tâche à terminer !")

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom += 1
            elif delta < 0 and self.zoom > 1:
                self.zoom -= 1
            self.setStyleSheet(f"font-size: {self.zoom}px;")

    def closeEvent(self, event):
        self.db.close()
        event.accept()
