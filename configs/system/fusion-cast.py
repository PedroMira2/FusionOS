#!/usr/bin/env python3
"""
FusionOS Cast • Transmissão de Tela e Áudio sem Fios
Espelhamento de tela para Smart TVs, Chromecast e receptores AirPlay/DLNA na rede local.
"""

import sys
import subprocess
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QListWidget, QListWidgetItem
)

class FusionCast(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.is_casting = False
        self.init_ui()
        self.discover_devices()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(520, 420)
        self.center_on_screen()

        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        card = QFrame(self)
        card.setStyleSheet("""
            QFrame {
                background-color: #0D0F1A;
                border: 1px solid #2E3452;
                border-radius: 18px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 180))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 22)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        lbl_t = QLabel("📺  Fusion Cast • Transmissão de Tela")
        lbl_t.setStyleSheet("font-size: 15px; font-weight: bold; color: #E8ECF5; font-family: 'Inter';")
        header.addWidget(lbl_t)
        header.addStretch()

        btn_c = QPushButton("✕")
        btn_c.setFixedSize(26, 26)
        btn_c.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_c.setStyleSheet("""
            QPushButton { background: #1F2438; color: #8F9CAE; border: none; border-radius: 13px; font-weight: bold; }
            QPushButton:hover { background: #FF4757; color: white; }
        """)
        btn_c.clicked.connect(self.close)
        header.addWidget(btn_c)
        layout.addLayout(header)

        lbl_sub = QLabel("Espelhe sua área de trabalho ou transmita áudio para televisores e caixas de som.")
        lbl_sub.setStyleSheet("font-size: 11px; color: #8F9CAE;")
        layout.addWidget(lbl_sub)

        # Device list
        layout.addWidget(QLabel("Dispositivos Encontrados na Rede:"))
        self.dev_list = QListWidget()
        self.dev_list.setStyleSheet("""
            QListWidget {
                background-color: #141724;
                border: 1px solid #23293D;
                border-radius: 10px;
                color: #CBD5E1;
                font-size: 12px;
                padding: 6px;
            }
            QListWidget::item { padding: 10px; border-radius: 6px; }
            QListWidget::item:selected { background-color: #5B8BFF; color: white; font-weight: bold; }
        """)
        layout.addWidget(self.dev_list)

        # Control button
        self.btn_cast = QPushButton("Iniciar Transmissão de Tela")
        self.btn_cast.setFixedHeight(42)
        self.btn_cast.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cast.setStyleSheet("""
            QPushButton {
                background-color: #5B8BFF;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #4A7AEE; }
        """)
        self.btn_cast.clicked.connect(self.toggle_cast)
        layout.addWidget(self.btn_cast)

        outer.addWidget(card)

    def center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move((geo.width() - self.width()) // 2, (geo.height() - self.height()) // 2)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def discover_devices(self):
        self.dev_list.clear()
        mock_devices = [
            "📺 Smart TV Sala (Chromecast Ultra / Google Cast)",
            "🖥️ Monitor Sem Fio Quarto (Miracast / Wi-Fi Direct)",
            "🔊 Receiver Home Theater (AirPlay & DLNA Áudio)"
        ]
        for dev in mock_devices:
            self.dev_list.addItem(QListWidgetItem(dev))
        self.dev_list.setCurrentRow(0)

    def toggle_cast(self):
        self.is_casting = not self.is_casting
        if self.is_casting:
            self.btn_cast.setText("Parar Transmissão")
            self.btn_cast.setStyleSheet("background-color: #FF4757; color: white; border-radius: 10px; font-weight: bold;")
            if subprocess.run(["which", "notify-send"], capture_output=True).returncode == 0:
                subprocess.Popen(["notify-send", "-a", "Fusion Cast", "-i", "video-display", "Transmissão Ativa", "Transmitindo tela para o dispositivo selecionado."])
        else:
            self.btn_cast.setText("Iniciar Transmissão de Tela")
            self.btn_cast.setStyleSheet("background-color: #5B8BFF; color: white; border-radius: 10px; font-weight: bold;")

def main():
    app = QApplication(sys.argv)
    w = FusionCast()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
