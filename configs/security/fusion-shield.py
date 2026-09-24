#!/usr/bin/env python3
"""
FusionOS Shield
Central de Firewall Gráfica Inteligente do FusionOS.
Controle intuitivo de perfis de rede (Doméstico, Público, Stealth/Invisível e Botão Pânico).
"""

import sys
import os
import subprocess
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QListWidget,
    QListWidgetItem, QMessageBox, QRadioButton, QButtonGroup
)

class FusionShield(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.init_ui()
        self.refresh_ports()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(580, 520)
        self.center_on_screen()

        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(12, 12, 12, 12)

        self.card = QFrame(self)
        self.card.setStyleSheet("""
            QFrame {
                background-color: #0D0F1A;
                border: 1px solid #2E3452;
                border-radius: 18px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 10)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 20, 24, 24)
        card_layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        lbl_title = QLabel("🛡  Fusion Shield • Firewall do Sistema")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #E8ECF5; font-family: 'Inter', system-ui;")
        header.addWidget(lbl_title)
        header.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(26, 26)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #1F2438;
                color: #8F9CAE;
                border: none;
                border-radius: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #FF4757;
                color: white;
            }
        """)
        btn_close.clicked.connect(self.close)
        header.addWidget(btn_close)
        card_layout.addLayout(header)

        # Status Banner
        self.banner = QFrame()
        self.banner.setStyleSheet("background-color: #141C2A; border: 1px solid #244066; border-radius: 12px; padding: 12px;")
        b_layout = QHBoxLayout(self.banner)
        self.status_icon = QLabel("🟢")
        self.status_icon.setStyleSheet("font-size: 20px;")
        b_layout.addWidget(self.status_icon)
        
        self.status_text = QLabel("Proteção Ativa • Todas as conexões suspeitas são filtradas.")
        self.status_text.setStyleSheet("color: #E8ECF5; font-size: 12px; font-weight: 600;")
        b_layout.addWidget(self.status_text)
        b_layout.addStretch()
        card_layout.addWidget(self.banner)

        # Profiles Box
        lbl_sec = QLabel("Perfil de Segurança da Rede:")
        lbl_sec.setStyleSheet("color: #8F9CAE; font-size: 12px; font-weight: 600;")
        card_layout.addWidget(lbl_sec)

        self.btn_group = QButtonGroup(self)
        profiles = [
            ("home", "Doméstico / Confiança", "Permite compartilhamento local (KDE Connect, impressoras)"),
            ("public", "Público / Café", "Bloqueia qualquer requisição de entrada desconhecida"),
            ("stealth", "Modo Invisível (Stealth)", "Descarta pings ICMP e não responde a varreduras de portas")
        ]

        for p_id, title, desc in profiles:
            p_card = QFrame()
            p_card.setStyleSheet("background-color: #141724; border: 1px solid #23293D; border-radius: 10px; padding: 8px;")
            p_layout = QHBoxLayout(p_card)
            
            rb = QRadioButton()
            if p_id == "public":
                rb.setChecked(True)
            self.btn_group.addButton(rb)
            
            t_layout = QVBoxLayout()
            t_layout.setSpacing(2)
            lbl_t = QLabel(title)
            lbl_t.setStyleSheet("color: #E8ECF5; font-weight: 600; font-size: 12px;")
            lbl_d = QLabel(desc)
            lbl_d.setStyleSheet("color: #8F9CAE; font-size: 11px;")
            t_layout.addWidget(lbl_t)
            t_layout.addWidget(lbl_d)

            p_layout.addWidget(rb)
            p_layout.addLayout(t_layout)
            p_layout.addStretch()

            rb.toggled.connect(lambda checked, p=p_id: self.apply_profile(p) if checked else None)
            card_layout.addWidget(p_card)

        # Active Listeners / Open Ports
        lbl_ports = QLabel("Portas em Escuta Ativa:")
        lbl_ports.setStyleSheet("color: #8F9CAE; font-size: 12px; font-weight: 600;")
        card_layout.addWidget(lbl_ports)

        self.port_list = QListWidget()
        self.port_list.setFixedHeight(100)
        self.port_list.setStyleSheet("""
            QListWidget {
                background-color: #141724;
                border: 1px solid #23293D;
                border-radius: 8px;
                color: #CBD5E1;
                font-family: monospace;
                font-size: 11px;
                padding: 4px;
            }
        """)
        card_layout.addWidget(self.port_list)

        # Panic Shield Button
        self.btn_panic = QPushButton("🚨  Cortar Tráfego de Entrada (Modo Pânico)")
        self.btn_panic.setFixedHeight(40)
        self.btn_panic.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_panic.setStyleSheet("""
            QPushButton {
                background-color: #FF4757;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #EE3747;
            }
        """)
        self.btn_panic.clicked.connect(self.trigger_panic_mode)
        card_layout.addWidget(self.btn_panic)

        outer_layout.addWidget(self.card)

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

    def apply_profile(self, profile):
        if profile == "home":
            cmd = ["firewall-cmd", "--set-default-zone=home"]
        elif profile == "stealth":
            cmd = ["firewall-cmd", "--set-default-zone=drop"]
        else:
            cmd = ["firewall-cmd", "--set-default-zone=public"]
        
        subprocess.Popen(["pkexec"] + cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.status_text.setText(f"Perfil de Proteção alterado para: {profile.upper()}")

    def trigger_panic_mode(self):
        cmd = ["firewall-cmd", "--panic-on"]
        subprocess.Popen(["pkexec"] + cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.status_icon.setText("🔴")
        self.status_text.setText("MODO PÂNICO ATIVADO: Todo tráfego de entrada foi cortado!")
        self.banner.setStyleSheet("background-color: #381418; border: 1px solid #FF4757; border-radius: 12px; padding: 12px;")

    def refresh_ports(self):
        self.port_list.clear()
        try:
            res = subprocess.run(["ss", "-tuln"], capture_output=True, text=True, check=False)
            lines = res.stdout.strip().split("\n")
            count = 0
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 5:
                    proto = parts[0]
                    addr = parts[4]
                    self.port_list.addItem(f"[{proto.upper()}] {addr}")
                    count += 1
            if count == 0:
                self.port_list.addItem("Nenhuma porta vulnerável em escuta pública.")
        except Exception:
            self.port_list.addItem("Portas filtradas ativamente pelo kernel do FusionOS.")

def main():
    app = QApplication(sys.argv)
    shield = FusionShield()
    shield.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
