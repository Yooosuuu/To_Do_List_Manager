from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QComboBox, QPushButton, QLabel, QListWidget, QMenu, QMessageBox, QDialog
)
from PyQt6.QtGui import QColor, QAction, QKeySequence, QShortcut, QIcon
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

from EditTaskDialog import EditTaskDialog 
from TaskDetailsDialog import TaskDetailsDialog
from AgendaDialog import AgendaDialog
from KanbanDialog import KanbanDialog
from database import Database
from ProgressionBar import SmoothProgressBar
from utils import resource_path

# Classe principale du gestionnaire de tâches
class TaskManager(QWidget):
    def __init__(self):
        super().__init__()
        self.zoom = 16
        self.setStyleSheet(f"font-size: {self.zoom}px;")
        self.setWindowTitle("Gestionnaire de Tâches")
        self.setWindowIcon(QIcon(resource_path("icon/logo.png")))
        self.setGeometry(100, 100, 500, 700)

        self.db = Database()

        self.layout = QVBoxLayout()

        # Ajout d'un indicateur global de progression
        self.last_progress = 0
        self.global_progress = SmoothProgressBar(self, self.zoom)
        self.global_progress.setFixedHeight(int(30*self.zoom/16))
        self.layout.addWidget(self.global_progress)
        
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

        # Liste des tâches actives
        self.layout.addWidget(QLabel("Tâches en cours :"))
        self.task_list = QListWidget(self)
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        self.task_list.itemDoubleClicked.connect(self.show_task_details)
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
        
        # Bouton Agenda pour passer en mode agenda
        self.agenda_dialog = None
        self.agenda_button = QPushButton("Afficher l'agenda", self)
        self.agenda_button.clicked.connect(self.open_agenda)
        self.layout.addWidget(self.agenda_button)
        
        # Bouton Kanban pour passer en mode Kanban
        self.kanban_dialog = None
        self.kanban_button = QPushButton("Afficher Kanban", self)
        self.kanban_button.clicked.connect(self.open_kanban)
        self.layout.addWidget(self.kanban_button)
        
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
            "Terminée": "lightblue"
        }
        if sort:
            tasks = self.db.sort_tasks()
        else:
            tasks = self.db.get_tasks()
        total = len(tasks)
        completed = 0
        for task in tasks:
            task_id = task[0]
            task_text = task[1]
            task_priority = task[2]
            task_status = task[3]
            if task_status == "Terminée":
                completed += 1
            display_text = f"{task_text}"
            display_text_with_priority = f"{task_text}   (Priorité : {task_priority})"
            if task_status == "Terminée":
                self.completed_list.addItem(display_text)
                item_widget = self.completed_list.item(self.completed_list.count() - 1)
                item_widget.setData(Qt.ItemDataRole.UserRole, task_id)
                item_widget.setForeground(QColor(color["Terminée"]))
            else:
                self.task_list.addItem(display_text_with_priority)
                item_widget = self.task_list.item(self.task_list.count() - 1)
                item_widget.setData(Qt.ItemDataRole.UserRole, task_id)
                if task_priority in color:
                    item_widget.setForeground(QColor(color[task_priority]))
        # Mise à jour de la barre de progression globale
        progress_value = int((completed / total) * 100) if total > 0 else 0
        if progress_value != self.last_progress:
            self.animate_progress_bar(progress_value)
            self.last_progress = progress_value
        if self.kanban_dialog and self.kanban_dialog.isVisible():
            self.kanban_dialog.refresh()
        if self.agenda_dialog and self.agenda_dialog.isVisible():
            self.agenda_dialog.update_task_list()
    
    def animate_progress_bar(self, value):
        self.progress_animation = QPropertyAnimation(self.global_progress, b"animatedValue")
        self.progress_animation.setDuration(2000)  # Ajustez la durée si nécessaire
        self.progress_animation.setStartValue(self.global_progress.getAnimatedValue())
        self.progress_animation.setEndValue(float(value))
        self.progress_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.progress_animation.start()
        

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
            dialog = EditTaskDialog(task_details, self.db, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_data()
                if data["task"]:
                    self.db.update_task_details(task_id,
                                                data["task"],
                                                data["priority"],
                                                data["description"],
                                                data["progress"],
                                                data["duration"],
                                                data["deadline"])
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
        self.db.update_task_progress(task_id, "Terminé")
        self.load_tasks()

    def mark_selected_task_completed(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            task_id = selected_item.data(Qt.ItemDataRole.UserRole)
            self.mark_task_completed(task_id)
        else:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une tâche à terminer !")

    def open_agenda(self):
        if self.agenda_dialog and self.agenda_dialog.isVisible():
            self.agenda_dialog.raise_()
            return
        agenda_dialog = AgendaDialog(self.db,self)
        agenda_dialog.setWindowModality(Qt.WindowModality.NonModal)
        agenda_dialog.show()
        
    def open_kanban(self):
        if self.kanban_dialog and self.kanban_dialog.isVisible():
            self.kanban_dialog.raise_()
            return
        self.kanban_dialog = KanbanDialog(self.db, self)
        self.kanban_dialog.setWindowModality(Qt.WindowModality.NonModal)
        self.kanban_dialog.show()

    
    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom += 1
            elif delta < 0 and self.zoom > 1:
                self.zoom -= 1
            self.setStyleSheet(f"font-size: {self.zoom}px;")
            self.global_progress.set_zoom(self.zoom)
            self.global_progress.setFixedHeight(int(30*(self.zoom/16)))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
