#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FusionOS - Master Audio & Dolby 3D Control Center
Interface gráfica para controle de áudio espacial, presets de som e Bluetooth Hi-Res.
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

class SoundCard(QFrame):
    def __init__(self, preset_id, title, subtitle, icon, tag, parent_gui):
        super().__init__()
        self.preset_id = preset_id
        self.parent_gui = parent_gui
        self.is_selected = False

        self.setFixedSize(115, 175)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(6)

        # Tag
        self.tag_label = QLabel(tag)
        self.tag_label.setStyleSheet("""
            background-color: #1E243D;
            color: #5B8BFF;
            font-size: 8px;
            font-weight: bold;
            padding: 2px 4px;
            border-radius: 4px;
        """)
        self.tag_label.setFixedHeight(18)
        layout.addWidget(self.tag_label, alignment=Qt.AlignmentFlag.AlignLeft)

        # Icone
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("font-size: 28px; background: transparent;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        # Titulo
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #E8ECF5; background: transparent;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        # Subtitulo
        self.sub_label = QLabel(subtitle)
        self.sub_label.setStyleSheet("font-size: 9px; color: #9CA3AF; background: transparent;")
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
                    border-radius: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #141724;
                    border: 1px solid #2E3452;
                    border-radius: 10px;
                }
                QFrame:hover {
                    background-color: #1A1F33;
                    border: 1px solid #3F476C;
                }
            """)

    def mousePressEvent(self, event):
        self.parent_gui.select_preset(self.preset_id)


class FusionSoundGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_preset = "FusionOS-Dolby-Spatial"
        self.cards = {}
        self.old_pos = QPoint()

        self.setWindowTitle("FusionOS Master Audio")
        self.setFixedSize(580, 410)
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

        title = QLabel("FusionOS Master Audio (Hi-Res & 3D)")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #E8ECF5;")

        subtitle = QLabel("Processamento espacial e codecs Bluetooth destravados")
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

        # Barra de Status do Bluetooth Hi-Res
        bt_bar = QFrame()
        bt_bar.setStyleSheet("""
            QFrame {
                background-color: #141724;
                border: 1px solid #2E3452;
                border-radius: 10px;
                padding: 8px 12px;
            }
        """)
        bt_layout = QHBoxLayout(bt_bar)
        bt_layout.setContentsMargins(8, 4, 8, 4)

        lbl_bt_icon = QLabel("📶")
        lbl_bt_icon.setStyleSheet("font-size: 16px;")
        lbl_bt_text = QLabel("Codecs Bluetooth Ativos:")
        lbl_bt_text.setStyleSheet("font-weight: bold; color: #9CA3AF; font-size: 11px;")
        lbl_codecs = QLabel("LDAC 990kbps (Sony) • aptX-HD • SBC-XQ 551kbps")
        lbl_codecs.setStyleSheet("color: #5B8BFF; font-weight: bold; font-size: 11px;")

        bt_layout.addWidget(lbl_bt_icon)
        bt_layout.addWidget(lbl_bt_text)
        bt_layout.addWidget(lbl_codecs)
        bt_layout.addStretch()

        main_vbox.addWidget(bt_bar)

        # Cards de Perfis
        cards_hbox = QHBoxLayout()
        cards_hbox.setSpacing(10)

        c1 = SoundCard("FusionOS-Dolby-Spatial", "Dolby 3D", "Surround e agudos", "🎧", "ATMOS 3D", self)
        c2 = SoundCard("FusionOS-Super-Bass", "Super Bass", "Subgraves profundos", "🔊", "GRAVES", self)
        c3 = SoundCard("FusionOS-Cinema-3D", "Cinema", "Vozes e imersão", "🎬", "CINEMA", self)
        c4 = SoundCard("direct", "Puro / Estúdio", "Fidelidade direta", "🎵", "DIRECT", self)

        self.cards["FusionOS-Dolby-Spatial"] = c1
        self.cards["FusionOS-Super-Bass"] = c2
        self.cards["FusionOS-Cinema-3D"] = c3
        self.cards["direct"] = c4

        cards_hbox.addWidget(c1)
        cards_hbox.addWidget(c2)
        cards_hbox.addWidget(c3)
        cards_hbox.addWidget(c4)

        main_vbox.addLayout(cards_hbox)
        c1.set_selected(True)

        # Footer
        footer_hbox = QHBoxLayout()
        footer_hbox.addStretch()

        self.btn_apply = QPushButton("Ativar Perfil de Áudio")
        self.btn_apply.setFixedSize(160, 38)
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
        self.btn_apply.clicked.connect(self.apply_preset)
        footer_hbox.addWidget(self.btn_apply)

        main_vbox.addLayout(footer_hbox)
        root_layout.addWidget(container)

    def select_preset(self, preset_id):
        self.selected_preset = preset_id
        for pid, card in self.cards.items():
            card.set_selected(pid == preset_id)

    def apply_preset(self):
        if self.selected_preset == "direct":
            subprocess.run(["easyeffects", "-b"], capture_output=True)
            msg = "Modo Direto de Estúdio Ativado (Sem filtros)"
        else:
            subprocess.run(["easyeffects", "-l", self.selected_preset], capture_output=True)
            msg = f"Perfil {self.selected_preset} Ativado com Sucesso!"

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            subprocess.Popen(["notify-send", "-a", "FusionOS Audio", "-i", "audio-speakers", "Áudio Hi-Res", msg])

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
    win = FusionSoundGUI()
    win.show()
    sys.exit(app.exec())
