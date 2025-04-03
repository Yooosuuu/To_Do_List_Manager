import sys
import os

def resource_path(relative_path):
    """ Récupère le chemin absolu pour les fichiers embarqués avec PyInstaller """
    if getattr(sys, 'frozen', False):  # Vérifie si l'app est en mode compilé
        base_path = sys._MEIPASS  # PyInstaller stocke les fichiers ici
    else:
        base_path = os.path.abspath(".")  # Mode normal (exécution directe)
    
    return os.path.join(base_path, relative_path)
