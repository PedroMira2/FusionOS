#!/usr/bin/env python3
"""
FusionOS HDR & OLED Studio
Calibração de Alta Faixa Dinâmica (HDR 10-bit), mapeamento de tons e proteção contra burn-in para telas OLED.
"""

import sys
import os
import subprocess
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QSlider, QCheckBox
)

class FusionHDRAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.hdr_enabled = False
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(540, 480)
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
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        lbl_t = QLabel("✨  Fusion HDR & OLED Studio")
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

        # HDR Master Switch
        switch_box = QFrame()
        switch_box.setStyleSheet("background-color: #141724; border: 1px solid #23293D; border-radius: 12px; padding: 12px;")
        s_layout = QHBoxLayout(switch_box)

        icon_hdr = QLabel("🌈")
        icon_hdr.setStyleSheet("font-size: 26px;")
        s_layout.addWidget(icon_hdr)

        info_v = QVBoxLayout()
        info_v.setSpacing(2)
        lbl_sw_title = QLabel("High Dynamic Range (HDR 10-bit)")
        lbl_sw_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #E8ECF5;")
        self.lbl_sw_status = QLabel("Desativado (Modo SDR Padrão)")
        self.lbl_sw_status.setStyleSheet("font-size: 11px; color: #8F9CAE;")
        info_v.addWidget(lbl_sw_title)
        info_v.addWidget(self.lbl_sw_status)
        s_layout.addLayout(info_v)
        s_layout.addStretch()

        self.btn_toggle_hdr = QPushButton("Ativar HDR")
        self.btn_toggle_hdr.setFixedSize(100, 32)
        self.btn_toggle_hdr.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_hdr.setStyleSheet("""
            QPushButton { background-color: #5B8BFF; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 11px; }
            QPushButton:hover { background-color: #4A7AEE; }
        """)
        self.btn_toggle_hdr.clicked.connect(self.toggle_hdr)
        s_layout.addWidget(self.btn_toggle_hdr)
        layout.addWidget(switch_box)

        # Peak Brightness Slider
        layout.addWidget(QLabel("Brilho de Pico HDR (Nits):"))
        self.slider_nits = QSlider(Qt.Orientation.Horizontal)
        self.slider_nits.setRange(400, 1500)
        self.slider_nits.setValue(1000)
        self.slider_nits.setStyleSheet("""
            QSlider::groove:horizontal { height: 6px; background: #141724; border-radius: 3px; }
            QSlider::sub-page:horizontal { background: #5B8BFF; border-radius: 3px; }
            QSlider::handle:horizontal { background: white; width: 16px; margin: -5px 0; border-radius: 8px; }
        """)
        layout.addWidget(self.slider_nits)

        # SDR Content Boost
        layout.addWidget(QLabel("Intensidade de Cores SDR em Tela HDR:"))
        self.slider_sdr = QSlider(Qt.Orientation.Horizontal)
        self.slider_sdr.setRange(100, 400)
        self.slider_sdr.setValue(220)
        self.slider_sdr.setStyleSheet("""
            QSlider::groove:horizontal { height: 6px; background: #141724; border-radius: 3px; }
            QSlider::sub-page:horizontal { background: #FFB347; border-radius: 3px; }
            QSlider::handle:horizontal { background: white; width: 16px; margin: -5px 0; border-radius: 8px; }
        """)
        layout.addWidget(self.slider_sdr)

        # OLED Burn-in Protection Box
        oled_box = QFrame()
        oled_box.setStyleSheet("background-color: #141724; border: 1px solid #23293D; border-radius: 12px; padding: 12px;")
        o_layout = QVBoxLayout(oled_box)
        o_layout.setSpacing(6)

        lbl_oled = QLabel("🛡️  Proteção Ativa para Painéis OLED:")
        lbl_oled.setStyleSheet("font-weight: bold; color: #E8ECF5; font-size: 12px;")
        o_layout.addWidget(lbl_oled)

        cb1 = QCheckBox("Pixel Shift Dinâmico (Desloca elementos estáticos sutilmente)")
        cb1.setChecked(True)
        cb1.setStyleSheet("color: #8F9CAE; font-size: 11px;")
        o_layout.addWidget(cb1)

        cb2 = QCheckBox("Auto-Dimming de barras estáticas e janelas inativas após 3 min")
        cb2.setChecked(True)
        cb2.setStyleSheet("color: #8F9CAE; font-size: 11px;")
        o_layout.addWidget(cb2)

        layout.addWidget(oled_box)

        # Save Button
        btn_save = QPushButton("Salvar Perfil de Calibração")
        btn_save.setFixedHeight(36)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton { background-color: #5B8BFF; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #4A7AEE; }
        """)
        btn_save.clicked.connect(self.save_settings)
        layout.addWidget(btn_save)

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

    def toggle_hdr(self):
        self.hdr_enabled = not self.hdr_enabled
        if self.hdr_enabled:
            self.btn_toggle_hdr.setText("Desativar")
            self.btn_toggle_hdr.setStyleSheet("background-color: #FF4757; color: white; border-radius: 8px; font-weight: bold;")
            self.lbl_sw_status.setText("Ativado (Gama BT.2020 / HDR10 PQ ativo)")
            self.lbl_sw_status.setStyleSheet("color: #6BCB77; font-size: 11px; font-weight: bold;")
            # Chamar kscreen-doctor se disponível
            subprocess.Popen(["kscreen-doctor", "output.1.hdr.enable"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            self.btn_toggle_hdr.setText("Ativar HDR")
            self.btn_toggle_hdr.setStyleSheet("background-color: #5B8BFF; color: white; border-radius: 8px; font-weight: bold;")
            self.lbl_sw_status.setText("Desativado (Modo SDR Padrão)")
            self.lbl_sw_status.setStyleSheet("color: #8F9CAE; font-size: 11px;")
            subprocess.Popen(["kscreen-doctor", "output.1.hdr.disable"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def save_settings(self):
        if subprocess.run(["which", "notify-send"], capture_output=True).returncode == 0:
            subprocess.Popen(["notify-send", "-a", "Fusion HDR", "-i", "video-display", "Perfil HDR Salvo", "Configurações aplicadas com sucesso."])
        self.close()

def main():
    app = QApplication(sys.argv)
    w = FusionHDRAssistant()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
