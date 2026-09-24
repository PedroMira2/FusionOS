#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FusionOS - System Cleaner & Disk Optimizer GUI
Interface moderna em PyQt6 para limpeza de disco e otimização do sistema com 1 clique.
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

class CleanThread(QThread):
    finished_signal = pyqtSignal(str)

    def run(self):
        cmd = "/usr/local/bin/fusion-cleaner"
        if not os.path.exists(cmd):
            candidate = os.path.join(os.path.dirname(__file__), "fusion-cleaner.sh")
            if os.path.exists(candidate):
                cmd = candidate

        try:
            res = subprocess.run(["bash", cmd, "--cli"], capture_output=True, text=True)
            output = res.stdout
            msg = "Sistema otimizado com sucesso!"
            for line in output.splitlines():
                if "espaco recuperados" in line:
                    msg = line.replace("[SUCESSO]", "").strip()
            self.finished_signal.emit(msg)
        except Exception as e:
            self.finished_signal.emit(f"Erro: {str(e)}")

class FusionCleanerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.old_pos = QPoint()

        self.setWindowTitle("Fusion Cleaner")
        self.setFixedSize(560, 410)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)

        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            QWidget#container {
                background-color: #0D0F1A;
                border: 1px solid #2E3452;
                border-radius: 16px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 6)
        container.setGraphicsEffect(shadow)

        main_vbox = QVBoxLayout(container)
        main_vbox.setContentsMargins(26, 20, 26, 22)
        main_vbox.setSpacing(14)

        # Header
        header_hbox = QHBoxLayout()
        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)

        title = QLabel("Fusion Cleaner & Otimizador")
        title.setStyleSheet("font-size: 19px; font-weight: bold; color: #E8ECF5;")

        subtitle = QLabel("Recupere espaço no SSD e acelere o sistema com 1 clique")
        subtitle.setStyleSheet("font-size: 12px; color: #9CA3AF;")

        title_vbox.addWidget(title)
        title_vbox.addWidget(subtitle)
        header_hbox.addLayout(title_vbox)

        header_hbox.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(28, 28)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #1A1D2B;
                border: 1px solid #2E3452;
                border-radius: 14px;
                color: #9CA3AF;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #FF6B7A;
                color: white;
                border-color: #FF6B7A;
            }
        """)
        btn_close.clicked.connect(self.close)
        header_hbox.addWidget(btn_close)

        main_vbox.addLayout(header_hbox)

        # Itens a serem limpos
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

        def make_item(icon, name, detail):
            h = QHBoxLayout()
            lbl_i = QLabel(icon)
            lbl_i.setStyleSheet("font-size: 18px;")
            lbl_n = QLabel(name)
            lbl_n.setStyleSheet("font-weight: bold; color: #E8ECF5; font-size: 12px;")
            lbl_d = QLabel(detail)
            lbl_d.setStyleSheet("color: #9CA3AF; font-size: 11px;")
            h.addWidget(lbl_i)
            h.addWidget(lbl_n)
            h.addStretch()
            h.addWidget(lbl_d)
            return h

        c_layout.addLayout(make_item("📦", "Runtimes Flatpak Órfãos", "Bibliotecas antigas não usadas"))
        c_layout.addLayout(make_item("💾", "Cache de Pacotes DNF", "Instaladores temporários"))
        c_layout.addLayout(make_item("📜", "Logs Antigos do Sistema", "Compactação para 100MB"))
        c_layout.addLayout(make_item("🖼️", "Caches e Miniaturas", "Arquivos temporários de imagens"))

        main_vbox.addWidget(card)

        # Progresso e Status
        self.lbl_status = QLabel("Pronto para otimizar o sistema.")
        self.lbl_status.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        main_vbox.addWidget(self.lbl_status)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 0)
        self.progress.setStyleSheet("QProgressBar { border-radius: 4px; height: 6px; }")
        main_vbox.addWidget(self.progress)

        # Footer com Botao
        footer_hbox = QHBoxLayout()
        footer_hbox.addStretch()

        self.btn_clean = QPushButton("Iniciar Limpeza & Otimização")
        self.btn_clean.setFixedSize(220, 40)
        self.btn_clean.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clean.setStyleSheet("""
            QPushButton {
                background-color: #5B8BFF;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4A7AEE;
            }
        """)
        self.btn_clean.clicked.connect(self.start_clean)
        footer_hbox.addWidget(self.btn_clean)

        main_vbox.addLayout(footer_hbox)
        root_layout.addWidget(container)

    def start_clean(self):
        self.btn_clean.setEnabled(False)
        self.btn_clean.setText("Otimizando...")
        self.progress.setVisible(True)
        self.lbl_status.setText("Limpando caches e removendo pacotes órfãos...")

        self.thread = CleanThread()
        self.thread.finished_signal.connect(self.on_clean_done)
        self.thread.start()

    def on_clean_done(self, msg):
        self.progress.setVisible(False)
        self.lbl_status.setText(f"✔ {msg}")
        self.lbl_status.setStyleSheet("color: #10B981; font-weight: bold; font-size: 12px;")
        self.btn_clean.setText("Limpeza Concluída")
        self.btn_clean.setStyleSheet("background-color: #10B981; color: white; border-radius: 8px;")

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
    win = FusionCleanerGUI()
    win.show()
    sys.exit(app.exec())
