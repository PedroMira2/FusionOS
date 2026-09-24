#!/usr/bin/env python3
"""
FusionOS App Shield • Flatpak Permission Manager
Gerenciador visual de privacidade e permissões para aplicativos Flatpak no FusionOS.
Permite alternar acesso a Rede, Microfone, Câmera, Disco e Servidor Gráfico.
"""

import sys
import os
import subprocess
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QListWidget,
    QListWidgetItem, QCheckBox, QScrollArea, QMessageBox
)

class AppPermissionCard(QFrame):
    def __init__(self, perm_key, icon_str, title, desc, app_id, parent=None):
        super().__init__(parent)
        self.perm_key = perm_key
        self.app_id = app_id
        
        self.setStyleSheet("""
            QFrame {
                background-color: #141724;
                border: 1px solid #23293D;
                border-radius: 12px;
                padding: 10px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        icon_lbl = QLabel(icon_str)
        icon_lbl.setStyleSheet("font-size: 22px;")
        layout.addWidget(icon_lbl)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #E8ECF5; font-size: 13px; font-weight: 600; font-family: 'Inter';")
        lbl_desc = QLabel(desc)
        lbl_desc.setStyleSheet("color: #8F9CAE; font-size: 11px;")
        info_layout.addWidget(lbl_title)
        info_layout.addWidget(lbl_desc)
        layout.addLayout(info_layout)
        layout.addStretch()

        self.cb = QCheckBox()
        self.cb.setChecked(True)
        self.cb.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb.setStyleSheet("""
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 1px solid #2E3452;
                background-color: #0D0F1A;
            }
            QCheckBox::indicator:checked {
                background-color: #5B8BFF;
                border-color: #5B8BFF;
            }
        """)
        self.cb.toggled.connect(self.on_toggled)
        layout.addWidget(self.cb)

    def on_toggled(self, checked):
        if not self.app_id:
            return
        arg = f"--{'' if checked else 'un'}share={self.perm_key}" if self.perm_key in ['network', 'ipc'] else f"--{'' if checked else 'no-'}socket={self.perm_key}"
        cmd = ["flatpak", "override", "--user", arg, self.app_id]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

class FusionPermissions(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.current_app_id = None
        self.init_ui()
        self.load_installed_apps()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(720, 540)
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
        card_layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        lbl_title = QLabel("🛡  Fusion App Shield • Permissões de Aplicativos")
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

        # Main splitter layout (Left: Apps list, Right: Permissions)
        body = QHBoxLayout()
        body.setSpacing(16)

        # Left list
        left_layout = QVBoxLayout()
        left_layout.setSpacing(6)
        lbl_apps = QLabel("Aplicativos Instalados:")
        lbl_apps.setStyleSheet("color: #8F9CAE; font-size: 12px; font-weight: 600;")
        left_layout.addWidget(lbl_apps)

        self.app_list = QListWidget()
        self.app_list.setFixedWidth(240)
        self.app_list.setStyleSheet("""
            QListWidget {
                background-color: #141724;
                border: 1px solid #23293D;
                border-radius: 10px;
                color: #E8ECF5;
                font-size: 12px;
                padding: 6px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #5B8BFF;
                color: #FFFFFF;
                font-weight: 600;
            }
        """)
        self.app_list.currentRowChanged.connect(self.on_app_selected)
        left_layout.addWidget(self.app_list)
        body.addLayout(left_layout)

        # Right permissions panel
        self.right_panel = QVBoxLayout()
        self.right_panel.setSpacing(10)

        self.lbl_selected_app = QLabel("Selecione um aplicativo para auditar permissões")
        self.lbl_selected_app.setStyleSheet("color: #E8ECF5; font-size: 14px; font-weight: 700;")
        self.right_panel.addWidget(self.lbl_selected_app)

        self.perm_network = AppPermissionCard("network", "🌐", "Acesso à Rede / Internet", "Permite conectar à internet e servidores externos", None)
        self.perm_fs = AppPermissionCard("filesystem=home", "📁", "Acesso aos Arquivos do Usuário", "Permite leitura e gravação na pasta pessoal", None)
        self.perm_audio = AppPermissionCard("pulseaudio", "🎤", "Áudio & Microfone", "Permite tocar sons e gravar áudio via PipeWire", None)
        self.perm_wayland = AppPermissionCard("wayland", "🖥️", "Servidor de Janelas Wayland", "Permite renderizar janelas na tela do usuário", None)

        self.right_panel.addWidget(self.perm_network)
        self.right_panel.addWidget(self.perm_fs)
        self.right_panel.addWidget(self.perm_audio)
        self.right_panel.addWidget(self.perm_wayland)
        self.right_panel.addStretch()

        body.addLayout(self.right_panel)
        card_layout.addLayout(body)

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

    def load_installed_apps(self):
        self.app_list.clear()
        try:
            res = subprocess.run(["flatpak", "list", "--app", "--columns=application,name"],
                                 capture_output=True, text=True, check=False)
            lines = [l.strip() for l in res.stdout.strip().split("\n") if l.strip()]
            for line in lines:
                parts = line.split("\t")
                app_id = parts[0]
                name = parts[1] if len(parts) > 1 else app_id
                item = QListWidgetItem(f"📦 {name}")
                item.setData(Qt.ItemDataRole.UserRole, app_id)
                self.app_list.addItem(item)
        except Exception:
            pass

        if self.app_list.count() == 0:
            mock_apps = [
                ("com.valvesoftware.Steam", "Steam Games"),
                ("com.discordapp.Discord", "Discord"),
                ("com.google.Chrome", "Google Chrome"),
                ("com.spotify.Client", "Spotify"),
                ("com.visualstudio.code", "VS Code")
            ]
            for app_id, name in mock_apps:
                item = QListWidgetItem(f"📦 {name}")
                item.setData(Qt.ItemDataRole.UserRole, app_id)
                self.app_list.addItem(item)

        self.app_list.setCurrentRow(0)

    def on_app_selected(self, row):
        item = self.app_list.item(row)
        if not item:
            return
        app_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_app_id = app_id
        self.lbl_selected_app.setText(f"Permissões: {item.text()}")
        
        self.perm_network.app_id = app_id
        self.perm_fs.app_id = app_id
        self.perm_audio.app_id = app_id
        self.perm_wayland.app_id = app_id

def main():
    app = QApplication(sys.argv)
    shield = FusionPermissions()
    shield.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
