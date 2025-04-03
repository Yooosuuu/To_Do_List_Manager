from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit, QListWidget, 
    QPushButton, QHBoxLayout, QDialogButtonBox, QListWidgetItem
)
from PyQt6.QtCore import Qt, QDate

# Classe pour éditer une tâche
class EditTaskDialog(QDialog):
    def __init__(self, task_details, db, parent=None):
        super().__init__(parent)
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

        # Ajout de la deadline avec un QDateEdit
        self.deadline_edit = QDateEdit(self)
        self.deadline_edit.setCalendarPopup(True)
        if self.task_details[7]:
            date = QDate.fromString(self.task_details[7], "dd/MM/yyyy")
            if date.isValid():
                self.deadline_edit.setDate(date)
            else:
                self.deadline_edit.setDate(QDate.currentDate())
        else:
            self.deadline_edit.setDate(QDate.currentDate())
        self.layout.addRow("Deadline:", self.deadline_edit)

        # Sous-tâches
        self.subtask_list = QListWidget(self)
        self.load_subtasks()   # Assure-toi que load_subtasks est défini ci-dessous.
        self.layout.addRow("Sous-tâches:", self.subtask_list)

        self.new_subtask_edit = QLineEdit(self)
        self.new_subtask_edit.setPlaceholderText("Ajouter une sous-tâche")
        self.new_subtask_edit.returnPressed.connect(self.add_subtask)
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

        self.subtask_list.itemChanged.connect(self.subtask_state_changed)

    def load_subtasks(self):
        self.subtask_list.clear()
        task_id = self.task_details[0]
        subtasks = self.db.get_subtasks(task_id)
        for sub in subtasks:
            item = QListWidgetItem(sub[1])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if sub[2] else Qt.CheckState.Unchecked)
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
        deadline_str = self.deadline_edit.date().toString("dd/MM/yyyy") if self.deadline_edit.date().isValid() else None
        return {
            "task": self.task_edit.text().strip(),
            "priority": self.priority_combo.currentText(),
            "description": self.description_edit.text().strip(),
            "progress": self.progress_combo.currentText(),
            "duration": self.duration_combo.currentText(),
            "deadline": deadline_str
        }
