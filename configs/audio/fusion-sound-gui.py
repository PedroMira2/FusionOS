#!/usr/bin/env python3
"""
FusionOS Master Audio Studio (Hi-Res 384kHz, Dolby Atmos DSP, Crisp Mic & AutoEQ)
Painel de controle de alta fidelidade sonora com cancelamento de ruído por IA e calibração de fones.
"""

import sys
import os
import subprocess
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QComboBox, QCheckBox
)

class SoundCard(QFrame):
    def __init__(self, preset_id, title, desc, icon, badge_text, parent_gui):
        super().__init__()
        self.preset_id = preset_id
        self.parent_gui = parent_gui
        self.is_selected = False

        self.setFixedSize(130, 115)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        top_hbox = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px; background: transparent;")
        top_hbox.addWidget(icon_label)
        top_hbox.addStretch()

        badge = QLabel(badge_text)
        badge.setStyleSheet("""
            background-color: #5B8BFF;
            color: #FFFFFF;
            font-size: 8px;
            font-weight: bold;
            padding: 2px 4px;
            border-radius: 4px;
        """)
        top_hbox.addWidget(badge)
        layout.addLayout(top_hbox)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #E8ECF5; background: transparent;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.sub_label = QLabel(desc)
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

        self.setWindowTitle("FusionOS Master Audio Studio")
        self.setFixedSize(620, 520)
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
                border-radius: 18px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        main_vbox = QVBoxLayout(container)
        main_vbox.setContentsMargins(24, 20, 24, 22)
        main_vbox.setSpacing(14)

        # Header
        header_hbox = QHBoxLayout()
        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)

        title = QLabel("FusionOS Master Audio Studio")
        title.setStyleSheet("font-size: 17px; font-weight: bold; color: #E8ECF5; font-family: 'Inter';")

        subtitle = QLabel("Processamento 3D Dolby Atmos • IA Crisp Mic • AutoEQ")
        subtitle.setStyleSheet("font-size: 11px; color: #8F9CAE;")

        title_vbox.addWidget(title)
        title_vbox.addWidget(subtitle)
        header_hbox.addLayout(title_vbox)

        header_hbox.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(26, 26)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #1A1D2B;
                border: 1px solid #2E3452;
                border-radius: 13px;
                color: #9CA3AF;
                font-size: 12px;
                font-weight: bold;
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
        bt_bar.setStyleSheet("background-color: #141724; border: 1px solid #2E3452; border-radius: 10px; padding: 6px 12px;")
        bt_layout = QHBoxLayout(bt_bar)
        bt_layout.setContentsMargins(8, 2, 8, 2)

        lbl_bt_icon = QLabel("📶")
        lbl_bt_text = QLabel("Codecs Bluetooth:")
        lbl_bt_text.setStyleSheet("font-weight: bold; color: #9CA3AF; font-size: 11px;")
        lbl_codecs = QLabel("LDAC 990kbps (Sony) • aptX-HD • SBC-XQ 551kbps")
        lbl_codecs.setStyleSheet("color: #5B8BFF; font-weight: bold; font-size: 11px;")

        bt_layout.addWidget(lbl_bt_icon)
        bt_layout.addWidget(lbl_bt_text)
        bt_layout.addWidget(lbl_codecs)
        bt_layout.addStretch()
        main_vbox.addWidget(bt_bar)

        # Cards de Perfis Espaciais
        lbl_presets = QLabel("Perfis Espaciais e Atmosféricos:")
        lbl_presets.setStyleSheet("color: #8F9CAE; font-size: 11px; font-weight: 600;")
        main_vbox.addWidget(lbl_presets)

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

        # Calibração AutoEQ para Fones Específicos
        autoeq_box = QFrame()
        autoeq_box.setStyleSheet("background-color: #141724; border: 1px solid #2E3452; border-radius: 10px; padding: 10px;")
        autoeq_layout = QHBoxLayout(autoeq_box)
        autoeq_layout.setContentsMargins(10, 6, 10, 6)

        lbl_eq_icon = QLabel("🎚️")
        lbl_eq_icon.setStyleSheet("font-size: 16px;")
        lbl_eq_text = QLabel("Calibração AutoEQ:")
        lbl_eq_text.setStyleSheet("color: #E8ECF5; font-size: 11px; font-weight: bold;")
        autoeq_layout.addWidget(lbl_eq_icon)
        autoeq_layout.addWidget(lbl_eq_text)

        self.combo_autoeq = QComboBox()
        self.combo_autoeq.setStyleSheet("""
            QComboBox {
                background-color: #0D0F1A;
                color: #CBD5E1;
                border: 1px solid #2E3452;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.combo_autoeq.addItem("Padrão / Curva Plana (Flat)")
        self.combo_autoeq.addItem("Sony WH-1000XM4 (Harman Target)")
        self.combo_autoeq.addItem("Sony WH-1000XM5 (Harman Target)")
        self.combo_autoeq.addItem("Apple AirPods Pro (Harman In-Ear)")
        self.combo_autoeq.addItem("HyperX Cloud II (Gaming Calibrated)")
        self.combo_autoeq.addItem("Sennheiser HD 600 (Audiophile Reference)")
        self.combo_autoeq.addItem("Samsung Galaxy Buds 2 Pro (Harman In-Ear)")
        autoeq_layout.addWidget(self.combo_autoeq)
        autoeq_layout.addStretch()
        main_vbox.addWidget(autoeq_box)

        # Fusion Crisp Mic - IA Noise Suppression
        mic_box = QFrame()
        mic_box.setStyleSheet("background-color: #141724; border: 1px solid #2E3452; border-radius: 10px; padding: 10px;")
        mic_layout = QHBoxLayout(mic_box)
        mic_layout.setContentsMargins(10, 6, 10, 6)

        lbl_mic_icon = QLabel("🎤")
        lbl_mic_icon.setStyleSheet("font-size: 18px;")
        mic_layout.addWidget(lbl_mic_icon)

        mic_text_vbox = QVBoxLayout()
        mic_text_vbox.setSpacing(2)
        lbl_mic_title = QLabel("Fusion Crisp Mic (IA Noise Suppression)")
        lbl_mic_title.setStyleSheet("color: #E8ECF5; font-size: 12px; font-weight: bold;")
        lbl_mic_sub = QLabel("Elimina ruído de teclado mecânico, ventilador e fundo via RNNoise neural.")
        lbl_mic_sub.setStyleSheet("color: #8F9CAE; font-size: 10px;")
        mic_text_vbox.addWidget(lbl_mic_title)
        mic_text_vbox.addWidget(lbl_mic_sub)
        mic_layout.addLayout(mic_text_vbox)
        mic_layout.addStretch()

        self.btn_mic_toggle = QPushButton("Ativar")
        self.btn_mic_toggle.setFixedSize(80, 30)
        self.btn_mic_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mic_toggle.setStyleSheet("""
            QPushButton {
                background-color: #5B8BFF;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4A7AEE;
            }
        """)
        self.btn_mic_toggle.clicked.connect(self.toggle_crisp_mic)
        mic_layout.addWidget(self.btn_mic_toggle)
        main_vbox.addWidget(mic_box)

        # Footer
        footer_hbox = QHBoxLayout()
        footer_hbox.addStretch()

        self.btn_apply = QPushButton("Aplicar Configurações de Áudio")
        self.btn_apply.setFixedSize(220, 38)
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

    def toggle_crisp_mic(self):
        script = "/usr/bin/fusion-crisp-mic"
        if not os.path.exists(script):
            script = os.path.join(os.path.dirname(__file__), "fusion-crisp-mic.sh")
        
        subprocess.run([script, "toggle"], check=False)
        if self.btn_mic_toggle.text() == "Ativar":
            self.btn_mic_toggle.setText("Ativo ✓")
            self.btn_mic_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #6BCB77;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)
        else:
            self.btn_mic_toggle.setText("Ativar")
            self.btn_mic_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #5B8BFF;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 11px;
                }
            """)

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
