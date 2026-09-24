#!/usr/bin/env python3
"""
FusionOS Software Hub
Loja de Aplicativos Exclusiva e Curada do FusionOS.
Instalação rápida e moderna de aplicativos Flatpak e RPM com categorização e busca fluida.
"""

import sys
import os
import subprocess
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QLineEdit,
    QScrollArea, QGridLayout, QProgressBar
)

CATALOG = [
    # Jogos
    {"id": "com.valvesoftware.Steam", "name": "Steam", "cat": "Jogos", "icon": "🎮", "desc": "Plataforma líder mundial de jogos para PC"},
    {"id": "com.heroicgameslauncher.hgl", "name": "Heroic Games", "cat": "Jogos", "icon": "⚡", "desc": "Launcher nativo para Epic Games e GOG no Linux"},
    {"id": "net.lutris.Lutris", "name": "Lutris", "cat": "Jogos", "icon": "🕹️", "desc": "Preservação e gerenciador de jogos de todas as eras"},
    {"id": "org.prismlauncher.PrismLauncher", "name": "Prism Launcher", "cat": "Jogos", "icon": "⛏️", "desc": "Launcher ultra-rápido para Minecraft com mods"},
    
    # Desenvolvimento
    {"id": "com.visualstudio.code", "name": "VS Code", "cat": "Desenvolvimento", "icon": "💻", "desc": "Editor de código fonte moderno e extensível"},
    {"id": "org.sublimetext.three", "name": "Sublime Text", "cat": "Desenvolvimento", "icon": "📝", "desc": "Editor de texto veloz para desenvolvedores"},
    {"id": "com.getpostman.Postman", "name": "Postman", "cat": "Desenvolvimento", "icon": "🚀", "desc": "Plataforma completa para desenvolvimento de APIs"},
    {"id": "io.dbeaver.DBeaverCommunity", "name": "DBeaver", "cat": "Desenvolvimento", "icon": "🗄️", "desc": "Gerenciador universal de bancos de dados SQL/NoSQL"},

    # Criatividade
    {"id": "org.blender.Blender", "name": "Blender 3D", "cat": "Criatividade", "icon": "🎨", "desc": "Suíte profissional de modelagem 3D, animação e render"},
    {"id": "org.gimp.GIMP", "name": "GIMP", "cat": "Criatividade", "icon": "🖼️", "desc": "Manipulação e edição profissional de imagens"},
    {"id": "com.obsproject.Studio", "name": "OBS Studio", "cat": "Criatividade", "icon": "📹", "desc": "Gravação de tela e transmissão ao vivo de alto nível"},
    {"id": "org.kde.kdenlive", "name": "Kdenlive", "cat": "Criatividade", "icon": "🎬", "desc": "Editor de vídeo multipista não linear e poderoso"},

    # Produtividade & Comunicação
    {"id": "com.discordapp.Discord", "name": "Discord", "cat": "Produtividade", "icon": "💬", "desc": "Comunicação por voz, vídeo e texto para comunidades"},
    {"id": "org.telegram.desktop", "name": "Telegram", "cat": "Produtividade", "icon": "✈️", "desc": "Mensageiro instantâneo seguro e veloz"},
    {"id": "com.spotify.Client", "name": "Spotify", "cat": "Multimídia", "icon": "🎵", "desc": "Milhões de músicas e podcasts em streaming"},
    {"id": "org.videolan.VLC", "name": "VLC Media Player", "cat": "Multimídia", "icon": "▶️", "desc": "Reprodutor universal de áudio e vídeo de alta performance"}
]

class InstallWorker(QThread):
    done_signal = pyqtSignal(bool, str)

    def __init__(self, app_id, action="install"):
        super().__init__()
        self.app_id = app_id
        self.action = action

    def run(self):
        cmd = ["flatpak", self.action, "-y", "flathub", self.app_id] if self.action == "install" else ["flatpak", "uninstall", "-y", self.app_id]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        self.done_signal.emit(res.returncode == 0, self.app_id)

class AppItemCard(QFrame):
    def __init__(self, app_data, parent_hub):
        super().__init__()
        self.app_data = app_data
        self.parent_hub = parent_hub
        self.is_installed = self.check_installed()

        self.setStyleSheet("""
            QFrame {
                background-color: #141724;
                border: 1px solid #23293D;
                border-radius: 14px;
                padding: 10px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setSpacing(12)

        icon_lbl = QLabel(app_data["icon"])
        icon_lbl.setStyleSheet("font-size: 30px;")
        layout.addWidget(icon_lbl)

        info_v = QVBoxLayout()
        info_v.setSpacing(2)
        lbl_name = QLabel(app_data["name"])
        lbl_name.setStyleSheet("font-size: 13px; font-weight: bold; color: #E8ECF5; font-family: 'Inter';")
        lbl_desc = QLabel(app_data["desc"])
        lbl_desc.setStyleSheet("font-size: 11px; color: #8F9CAE;")
        lbl_desc.setWordWrap(True)
        info_v.addWidget(lbl_name)
        info_v.addWidget(lbl_desc)
        layout.addLayout(info_v)
        layout.addStretch()

        self.btn_act = QPushButton("Abrir" if self.is_installed else "Instalar")
        self.btn_act.setFixedSize(86, 32)
        self.btn_act.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_btn_style()
        self.btn_act.clicked.connect(self.handle_action)
        layout.addWidget(self.btn_act)

    def check_installed(self):
        try:
            res = subprocess.run(["flatpak", "info", self.app_data["id"]], capture_output=True, check=False)
            return res.returncode == 0
        except Exception:
            return False

    def update_btn_style(self):
        if self.is_installed:
            self.btn_act.setStyleSheet("background-color: #1F2642; color: #5B8BFF; border: 1px solid #5B8BFF; border-radius: 8px; font-weight: bold; font-size: 11px;")
        else:
            self.btn_act.setStyleSheet("background-color: #5B8BFF; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 11px;")

    def handle_action(self):
        if self.is_installed:
            subprocess.Popen(["flatpak", "run", self.app_data["id"]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            self.btn_act.setEnabled(False)
            self.btn_act.setText("Baixando...")
            self.worker = InstallWorker(self.app_data["id"], "install")
            self.worker.done_signal.connect(self.on_installed)
            self.worker.start()

    def on_installed(self, success, app_id):
        self.is_installed = success
        self.btn_act.setEnabled(True)
        self.btn_act.setText("Abrir" if success else "Instalar")
        self.update_btn_style()

class FusionSoftwareHub(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.current_cat = "Todos"
        self.cards = []
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(860, 620)
        self.center_on_screen()

        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        card = QFrame(self)
        card.setStyleSheet("""
            QFrame {
                background-color: #0D0F1A;
                border: 1px solid #2E3452;
                border-radius: 20px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 180))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        lbl_t = QLabel("🛍️  Fusion Software Hub • Loja de Aplicativos")
        lbl_t.setStyleSheet("font-size: 16px; font-weight: bold; color: #E8ECF5; font-family: 'Inter';")
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

        # Search Bar
        search_box = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar aplicativos, jogos, utilitários...")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #141724;
                color: #FFFFFF;
                border: 1px solid #2E3452;
                border-radius: 10px;
                padding-left: 14px;
                font-size: 12px;
            }
            QLineEdit:focus { border-color: #5B8BFF; }
        """)
        self.search_input.textChanged.connect(self.filter_apps)
        search_box.addWidget(self.search_input)
        layout.addLayout(search_box)

        # Category pills
        cat_box = QHBoxLayout()
        cat_box.setSpacing(8)
        self.cat_buttons = {}
        for cat in ["Todos", "Jogos", "Desenvolvimento", "Criatividade", "Produtividade", "Multimídia"]:
            btn = QPushButton(cat)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda ch, c=cat: self.select_category(c))
            self.cat_buttons[cat] = btn
            cat_box.addWidget(btn)
        cat_box.addStretch()
        layout.addLayout(cat_box)
        self.update_cat_buttons()

        # Scroll area with apps
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)

        for app_data in CATALOG:
            c = AppItemCard(app_data, self)
            self.cards.append((app_data, c))
            self.scroll_layout.addWidget(c)
        self.scroll_layout.addStretch()

        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)

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

    def select_category(self, cat):
        self.current_cat = cat
        self.update_cat_buttons()
        self.filter_apps()

    def update_cat_buttons(self):
        for c, b in self.cat_buttons.items():
            if c == self.current_cat:
                b.setStyleSheet("background-color: #5B8BFF; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 11px; padding: 0 12px;")
            else:
                b.setStyleSheet("background-color: #141724; color: #8F9CAE; border: 1px solid #23293D; border-radius: 8px; font-size: 11px; padding: 0 12px;")

    def filter_apps(self):
        query = self.search_input.text().lower().strip()
        for app_data, card in self.cards:
            match_cat = (self.current_cat == "Todos") or (app_data["cat"] == self.current_cat)
            match_query = (query in app_data["name"].lower()) or (query in app_data["desc"].lower())
            card.setVisible(match_cat and match_query)

def main():
    app = QApplication(sys.argv)
    hub = FusionSoftwareHub()
    hub.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
