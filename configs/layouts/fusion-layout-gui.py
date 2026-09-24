#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FusionOS - Chameleon Layout Switcher GUI
Interface grafica moderna em PyQt6 para alternar o layout do desktop com 1 clique.
"""

import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QFont

class LayoutCard(QFrame):
    def __init__(self, layout_id, title, subtitle, tag, icon, parent_gui):
        super().__init__()
        self.layout_id = layout_id
        self.parent_gui = parent_gui
        self.is_selected = False

        self.setFixedSize(210, 240)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(10)

        # Tag
        self.tag_label = QLabel(tag)
        self.tag_label.setStyleSheet("""
            background-color: #1E243D;
            color: #5B8BFF;
            font-size: 10px;
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 6px;
        """)
        self.tag_label.setFixedHeight(24)
        layout.addWidget(self.tag_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Icone
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("font-size: 42px; background: transparent;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        # Titulo
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #E8ECF5; background: transparent;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Subtitulo
        self.sub_label = QLabel(subtitle)
        self.sub_label.setStyleSheet("font-size: 11px; color: #9CA3AF; background: transparent;")
        self.sub_label.setWordWrap(True)
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_label)

        layout.addStretch()
        self.update_style()

    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()

    def update_style(self):
        if self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1F2642;
                    border: 2px solid #5B8BFF;
                    border-radius: 14px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #141724;
                    border: 1px solid #2E3452;
                    border-radius: 14px;
                }
                QFrame:hover {
                    background-color: #1A1F33;
                    border: 1px solid #3F476C;
                }
            """)

    def mousePressEvent(self, event):
        self.parent_gui.select_layout(self.layout_id)


class ChameleonSwitcherGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_layout = "macos"
        self.cards = {}
        self.old_pos = QPoint()

        self.setWindowTitle("Chameleon Layout Engine")
        self.setFixedSize(720, 460)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()

    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(15, 15, 15, 15)

        # Container principal com sombra
        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            QWidget#container {
                background-color: #0D0F1A;
                border: 1px solid #2E3452;
                border-radius: 18px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(35)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        main_vbox = QVBoxLayout(container)
        main_vbox.setContentsMargins(28, 20, 28, 24)
        main_vbox.setSpacing(18)

        # Barra Superior / Titulo
        header_hbox = QHBoxLayout()

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(3)

        title = QLabel("Chameleon Layout Engine")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #E8ECF5;")

        subtitle = QLabel("Alterne o visual e a disposição do desktop com apenas um clique")
        subtitle.setStyleSheet("font-size: 13px; color: #9CA3AF;")

        title_vbox.addWidget(title)
        title_vbox.addWidget(subtitle)
        header_hbox.addLayout(title_vbox)

        header_hbox.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(30, 30)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #1A1D2B;
                border: 1px solid #2E3452;
                border-radius: 15px;
                color: #9CA3AF;
                font-size: 14px;
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

        # Area Central: 3 Cartoes
        cards_hbox = QHBoxLayout()
        cards_hbox.setSpacing(16)

        c1 = LayoutCard("macos", "macOS Style", "Barra Superior translúcida e Dock flutuante", "PRODUTIVIDADE", "🍎", self)
        c2 = LayoutCard("win11", "Windows 11", "Barra de tarefas centralizada e menu familiar", "FAMILIAR", "🪟", self)
        c3 = LayoutCard("gamer", "Gamer Mode", "Imersão total com auto-ocultação e foco", "FOCO & JOGOS", "🎮", self)

        self.cards["macos"] = c1
        self.cards["win11"] = c2
        self.cards["gamer"] = c3

        cards_hbox.addWidget(c1)
        cards_hbox.addWidget(c2)
        cards_hbox.addWidget(c3)

        main_vbox.addLayout(cards_hbox)

        # Seleciona o primeiro por padrao
        c1.set_selected(True)

        # Rodape com Botoes de Acao
        footer_hbox = QHBoxLayout()
        footer_hbox.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedSize(110, 40)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #2E3452;
                border-radius: 8px;
                color: #9CA3AF;
                font-weight: 500;
            }
            QPushButton:hover {
                color: #E8ECF5;
                border-color: #3F476C;
            }
        """)
        btn_cancel.clicked.connect(self.close)
        footer_hbox.addWidget(btn_cancel)

        self.btn_apply = QPushButton("Aplicar Layout")
        self.btn_apply.setFixedSize(140, 40)
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #5B8BFF;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4A7AEE;
            }
            QPushButton:pressed {
                background-color: #3A60D9;
            }
        """)
        self.btn_apply.clicked.connect(self.apply_selected_layout)
        footer_hbox.addWidget(self.btn_apply)

        main_vbox.addLayout(footer_hbox)
        root_layout.addWidget(container)

    def select_layout(self, layout_id):
        self.selected_layout = layout_id
        for lid, card in self.cards.items():
            card.set_selected(lid == layout_id)

    def apply_selected_layout(self):
        self.btn_apply.setText("Aplicando...")
        self.btn_apply.setEnabled(False)
        QApplication.processEvents()

        # Determina o executavel do switch-layout
        target = self.selected_layout
        cmd_path = "/usr/local/bin/fusion-switch-layout"
        if not os.path.exists(cmd_path):
            local_candidate = os.path.join(os.path.dirname(__file__), "../../scripts/fusion-switch-layout.sh")
            if os.path.exists(local_candidate):
                cmd_path = os.path.abspath(local_candidate)

        try:
            subprocess.Popen(["bash", cmd_path, target])
        except Exception as e:
            print(f"Erro ao alternar layout: {e}", file=sys.stderr)

        self.close()

    # Arrastar janela pelo mouse
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
    window = ChameleonSwitcherGUI()
    window.show()
    sys.exit(app.exec())
