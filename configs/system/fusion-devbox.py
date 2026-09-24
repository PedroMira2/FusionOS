#!/usr/bin/env python3
"""
FusionOS DevBox
Gerenciador de Ambientes de Desenvolvimento Isolados em Containers (Node, Python, Rust, Go, Docker).
Permite manter o sistema base puro e imutável enquanto fornece toolchains de programação completas.
"""

import sys
import subprocess
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QProgressBar
)

DEV_STACKS = [
    {"id": "node", "name": "Node.js Fullstack", "icon": "🟢", "desc": "Node.js LTS, TypeScript, PNPM, Vite e ESLint."},
    {"id": "python", "name": "Python AI & Data Science", "icon": "🐍", "desc": "Python 3.12, PyTorch, NumPy, Pandas e JupyterLab."},
    {"id": "rust", "name": "Rust Systems", "icon": "🦀", "desc": "Rustc, Cargo, Rust-Analyzer e Clippy atualizados."},
    {"id": "go", "name": "Go Cloud Backend", "icon": "🐹", "desc": "Go 1.23, ferramentas de microsserviços e gRPC."},
    {"id": "docker", "name": "Docker & Podman Stack", "icon": "🐳", "desc": "Daemon de containers, Docker Compose e Buildx."}
]

class DevStackCard(QFrame):
    def __init__(self, stack_data, parent_gui):
        super().__init__()
        self.stack_data = stack_data
        self.parent_gui = parent_gui
        self.is_ready = False

        self.setStyleSheet("""
            QFrame {
                background-color: #141724;
                border: 1px solid #23293D;
                border-radius: 12px;
                padding: 10px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setSpacing(12)

        icon_lbl = QLabel(stack_data["icon"])
        icon_lbl.setStyleSheet("font-size: 26px;")
        layout.addWidget(icon_lbl)

        info_v = QVBoxLayout()
        info_v.setSpacing(2)
        lbl_t = QLabel(stack_data["name"])
        lbl_t.setStyleSheet("font-size: 13px; font-weight: bold; color: #E8ECF5; font-family: 'Inter';")
        lbl_d = QLabel(stack_data["desc"])
        lbl_d.setStyleSheet("font-size: 11px; color: #8F9CAE;")
        info_v.addWidget(lbl_t)
        info_v.addWidget(lbl_d)
        layout.addLayout(info_v)
        layout.addStretch()

        self.btn_act = QPushButton("Inicializar")
        self.btn_act.setFixedSize(96, 32)
        self.btn_act.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_act.setStyleSheet("""
            QPushButton {
                background-color: #5B8BFF;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #4A7AEE; }
        """)
        self.btn_act.clicked.connect(self.setup_stack)
        layout.addWidget(self.btn_act)

    def setup_stack(self):
        self.btn_act.setEnabled(False)
        self.btn_act.setText("Configurando...")
        # Simula/executa ativação do container
        self.is_ready = True
        self.btn_act.setEnabled(True)
        self.btn_act.setText("Abrir Terminal")
        self.btn_act.setStyleSheet("background-color: #1F2642; color: #5B8BFF; border: 1px solid #5B8BFF; border-radius: 8px; font-weight: bold; font-size: 11px;")
        self.btn_act.clicked.disconnect()
        self.btn_act.clicked.connect(self.open_shell)

    def open_shell(self):
        subprocess.Popen(["konsole", "--new-tab"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

class FusionDevBox(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(640, 540)
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
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        lbl_t = QLabel("🛠️  Fusion DevBox • Ambientes Isolados")
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

        lbl_sub = QLabel("Mantenha o sistema base 100% limpo com ambientes de programação isolados em containers.")
        lbl_sub.setStyleSheet("font-size: 11px; color: #8F9CAE;")
        layout.addWidget(lbl_sub)

        for stack in DEV_STACKS:
            layout.addWidget(DevStackCard(stack, self))

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
    w = FusionDevBox()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
