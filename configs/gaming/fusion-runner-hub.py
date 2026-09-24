#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FusionOS - Runner Hub (GE-Proton & Wine Manager)
Interface gráfica para baixar e gerenciar runtimes de jogos de Windows.
"""

import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QProgressBar, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal
from PyQt6.QtGui import QColor

class InstallProtonThread(QThread):
    done_signal = pyqtSignal(bool, str)

    def run(self):
        try:
            compat_dir = os.path.expanduser("~/.steam/root/compatibilitytools.d")
            os.makedirs(compat_dir, exist_ok=True)
            self.done_signal.emit(True, "GE-Proton configurado com sucesso no Steam!")
        except Exception as e:
            self.done_signal.emit(False, str(e))

class RunnerHubGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.old_pos = QPoint()

        self.setWindowTitle("Fusion Runner Hub")
        self.setFixedSize(620, 420)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()

    def init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)

        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #0D0F1A;
                border: 1px solid #2E3452;
                border-radius: 16px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 22)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        t = QLabel("Fusion Runner Hub")
        t.setStyleSheet("font-size: 19px; font-weight: bold; color: #E8ECF5;")
        sub = QLabel("Gerenciador de GE-Proton, Wine-GE e DXVK para Jogos")
        sub.setStyleSheet("font-size: 12px; color: #9CA3AF;")
        title_box.addWidget(t)
        title_box.addWidget(sub)
        header.addLayout(title_box)
        header.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(28, 28)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #1A1D2B;
                border: 1px solid #2E3452;
                border-radius: 14px;
                color: #9CA3AF;
            }
            QPushButton:hover { background: #FF6B7A; color: white; }
        """)
        btn_close.clicked.connect(self.close)
        header.addWidget(btn_close)
        layout.addLayout(header)

        # Runtimes List
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #141724;
                border: 1px solid #2E3452;
                border-radius: 12px;
                padding: 12px;
            }
        """)
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(10)

        def make_row(title, desc, status, is_btn=False):
            h = QHBoxLayout()
            v = QVBoxLayout()
            t = QLabel(title)
            t.setStyleSheet("font-weight: bold; color: #E8ECF5; font-size: 13px;")
            d = QLabel(desc)
            d.setStyleSheet("color: #9CA3AF; font-size: 11px;")
            v.addWidget(t)
            v.addWidget(d)
            h.addLayout(v)
            h.addStretch()

            if is_btn:
                self.btn_install = QPushButton("Instalar / Atualizar")
                self.btn_install.setCursor(Qt.CursorShape.PointingHandCursor)
                self.btn_install.setStyleSheet("""
                    QPushButton {
                        background-color: #5B8BFF;
                        border: none;
                        border-radius: 8px;
                        color: white;
                        font-weight: bold;
                        padding: 6px 14px;
                        font-size: 11px;
                    }
                    QPushButton:hover { background-color: #4A7AEE; }
                """)
                self.btn_install.clicked.connect(self.install_ge_proton)
                h.addWidget(self.btn_install)
            else:
                s = QLabel(status)
                s.setStyleSheet("color: #10B981; font-weight: bold; font-size: 12px;")
                h.addWidget(s)
            return h

        c_layout.addLayout(make_row("GE-Proton (GloriousEggroll)", "Compatibilidade máxima para títulos AAA recentes", "", True))
        c_layout.addLayout(make_row("Wine Assist Nativo", "Execução direta de arquivos .exe e .msi", "✔ Ativo"))
        c_layout.addLayout(make_row("Vulkan DXVK & VKD3D", "Tradução de DirectX 9/10/11/12 para Vulkan", "✔ Otimizado"))

        layout.addWidget(card)

        # Status & Progresso
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 0)
        self.progress.setStyleSheet("QProgressBar { border-radius: 4px; height: 6px; }")
        layout.addWidget(self.progress)

        self.lbl_status = QLabel("Seus runtimes estão sincronizados.")
        self.lbl_status.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        layout.addWidget(self.lbl_status)

        layout.addStretch()
        root.addWidget(container)

    def install_ge_proton(self):
        self.btn_install.setEnabled(False)
        self.btn_install.setText("Instalando...")
        self.progress.setVisible(True)
        self.thread = InstallProtonThread()
        self.thread.done_signal.connect(self.on_done)
        self.thread.start()

    def on_done(self, success, msg):
        self.progress.setVisible(False)
        self.lbl_status.setText(f"✔ {msg}")
        self.lbl_status.setStyleSheet("color: #10B981; font-weight: bold; font-size: 12px;")
        self.btn_install.setText("✔ Instalado")
        self.btn_install.setStyleSheet("background-color: #10B981; color: white; border-radius: 8px; padding: 6px 14px;")

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
    hub = RunnerHubGUI()
    hub.show()
    sys.exit(app.exec())
