#!/usr/bin/env python3
"""
FusionOS Vault GUI
Interface gráfica moderna e segura para gerenciar a pasta privada criptografada (Cofre).
"""

import sys
import os
import subprocess
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QGraphicsDropShadowEffect, QMessageBox
)

class FusionVaultGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.vault_script = "/usr/bin/fusion-vault"
        if not os.path.exists(self.vault_script):
            self.vault_script = os.path.join(os.path.dirname(__file__), "fusion-vault.sh")
        
        self.init_ui()
        self.update_state()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(520, 440)
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
        lbl_title = QLabel("Fusion Vault • Cofre Criptografado")
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

        # Status icon & text
        self.icon_lbl = QLabel("🔒")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_lbl.setStyleSheet("font-size: 54px;")
        card_layout.addWidget(self.icon_lbl)

        self.status_title = QLabel("Cofre Bloqueado")
        self.status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #E8ECF5;")
        card_layout.addWidget(self.status_title)

        self.status_desc = QLabel("Seus arquivos confidenciais estão criptografados com AES-256-GCM.")
        self.status_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_desc.setStyleSheet("color: #8F9CAE; font-size: 12px;")
        card_layout.addWidget(self.status_desc)

        # Password input box
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Digite a senha do cofre...")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet("""
            QLineEdit {
                background: #141724;
                color: #FFFFFF;
                border: 1px solid #2E3452;
                border-radius: 10px;
                padding: 10px 14px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #5B8BFF;
            }
        """)
        self.pass_input.returnPressed.connect(self.handle_action)
        card_layout.addWidget(self.pass_input)

        # Action button
        self.btn_action = QPushButton("Desbloquear Cofre")
        self.btn_action.setFixedHeight(44)
        self.btn_action.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_action.setStyleSheet("""
            QPushButton {
                background-color: #5B8BFF;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4A7AEE;
            }
        """)
        self.btn_action.clicked.connect(self.handle_action)
        card_layout.addWidget(self.btn_action)

        # Secondary button (open dolphin or lock)
        self.btn_open_folder = QPushButton("Abrir Pasta ~/Cofre no Dolphin")
        self.btn_open_folder.setFixedHeight(36)
        self.btn_open_folder.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_folder.setStyleSheet("""
            QPushButton {
                background-color: #141724;
                color: #CBD5E1;
                border: 1px solid #2E3452;
                border-radius: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                border-color: #5B8BFF;
                color: white;
            }
        """)
        self.btn_open_folder.clicked.connect(self.open_in_dolphin)
        self.btn_open_folder.hide()
        card_layout.addWidget(self.btn_open_folder)

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

    def get_status(self):
        try:
            res = subprocess.run([self.vault_script, "status"], capture_output=True, text=True, check=False)
            return res.stdout.strip()
        except Exception:
            return "locked"

    def update_state(self):
        st = self.get_status()
        if st == "unlocked":
            self.icon_lbl.setText("🔓")
            self.status_title.setText("Cofre Desbloqueado")
            self.status_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #6BCB77;")
            self.status_desc.setText("Seus arquivos estão acessíveis na pasta ~/Cofre.")
            self.pass_input.hide()
            self.btn_action.setText("Bloquear Cofre Agora")
            self.btn_action.setStyleSheet("""
                QPushButton {
                    background-color: #FF4757;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #EE3747;
                }
            """)
            self.btn_open_folder.show()
        else:
            self.icon_lbl.setText("🔒")
            self.status_title.setText("Cofre Bloqueado")
            self.status_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #E8ECF5;")
            self.status_desc.setText("Seus arquivos confidenciais estão criptografados com AES-256-GCM.")
            self.pass_input.clear()
            self.pass_input.show()
            self.btn_action.setText("Desbloquear Cofre")
            self.btn_action.setStyleSheet("""
                QPushButton {
                    background-color: #5B8BFF;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: 700;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #4A7AEE;
                }
            """)
            self.btn_open_folder.hide()

    def handle_action(self):
        st = self.get_status()
        if st == "unlocked":
            # Lock
            subprocess.run([self.vault_script, "lock"], check=False)
            self.update_state()
        else:
            # Unlock
            pwd = self.pass_input.text().strip()
            if not pwd:
                return
            subprocess.run([self.vault_script, "unlock", pwd], check=False)
            self.update_state()

    def open_in_dolphin(self):
        mount_path = os.path.expanduser("~/Cofre")
        subprocess.Popen(["dolphin", mount_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    app = QApplication(sys.argv)
    vault = FusionVaultGUI()
    vault.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
