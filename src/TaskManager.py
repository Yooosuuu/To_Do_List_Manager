from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QComboBox, QPushButton, QLabel, QListWidget, QMenu, QMessageBox, QDialog
)
from PyQt6.QtGui import QColor, QIcon, QAction, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve

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
        self.setWindowTitle("Gestionnaire de Tâches")
        self.setWindowIcon(QIcon(resource_path("icon/logo.png")))
        self.setGeometry(100, 100, 700, 700)
        self.apply_stylesheet()

        self.db = Database()

        # Panneau principal
        self.main_layout = QVBoxLayout(self)
        self.last_progress = 0
        self.global_progress = SmoothProgressBar(self, self.zoom)
        self.global_progress.setFixedHeight(int(30 * self.zoom / 16))
        self.main_layout.addWidget(self.global_progress)

        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Ajouter une nouvelle tâche")
        self.task_input.returnPressed.connect(self.add_task)
        self.main_layout.addWidget(self.task_input)

        self.priority_selector = QComboBox(self)
        self.priority_selector.addItems(["Faible", "Normale", "Haute"])
        self.main_layout.addWidget(self.priority_selector)

        self.add_button = QPushButton("Ajouter Tâche", self)
        self.add_button.clicked.connect(self.add_task)
        self.main_layout.addWidget(self.add_button)

        self.main_layout.addWidget(QLabel("Tâches en cours :"))
        self.task_list = QListWidget(self)
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        self.task_list.itemDoubleClicked.connect(self.show_task_details)
        self.main_layout.addWidget(self.task_list)

        self.main_layout.addWidget(QLabel("Tâches terminées :"))
        self.completed_list = QListWidget(self)
        self.completed_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.completed_list.customContextMenuRequested.connect(self.show_context_menu_completed)
        self.main_layout.addWidget(self.completed_list)

        # Ajouter le bouton pour ouvrir/fermer le panneau latéral
        self.toggle_button = QPushButton(self)
        self.toggle_button.setIcon(QIcon(resource_path("icon/menu.png")))  # Icône de menu hamburger
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        self.main_layout.addWidget(self.toggle_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Panneau latéral flottant
        self.sidebar = QWidget(self)
        self.sidebar.setStyleSheet("background-color: #3B4252;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        # Ajout des options dans le panneau latéral
        self.category_filter = QLineEdit(self)
        self.category_filter.setPlaceholderText("Filtrer par catégorie")
        self.category_filter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.category_filter.textChanged.connect(self.filter_tasks_by_category)
        self.sidebar_layout.addWidget(self.category_filter)

        self.clear_button = QPushButton("Vider les tâches terminées", self)
        self.clear_button.clicked.connect(self.clear_completed_tasks)
        self.sidebar_layout.addWidget(self.clear_button)

        self.agenda_dialog = None
        self.agenda_button = QPushButton("Afficher l'agenda", self)
        self.agenda_button.clicked.connect(self.open_agenda)
        self.sidebar_layout.addWidget(self.agenda_button)

        self.kanban_dialog = None
        self.kanban_button = QPushButton("Afficher Kanban", self)
        self.kanban_button.clicked.connect(self.open_kanban)
        self.sidebar_layout.addWidget(self.kanban_button)

        self.sidebar.hide()  # Masquer le panneau latéral par défaut
        self.main_layout.addWidget(self.sidebar)
        

        self.setLayout(self.main_layout)

        self.load_tasks()
        
        self.add_shortcuts()

    def add_shortcuts(self):
        """Ajoute des raccourcis clavier pour certaines actions."""
        # Raccourci pour ouvrir/fermer le panneau latéral
        toggle_sidebar_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        toggle_sidebar_shortcut.activated.connect(self.toggle_sidebar)

        # Raccourci pour ajouter une tâche
        add_task_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        add_task_shortcut.activated.connect(self.add_task)

        # Raccourci pour vider les tâches terminées
        clear_completed_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        clear_completed_shortcut.activated.connect(self.clear_completed_tasks)
        
        # Raccourci pour marquer une tâche comme terminée
        mark_completed_shortcut = QShortcut(QKeySequence("Ctrl+Enter"), self)
        mark_completed_shortcut.activated.connect(self.mark_selected_task_completed)
        
        # Raccourci pour supprimer une tâche
        delete_task_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_task_shortcut.activated.connect(self.delete_task)
        
        # Raccourci pour afficher le kanban
        kanban_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        kanban_shortcut.activated.connect(self.open_kanban)

    def toggle_sidebar(self):
        """Afficher ou masquer le panneau latéral avec une animation."""
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()          

    def apply_stylesheet(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #2E3440;  /* Couleur de fond sombre */
                color: #D8DEE9;            /* Couleur du texte */
                font-size: {self.zoom}px; /* Taille de la police */
            }}
            QLineEdit, QComboBox, QPushButton, QListWidget {{
                background-color: #3B4252; /* Couleur de fond des widgets */
                color: #ECEFF4;            /* Couleur du texte des widgets */
                border: 1px solid #4C566A;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #4C566A; /* Couleur au survol */
            }}
        """)

    def filter_tasks_by_category(self):
        category = self.category_filter.text().strip()
        self.load_tasks(filter_category=category)

    def load_tasks(self, sort=True, filter_category=None):
        self.task_list.clear()
        self.completed_list.clear()
        color = {
            "Faible": "#A3BE8C",  # Vert doux
            "Normale": "#EBCB8B",  # Jaune pastel
            "Haute": "#BF616A",    # Rouge atténué
            "Terminée": "#88C0D0"  # Bleu clair
        }
        tasks = self.db.sort_tasks() if sort else self.db.get_tasks()
        if filter_category:
            filtered_tasks = []
            for task in tasks:
                if task[8] and str(filter_category).lower() in task[8].lower():
                    filtered_tasks.append(task)
            tasks = filtered_tasks
        # Affichage des tâches dans la liste
        total = len(tasks)
        completed = 0
        for task in tasks:
            task_id, task_text, task_priority, task_status, _, _, _, _, task_category = task
            if task_status == "Terminée":
                completed += 1
            display_text = f"{task_text} (Catégorie : {task_category})" if task_category else task_text
            display_text_with_priority = f"{display_text}   (Priorité : {task_priority})"
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
        selected_item = None
        if self.task_list.currentItem():
            selected_item = self.task_list.currentItem()
        elif self.completed_list.currentItem():
            selected_item = self.completed_list.currentItem()
        if selected_item is not None:
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
                                                data["deadline"],
                                                data["category"])
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
        agenda_dialog = AgendaDialog(self.db, self)
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

            # Appliquer la feuille de style avec le zoom mis à jour
            self.apply_stylesheet()

            # Mettre à jour la taille de la barre de progression
            self.global_progress.set_zoom(self.zoom)
            self.global_progress.setFixedHeight(int(30 * (self.zoom / 16)))

    def closeEvent(self, event):
        self.db.close()
        event.accept()
