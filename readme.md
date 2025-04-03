# Task Manager

Le **Task Manager** est une application de gestion de tâches développée en Python, utilisant PyQt6 pour l'interface graphique et Pygame pour certains éléments visuels interactifs. Cette application vous aide à organiser vos tâches personnelles ou professionnelles de manière efficace.

## Fonctionnalités

- **Gestion des tâches** : Ajouter, modifier, supprimer et organiser vos tâches.
- **Suivi de l'avancement** : Classement des tâches par statut ("À faire", "En cours", "Terminé").
- **Interface intuitive** : Une interface graphique claire et accessible pour une utilisation quotidienne.
- **Gestion des priorités** : Assigner des priorités aux tâches pour mieux les organiser.

## Prérequis

Avant d'utiliser cette application, assurez-vous d'avoir installé Python ainsi que les bibliothèques suivantes :

- Python 3.x (testé avec Python 3.13)
- PyQt6
- Pygame (si des éléments interactifs sont utilisés)

Installation des dépendances :

```sh
pip install pyqt6 pygame
```

## Installation

1. Clonez ce dépôt :
   ```sh
   git clone https://github.com/ton-username/task-manager.git
   ```
2. Accédez au dossier du projet :
   ```sh
   cd task-manager
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

L'exécutable sera disponible dans le dossier `dist/`.

## Structure du projet

```
task-manager/
│
├── src/                # Code source de l'application
│   ├── main.py         # Point d'entrée du programme
│   ├── taskmanager.py  # Gestionnaire des tâches
│   └── icon/           # Ressources graphiques
│
├── dist/               # Exécutable généré par PyInstaller
├── build/              # Dossier temporaire de compilation
├── requirements.txt    # Dépendances requises
└── README.md           # Documentation
```

## Contribution

Les contributions sont les bienvenues ! Vous pouvez proposer des améliorations via des *pull requests* ou signaler des problèmes via les *issues*.
