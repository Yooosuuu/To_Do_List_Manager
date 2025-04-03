# To Do List Manager

**To Do List Manager** est une application de gestion de tâches développée en Python, utilisant PyQt6 pour l'interface graphique et sqlite3 pour la gestion des données. Cette application vous aide à organiser vos tâches personnelles et/ou professionnelles de manière efficace.

## Fonctionnalités

- **Gestion des tâches** : Ajouter, modifier, supprimer et organiser vos tâches.
- **Suivi de l'avancement** : Classement des tâches par statut ("À faire", "En cours", "Terminé").
- **Interface intuitive** : Une interface graphique claire et accessible pour une utilisation quotidienne.
- **Gestion des priorités** : Assigner des priorités aux tâches pour mieux les organiser.
- **Une interface Kanban** : Possibilité de passer sur une interface Kanban

## Prérequis

Avant d'utiliser cette application, assurez-vous d'avoir installé Python ainsi que les bibliothèques suivantes :

- Python 3.x (testé avec Python 3.13)
- PyQt6
- sqlite3

Installation des dépendances :

```sh
pip install pyqt6 sqlite3
```

## Installation

1. Clonez ce dépôt :
   ```sh
   git clone https://github.com/ton-username/task-manager.git
   ```
2. Accédez au dossier du projet :
   ```sh
   cd task_manager
   ```
3. Installez les dépendances requises :
   ```sh
   pip install -r requirements.txt
   ```
4. Lancez l'application :
   ```sh
   python src/main.py
   ```

## Générer un Exécutable

Pour créer un exécutable, utilisez **PyInstaller** :

1. Installez PyInstaller :
   ```sh
   pip install pyinstaller
   ```
2. Générez l'exécutable :
   ```sh
   pyinstaller --onefile --windowed --add-data "src/icon/*;icon" --icon=src/icon/logo.png src/main.py
   ```

L'exécutable sera disponible dans le dossier `dist/`. (Remplacer ; par : si sur linux/MacOS)

## Structure du projet

```
Task_manager/
├─ dist/ (si création d'un exécutable)
│  ├─ tasks.db
│  └─ To Do List.exe
├─ src/
│  ├─ icon/
│  │  ├─ agenda.png
│  │  ├─ kanban.png
│  │  ├─ logo.png
│  │  └─ loupe.png
│  ├─ AgendaDialog.py
│  ├─ database.py
│  ├─ EditTaskDialog.py
│  ├─ KanbanDialog.py
│  ├─ main.py
│  ├─ ProgressionBar.py
│  ├─ TaskDetailsDialog.py
│  ├─ TaskManager.py
│  ├─ ui.py
│  └─ utils.py
├─ .gitignore
├─ main.spec
├─ readme.md
└─ requirements.txt

```

## Contribution

Les contributions sont les bienvenues ! Vous pouvez proposer des améliorations via des *pull requests* ou signaler des problèmes via les *issues*.
