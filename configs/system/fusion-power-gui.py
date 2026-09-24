#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FusionOS - Power & Performance Profile GUI
Interface moderna em PyQt6 para alternar perfis de energia e desempenho com 1 clique.
"""

import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor

class PowerCard(QFrame):
    def __init__(self, mode_id, title, subtitle, icon, tag, parent_gui):
        super().__init__()
        self.mode_id = mode_id
        self.parent_gui = parent_gui
        self.is_selected = False

        self.setFixedSize(150, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(8)

        # Tag
        self.tag_label = QLabel(tag)
        self.tag_label.setStyleSheet("""
            background-color: #1E243D;
            color: #5B8BFF;
            font-size: 9px;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 4px;
        """)
        self.tag_label.setFixedHeight(20)
        layout.addWidget(self.tag_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Icone
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("font-size: 34px; background: transparent;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        # Titulo
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #E8ECF5; background: transparent;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Subtitulo
        self.sub_label = QLabel(subtitle)
        self.sub_label.setStyleSheet("font-size: 10px; color: #9CA3AF; background: transparent;")
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
                    border-radius: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #141724;
                    border: 1px solid #2E3452;
                    border-radius: 12px;
                }
                QFrame:hover {
                    background-color: #1A1F33;
                    border: 1px solid #3F476C;
                }
            """)

    def mousePressEvent(self, event):
        self.parent_gui.select_mode(self.mode_id)


class FusionPowerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_mode = "balanced"
        self.cards = {}
        self.old_pos = QPoint()

        self.setWindowTitle("FusionOS Power Profiles")
        self.setFixedSize(540, 360)
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
        main_vbox.setContentsMargins(24, 18, 24, 20)
        main_vbox.setSpacing(14)

        # Header
        header_hbox = QHBoxLayout()
        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)

        title = QLabel("Perfis de Desempenho")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #E8ECF5;")

        subtitle = QLabel("Ajuste o comportamento do hardware para seu fluxo")
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

        # Cards
        cards_hbox = QHBoxLayout()
        cards_hbox.setSpacing(12)

        c1 = PowerCard("powersave", "Silencioso", "Economia e bateria máxima", "🍃", "ECO", self)
        c2 = PowerCard("balanced", "Equilibrado", "Desempenho fluido diário", "⚖️", "PADRÃO", self)
        c3 = PowerCard("performance", "Ultra Gamer", "Clock total e GameMode", "🚀", "TURBO", self)

        self.cards["powersave"] = c1
        self.cards["balanced"] = c2
        self.cards["performance"] = c3

        cards_hbox.addWidget(c1)
        cards_hbox.addWidget(c2)
        cards_hbox.addWidget(c3)

        main_vbox.addLayout(cards_hbox)
        c2.set_selected(True)

        # Footer
        footer_hbox = QHBoxLayout()
        footer_hbox.addStretch()

        self.btn_apply = QPushButton("Aplicar Perfil")
        self.btn_apply.setFixedSize(140, 38)
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply.setStyleSheet("""
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
        self.btn_apply.clicked.connect(self.apply_mode)
        footer_hbox.addWidget(self.btn_apply)

        main_vbox.addLayout(footer_hbox)
        root_layout.addWidget(container)

    def select_mode(self, mode_id):
        self.selected_mode = mode_id
        for mid, card in self.cards.items():
            card.set_selected(mid == mode_id)

    def apply_mode(self):
        cmd = "/usr/local/bin/fusion-power-mode"
        if not os.path.exists(cmd):
            candidate = os.path.join(os.path.dirname(__file__), "fusion-power-mode.sh")
            if os.path.exists(candidate):
                cmd = candidate

        try:
            subprocess.Popen(["bash", cmd, self.selected_mode])
        except Exception as e:
            print(f"Erro ao aplicar perfil: {e}", file=sys.stderr)

        self.close()

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
    win = FusionPowerGUI()
    win.show()
    sys.exit(app.exec())
