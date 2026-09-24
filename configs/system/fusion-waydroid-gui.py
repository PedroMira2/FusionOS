#!/usr/bin/env python3
"""
FusionOS Android Subsystem GUI
Central de controle para executar aplicativos e jogos do Android diretamente no Wayland.
"""

import sys
import os
import subprocess
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QMessageBox
)

class FusionWaydroidGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.init_ui()
        self.update_status()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(520, 390)
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
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        lbl_t = QLabel("🤖  Fusion Android Subsystem")
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

        # Status box
        status_box = QFrame()
        status_box.setStyleSheet("background-color: #141724; border: 1px solid #23293D; border-radius: 12px; padding: 14px;")
        s_layout = QHBoxLayout(status_box)
        
        self.icon_status = QLabel("🟢")
        self.icon_status.setStyleSheet("font-size: 26px;")
        s_layout.addWidget(self.icon_status)

        info_v = QVBoxLayout()
        info_v.setSpacing(2)
        self.lbl_st_title = QLabel("Subsistema Android Pronto")
        self.lbl_st_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #E8ECF5;")
        self.lbl_st_desc = QLabel("Aceleração gráfica Mesa/Vulkan ativa em modo multi-janelas.")
        self.lbl_st_desc.setStyleSheet("font-size: 11px; color: #8F9CAE;")
        info_v.addWidget(self.lbl_st_title)
        info_v.addWidget(self.lbl_st_desc)
        s_layout.addLayout(info_v)
        s_layout.addStretch()
        layout.addWidget(status_box)

        # Action Buttons
        self.btn_toggle = QPushButton("Iniciar Subsistema Android")
        self.btn_toggle.setFixedHeight(42)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setStyleSheet("""
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
        self.btn_toggle.clicked.connect(self.toggle_android)
        layout.addWidget(self.btn_toggle)

        extra_h = QHBoxLayout()
        self.btn_apps = QPushButton("Abrir Gaveta de Apps Android")
        self.btn_apps.setFixedHeight(34)
        self.btn_apps.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apps.setStyleSheet("""
            QPushButton {
                background-color: #141724;
                color: #CBD5E1;
                border: 1px solid #2E3452;
                border-radius: 8px;
                font-size: 11px;
            }
            QPushButton:hover { border-color: #5B8BFF; color: white; }
        """)
        self.btn_apps.clicked.connect(self.open_app_drawer)
        extra_h.addWidget(self.btn_apps)
        layout.addLayout(extra_h)

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

    def update_status(self):
        self.is_running = False
        self.btn_toggle.setText("Iniciar Subsistema Android")

    def toggle_android(self):
        script = "/usr/bin/fusion-waydroid-setup"
        if not os.path.exists(script):
            script = os.path.join(os.path.dirname(__file__), "fusion-waydroid-setup.sh")

        if not self.is_running:
            subprocess.run([script, "start"], check=False)
            self.is_running = True
            self.btn_toggle.setText("Encerrar Android")
            self.btn_toggle.setStyleSheet("background-color: #FF4757; color: white; border-radius: 10px; font-weight: bold;")
        else:
            subprocess.run([script, "stop"], check=False)
            self.is_running = False
            self.btn_toggle.setText("Iniciar Subsistema Android")
            self.btn_toggle.setStyleSheet("background-color: #5B8BFF; color: white; border-radius: 10px; font-weight: bold;")

    def open_app_drawer(self):
        subprocess.Popen(["waydroid", "show-full-ui"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    app = QApplication(sys.argv)
    w = FusionWaydroidGUI()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
