#!/usr/bin/env python3
"""
FusionOS Cloud Connect GUI
Interface gráfica para sincronizar e montar serviços de nuvem (Google Drive, OneDrive, Nextcloud)
diretamente como pastas locais no Dolphin.
"""

import sys
import os
import subprocess
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QGridLayout
)

class CloudCard(QFrame):
    def __init__(self, provider_id, icon, name, parent_gui):
        super().__init__()
        self.provider_id = provider_id
        self.parent_gui = parent_gui
        self.is_connected = False

        self.setStyleSheet("""
            QFrame {
                background-color: #141724;
                border: 1px solid #23293D;
                border-radius: 14px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        top_h = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 26px;")
        top_h.addWidget(lbl_icon)
        top_h.addStretch()

        self.lbl_badge = QLabel("Desconectado")
        self.lbl_badge.setStyleSheet("color: #8F9CAE; font-size: 10px; font-weight: bold;")
        top_h.addWidget(self.lbl_badge)
        layout.addLayout(top_h)

        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-size: 13px; font-weight: bold; color: #E8ECF5;")
        layout.addWidget(lbl_name)

        btn_box = QHBoxLayout()
        self.btn_toggle = QPushButton("Conectar")
        self.btn_toggle.setFixedHeight(30)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #5B8BFF;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #4A7AEE; }
        """)
        self.btn_toggle.clicked.connect(self.toggle_mount)
        btn_box.addWidget(self.btn_toggle)

        self.btn_open = QPushButton("📁")
        self.btn_open.setFixedSize(30, 30)
        self.btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open.setStyleSheet("""
            QPushButton {
                background-color: #1F2438;
                color: #CBD5E1;
                border: 1px solid #2E3452;
                border-radius: 6px;
            }
            QPushButton:hover { border-color: #5B8BFF; }
        """)
        self.btn_open.clicked.connect(self.open_folder)
        self.btn_open.hide()
        btn_box.addWidget(self.btn_open)

        layout.addLayout(btn_box)

    def toggle_mount(self):
        script = "/usr/bin/fusion-cloud-connect"
        if not os.path.exists(script):
            script = os.path.join(os.path.dirname(__file__), "fusion-cloud-connect.sh")

        if not self.is_connected:
            subprocess.run([script, "mount", self.provider_id], check=False)
            self.is_connected = True
            self.lbl_badge.setText("Conectado ✓")
            self.lbl_badge.setStyleSheet("color: #6BCB77; font-size: 10px; font-weight: bold;")
            self.btn_toggle.setText("Desconectar")
            self.btn_toggle.setStyleSheet("background-color: #242B42; color: #FF6B7A; border-radius: 6px; font-weight: bold; font-size: 11px;")
            self.btn_open.show()
        else:
            subprocess.run([script, "unmount", self.provider_id], check=False)
            self.is_connected = False
            self.lbl_badge.setText("Desconectado")
            self.lbl_badge.setStyleSheet("color: #8F9CAE; font-size: 10px; font-weight: bold;")
            self.btn_toggle.setText("Conectar")
            self.btn_toggle.setStyleSheet("background-color: #5B8BFF; color: white; border-radius: 6px; font-weight: bold; font-size: 11px;")
            self.btn_open.hide()

    def open_folder(self):
        p = os.path.expanduser(f"~/Nuvem/{self.provider_id}")
        subprocess.Popen(["dolphin", p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

class FusionCloudGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(560, 420)
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
        lbl_t = QLabel("☁️  Fusion Cloud Connect")
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

        lbl_desc = QLabel("Monte seus discos virtuais como pastas nativas no Dolphin com cache inteligente.")
        lbl_desc.setStyleSheet("color: #8F9CAE; font-size: 11px;")
        layout.addWidget(lbl_desc)

        # 2x2 Grid of Providers
        grid = QGridLayout()
        grid.setSpacing(12)

        p1 = CloudCard("gdrive", "🔵", "Google Drive", self)
        p2 = CloudCard("onedrive", "🟦", "Microsoft OneDrive", self)
        p3 = CloudCard("nextcloud", "🔷", "Nextcloud / OwnCloud", self)
        p4 = CloudCard("dropbox", "📦", "Dropbox", self)

        grid.addWidget(p1, 0, 0)
        grid.addWidget(p2, 0, 1)
        grid.addWidget(p3, 1, 0)
        grid.addWidget(p4, 1, 1)

        layout.addLayout(grid)
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

def main():
    app = QApplication(sys.argv)
    w = FusionCloudGUI()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
