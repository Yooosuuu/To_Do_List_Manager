from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtCore import pyqtProperty, Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient, QFont

class SmoothProgressBar(QProgressBar):
    def __init__(self, parent=None, zoom=1.0):
        super().__init__(parent)
        self._animated_value = 0.0  # Valeur flottante pour l'animation
        self.setTextVisible(True)
        self.zoom = zoom  # Zoom factor from taskmanager

    def getAnimatedValue(self):
        return self._animated_value

    def setAnimatedValue(self, value):
        self._animated_value = value
        self.update()  # Forcer le redessin
        
    def set_zoom(self, zoom):
        self.zoom = zoom
        self.update()

    animatedValue = pyqtProperty(float, fget=getAnimatedValue, fset=setAnimatedValue)

    def paintEvent(self, event):
        # Obtenir le rectangle de la barre
        rect = QRectF(self.rect())  # Convertir en QRectF pour éviter d'autres erreurs

        # Configurer le painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dessiner le fond (barre vide)
        background_brush = QBrush(QColor(255, 255, 255, 77))  # Blanc semi-transparent
        pen = QPen(QColor(0, 0, 0, 77))
        pen.setWidth(int(3 * self.zoom))  # Adjust pen width based on zoom
        painter.setPen(pen)
        painter.setBrush(background_brush)
        painter.drawRoundedRect(rect, self.zoom, self.zoom)

        # Calculer la largeur de progression
        progress_fraction = self._animated_value / self.maximum() if self.maximum() > 0 else 0
        progress_width = int(rect.width() * progress_fraction)
        progress_rect = QRectF(rect.x(), rect.y(), progress_width, rect.height())

        # Appliquer un dégradé de couleur
        gradient = QLinearGradient(QPointF(rect.left(), rect.top()), QPointF(rect.right(), rect.top()))
        gradient.setColorAt(0, QColor(76, 175, 80))  # Vert foncé
        gradient.setColorAt(1, QColor(129, 199, 132))  # Vert clair
        progress_brush = QBrush(gradient)

        # Dessiner la barre de progression
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(progress_brush)
        painter.drawRoundedRect(progress_rect, self.zoom, self.zoom)

        # ✅ Ajouter le texte de progression au centre
        painter.setPen(Qt.GlobalColor.black)
        painter.setFont(QFont("Arial", int(self.zoom*0.75), QFont.Weight.Bold))  # Adjust font size based on zoom

        text = f"{int(self._animated_value)}% fait"
        text_rect = rect.toRect()  # Convertir QRectF en QRect pour drawText
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
