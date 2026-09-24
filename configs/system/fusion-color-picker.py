#!/usr/bin/env python3
"""
FusionOS Color Picker • Seletor e Conta-Gotas Global
Conta-gotas flutuante de alta precisão com visualização HEX, RGB e cópia com um clique.
"""

import sys
import subprocess
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QCursor, QColor, QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGraphicsDropShadowEffect
)

class FusionColorPicker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(220, 90)

        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.card = QFrame(self)
        self.card.setStyleSheet("""
            QFrame {
                background-color: #0D0F1A;
                border: 1px solid #2E3452;
                border-radius: 12px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.card.setGraphicsEffect(shadow)

        c_layout = QHBoxLayout(self.card)
        c_layout.setContentsMargins(12, 10, 12, 10)
        c_layout.setSpacing(12)

        # Swatch preview box
        self.swatch = QFrame()
        self.swatch.setFixedSize(36, 36)
        self.swatch.setStyleSheet("background-color: #5B8BFF; border-radius: 8px; border: 1px solid #ffffff33;")
        c_layout.addWidget(self.swatch)

        # Text info
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.lbl_hex = QLabel("#5B8BFF")
        self.lbl_hex.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF; font-family: monospace;")

        self.lbl_rgb = QLabel("rgb(91, 139, 255)")
        self.lbl_rgb.setStyleSheet("font-size: 10px; color: #8F9CAE; font-family: monospace;")

        text_layout.addWidget(self.lbl_hex)
        text_layout.addWidget(self.lbl_rgb)
        c_layout.addLayout(text_layout)

        layout.addWidget(self.card)

        # Cursor follow timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_color)
        self.timer.start(30)

        self.current_hex = "#5B8BFF"

    def update_color(self):
        pos = QCursor.pos()
        # Offset badge slightly from cursor so it doesn't block pixel
        self.move(pos.x() + 18, pos.y() + 18)

        screen = QApplication.primaryScreen()
        if screen:
            pixmap = screen.grabWindow(0, pos.x(), pos.y(), 1, 1)
            img = pixmap.toImage()
            if not img.isNull():
                col = QColor(img.pixel(0, 0))
                self.current_hex = col.name().upper()
                self.lbl_hex.setText(self.current_hex)
                self.lbl_rgb.setText(f"rgb({col.red()}, {col.green()}, {col.blue()})")
                self.swatch.setStyleSheet(f"background-color: {self.current_hex}; border-radius: 8px; border: 1px solid #ffffff44;")

    def mousePressEvent(self, event):
        # Click copies to clipboard and closes
        QApplication.clipboard().setText(self.current_hex)
        if subprocess.run(["which", "notify-send"], capture_output=True).returncode == 0:
            subprocess.Popen([
                "notify-send", "-a", "Color Picker", "-i", "color-picker",
                "Cor Copiada!", f"{self.current_hex} copiado para a área de transferência."
            ])
        self.close()

def main():
    app = QApplication(sys.argv)
    picker = FusionColorPicker()
    picker.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
