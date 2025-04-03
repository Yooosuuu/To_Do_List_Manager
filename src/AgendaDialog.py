from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCalendarWidget, QListWidget, QDialogButtonBox
from PyQt6.QtGui import QIcon

# Classe pour afficher l'agenda
class AgendaDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agenda")
        self.setWindowIcon(QIcon("icon/agenda.png"))
        self.db = db
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.update_task_list)
        layout.addWidget(self.calendar)
        
        self.task_list = QListWidget(self)
        layout.addWidget(self.task_list)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, self)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
        self.update_task_list()
        
    def update_task_list(self):
        self.task_list.clear()
        selected_date = self.calendar.selectedDate().toString("dd/MM/yyyy")
        # Filtrer les tâches dont la deadline correspond à la date sélectionnée
        tasks = self.db.get_tasks()
        for task in tasks:
            deadline = task[7]  # colonne deadline
            if deadline == selected_date:
                display_text = f"{task[1]} (Priorité : {task[2]})"
                self.task_list.addItem(display_text)
