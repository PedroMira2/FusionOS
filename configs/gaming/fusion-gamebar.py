#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FusionOS - Game Bar & Overlay de Performance (Super + G)
Barra flutuante para monitoramento de FPS, temperatura, VRAM e controle de jogos.
"""

import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QColor

class FusionGameBar(QWidget):
    def __init__(self):
        super().__init__()
        self.old_pos = QPoint()

        self.setWindowTitle("FusionOS Game Bar")
        self.setFixedSize(760, 80)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1500)

    def init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)

        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #0D0F1AE6;
                border: 1px solid #2E3452;
                border-radius: 20px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 200))
        container.setGraphicsEffect(shadow)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(18)

        # Logo / Tag
        lbl_brand = QLabel("🎮 FUSION GAME")
        lbl_brand.setStyleSheet("font-weight: bold; color: #5B8BFF; font-size: 13px;")
        layout.addWidget(lbl_brand)

        # Separador
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("color: #2E3452;")
        layout.addWidget(sep1)

        # Métricas de Hardware
        self.lbl_cpu = QLabel("CPU: --%")
        self.lbl_cpu.setStyleSheet("color: #E8ECF5; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.lbl_cpu)

        self.lbl_ram = QLabel("RAM: --%")
        self.lbl_ram.setStyleSheet("color: #E8ECF5; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.lbl_ram)

        self.lbl_gpu = QLabel("GPU: Pronto")
        self.lbl_gpu.setStyleSheet("color: #10B981; font-size: 12px; font-weight: bold;")
        layout.addWidget(self.lbl_gpu)

        layout.addStretch()

        # Botão Gravar Clipe
        btn_clip = QPushButton("⏺ Gravar Clipe")
        btn_clip.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clip.setStyleSheet("""
            QPushButton {
                background-color: #1F243D;
                border: 1px solid #3F476C;
                border-radius: 10px;
                color: #E8ECF5;
                font-weight: bold;
                padding: 6px 14px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #FF6B7A;
                border-color: #FF6B7A;
                color: white;
            }
        """)
        btn_clip.clicked.connect(self.record_clip)
        layout.addWidget(btn_clip)

        # Botão GameMode
        self.btn_gm = QPushButton("⚡ GameMode")
        self.btn_gm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_gm.setStyleSheet("""
            QPushButton {
                background-color: #5B8BFF;
                border: none;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                padding: 6px 14px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4A7AEE;
            }
        """)
        self.btn_gm.clicked.connect(self.toggle_gamemode)
        layout.addWidget(self.btn_gm)

        # Botão Fechar
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(24, 24)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #1A1D2B;
                border: 1px solid #2E3452;
                border-radius: 12px;
                color: #9CA3AF;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #FF6B7A;
                color: white;
            }
        """)
        btn_close.clicked.connect(self.close)
        layout.addWidget(btn_close)

        root.addWidget(container)

    def update_stats(self):
        try:
            with open("/proc/loadavg", "r") as f:
                load = f.read().split()[0]
                self.lbl_cpu.setText(f"CPU: {load}")

            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
                total = int(lines[0].split()[1])
                avail = int(lines[2].split()[1])
                used_pct = round(((total - avail) / total) * 100)
                self.lbl_ram.setText(f"RAM: {used_pct}%")
        except Exception:
            pass

    def record_clip(self):
        clip_script = "/usr/local/bin/fusion-clip-record"
        if os.path.exists(clip_script):
            subprocess.Popen(["bash", clip_script])
        self.close()

    def toggle_gamemode(self):
        subprocess.Popen(["fusion-power-mode", "performance"])
        self.btn_gm.setText("✔ Ativo")
        self.btn_gm.setStyleSheet("background-color: #10B981; color: white; border-radius: 10px; padding: 6px 14px;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if not self.old_pos.isNull():
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = QPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    bar = FusionGameBar()
    bar.show()
    sys.exit(app.exec())
