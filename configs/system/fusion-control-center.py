#!/usr/bin/env python3
"""
FusionOS Control Center
Centro de Controle Unificado estilo macOS / iOS para FusionOS.
Controle rápido de Wi-Fi, Bluetooth, Modo Foco, Luz Noturna, Volume Hi-Res, Brilho e Perfis de Energia.
"""

import sys
import os
import subprocess
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QSlider, QFrame, QGraphicsDropShadowEffect,
    QProgressBar, QScrollArea
)

class ToggleButton(QPushButton):
    def __init__(self, icon_str, title, subtitle="", parent=None):
        super().__init__(parent)
        self.is_active = False
        self.icon_str = icon_str
        self.title = title
        self.subtitle = subtitle
        self.setCheckable(True)
        self.setFixedHeight(64)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()

    def set_active(self, active: bool):
        self.is_active = active
        self.setChecked(active)
        self.update_style()

    def update_style(self):
        bg = "#5B8BFF" if self.is_active else "#1A1F33"
        txt_main = "#FFFFFF" if self.is_active else "#E8ECF5"
        txt_sub = "#D0DEFF" if self.is_active else "#8F9CAE"
        border = "#7CA3FF" if self.is_active else "#2E3452"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 14px;
                text-align: left;
                padding-left: 14px;
            }}
            QPushButton:hover {{
                border-color: #5B8BFF;
            }}
        """)
        self.setText(f"{self.icon_str}  {self.title}\n    {self.subtitle}")
        self.setFont(QFont("Inter", 10, QFont.Weight.Medium))

class FusionControlCenter(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.refresh_states()

        # Timer para atualizar métricas
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(3000)

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(390, 620)
        self.position_top_right()

        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(12, 12, 12, 12)

        self.panel = QFrame(self)
        self.panel.setStyleSheet("""
            QFrame {
                background-color: #0D0F1A;
                border: 1px solid #2E3452;
                border-radius: 20px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 10)
        self.panel.setGraphicsEffect(shadow)

        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(18, 18, 18, 18)
        panel_layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        lbl_title = QLabel("Central de Controle")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #E8ECF5; font-family: 'Inter', system-ui;")
        header.addWidget(lbl_title)
        header.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(26, 26)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #1A1F33;
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
        panel_layout.addLayout(header)

        # Grid de Controles Rápidos (Wi-Fi, Bluetooth, Modo Foco, Luz Noturna)
        grid = QGridLayout()
        grid.setSpacing(10)

        self.btn_wifi = ToggleButton("📶", "Wi-Fi", "Conectado")
        self.btn_wifi.clicked.connect(self.toggle_wifi)
        grid.addWidget(self.btn_wifi, 0, 0)

        self.btn_bt = ToggleButton("⚡", "Bluetooth", "Ativo")
        self.btn_bt.clicked.connect(self.toggle_bluetooth)
        grid.addWidget(self.btn_bt, 0, 1)

        self.btn_focus = ToggleButton("🌙", "Modo Foco", "Desativado")
        self.btn_focus.clicked.connect(self.toggle_focus)
        grid.addWidget(self.btn_focus, 1, 0)

        self.btn_night = ToggleButton("👁", "Luz Noturna", "Ativa (3800K)")
        self.btn_night.clicked.connect(self.toggle_night_color)
        grid.addWidget(self.btn_night, 1, 1)

        panel_layout.addLayout(grid)

        # Card de Volume de Áudio Hi-Res
        vol_card = QFrame()
        vol_card.setStyleSheet("background-color: #141724; border: 1px solid #23293D; border-radius: 14px; padding: 10px;")
        vol_layout = QVBoxLayout(vol_card)
        vol_layout.setSpacing(8)

        vol_header = QHBoxLayout()
        lbl_vol = QLabel("🔊  Volume de Áudio (PipeWire Hi-Res)")
        lbl_vol.setStyleSheet("color: #E8ECF5; font-size: 12px; font-weight: 600; font-family: 'Inter';")
        self.lbl_vol_val = QLabel("70%")
        self.lbl_vol_val.setStyleSheet("color: #5B8BFF; font-size: 12px; font-weight: 700;")
        vol_header.addWidget(lbl_vol)
        vol_header.addStretch()
        vol_header.addWidget(self.lbl_vol_val)
        vol_layout.addLayout(vol_header)

        self.slider_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_vol.setRange(0, 100)
        self.slider_vol.setValue(70)
        self.slider_vol.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #1F2538;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #5B8BFF;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                width: 18px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 9px;
            }
        """)
        self.slider_vol.valueChanged.connect(self.on_volume_changed)
        vol_layout.addWidget(self.slider_vol)
        panel_layout.addWidget(vol_card)

        # Card de Brilho da Tela
        bri_card = QFrame()
        bri_card.setStyleSheet("background-color: #141724; border: 1px solid #23293D; border-radius: 14px; padding: 10px;")
        bri_layout = QVBoxLayout(bri_card)
        bri_layout.setSpacing(8)

        bri_header = QHBoxLayout()
        lbl_bri = QLabel("🔆  Brilho da Tela")
        lbl_bri.setStyleSheet("color: #E8ECF5; font-size: 12px; font-weight: 600; font-family: 'Inter';")
        self.lbl_bri_val = QLabel("85%")
        self.lbl_bri_val.setStyleSheet("color: #FFB347; font-size: 12px; font-weight: 700;")
        bri_header.addWidget(lbl_bri)
        bri_header.addStretch()
        bri_header.addWidget(self.lbl_bri_val)
        bri_layout.addLayout(bri_header)

        self.slider_bri = QSlider(Qt.Orientation.Horizontal)
        self.slider_bri.setRange(10, 100)
        self.slider_bri.setValue(85)
        self.slider_bri.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #1F2538;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: #FFB347;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #FFFFFF;
                width: 18px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 9px;
            }
        """)
        self.slider_bri.valueChanged.connect(self.on_brightness_changed)
        bri_layout.addWidget(self.slider_bri)
        panel_layout.addWidget(bri_card)

        # Perfis de Energia (Pills)
        pwr_card = QFrame()
        pwr_card.setStyleSheet("background-color: #141724; border: 1px solid #23293D; border-radius: 14px; padding: 10px;")
        pwr_layout = QVBoxLayout(pwr_card)
        pwr_layout.setSpacing(8)
        lbl_pwr = QLabel("⚡  Perfil de Desempenho")
        lbl_pwr.setStyleSheet("color: #E8ECF5; font-size: 12px; font-weight: 600;")
        pwr_layout.addWidget(lbl_pwr)

        pwr_buttons = QHBoxLayout()
        pwr_buttons.setSpacing(4)
        self.btn_eco = QPushButton("Eco")
        self.btn_multi = QPushButton("Multitarefa")
        self.btn_perf = QPushButton("Máximo")
        self.btn_game = QPushButton("Jogos")
        for b, mode in [(self.btn_eco, "powersave"), (self.btn_multi, "multitask"), (self.btn_perf, "performance"), (self.btn_game, "gaming")]:
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setFixedHeight(28)
            b.clicked.connect(lambda ch, m=mode: self.set_power_mode(m))
            pwr_buttons.addWidget(b)
        pwr_layout.addLayout(pwr_buttons)
        panel_layout.addWidget(pwr_card)
        self.set_power_ui("multitask")

        # Atalhos de Aplicativos do Sistema
        apps_layout = QHBoxLayout()
        apps_layout.setSpacing(8)
        quick_apps = [
            ("🎮", "Game Bar", "/usr/bin/fusion-gamebar"),
            ("🎵", "Áudio", "/usr/bin/fusion-sound-control"),
            ("🛡", "Segurança", "/usr/bin/fusion-shield"),
            ("🧹", "Limpeza", "/usr/bin/fusion-cleaner-gui")
        ]
        for icon, name, cmd in quick_apps:
            btn = QPushButton(f"{icon}\n{name}")
            btn.setFixedHeight(54)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: #141724;
                    color: #CBD5E1;
                    border: 1px solid #23293D;
                    border-radius: 10px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #1F2538;
                    border-color: #5B8BFF;
                    color: #FFFFFF;
                }
            """)
            btn.clicked.connect(lambda ch, c=cmd: self.launch_app(c))
            apps_layout.addWidget(btn)
        panel_layout.addLayout(apps_layout)

        # Métricas de Sistema (CPU / RAM)
        metrics_layout = QHBoxLayout()
        self.lbl_cpu = QLabel("CPU: 3%")
        self.lbl_ram = QLabel("RAM: 1.8 / 16 GB")
        self.lbl_cpu.setStyleSheet("color: #6BCB77; font-size: 11px; font-weight: 600;")
        self.lbl_ram.setStyleSheet("color: #5B8BFF; font-size: 11px; font-weight: 600;")
        metrics_layout.addWidget(self.lbl_cpu)
        metrics_layout.addStretch()
        metrics_layout.addWidget(self.lbl_ram)
        panel_layout.addLayout(metrics_layout)

        outer_layout.addWidget(self.panel)

    def position_top_right(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            # Margem de 16px do canto superior direito
            self.move(geo.width() - self.width() - 16, geo.top() + 40)

    def refresh_states(self):
        self.btn_wifi.set_active(True)
        self.btn_bt.set_active(True)
        self.btn_focus.set_active(False)
        self.btn_night.set_active(True)

    def toggle_wifi(self):
        new_state = not self.btn_wifi.is_active
        self.btn_wifi.set_active(new_state)
        self.btn_wifi.subtitle = "Conectado" if new_state else "Desativado"
        self.btn_wifi.update_style()
        cmd = ["nmcli", "radio", "wifi", "on" if new_state else "off"]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def toggle_bluetooth(self):
        new_state = not self.btn_bt.is_active
        self.btn_bt.set_active(new_state)
        self.btn_bt.subtitle = "Ativo" if new_state else "Desativado"
        self.btn_bt.update_style()
        cmd = ["bluetoothctl", "power", "on" if new_state else "off"]
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def toggle_focus(self):
        new_state = not self.btn_focus.is_active
        self.btn_focus.set_active(new_state)
        self.btn_focus.subtitle = "Ativado (Não Perturbe)" if new_state else "Desativado"
        self.btn_focus.update_style()
        subprocess.Popen(["/usr/bin/fusion-focus-mode", "toggle"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def toggle_night_color(self):
        new_state = not self.btn_night.is_active
        self.btn_night.set_active(new_state)
        self.btn_night.subtitle = "Ativa (3800K)" if new_state else "Desativada"
        self.btn_night.update_style()

    def on_volume_changed(self, val):
        self.lbl_vol_val.setText(f"{val}%")
        # wpctl set-volume @DEFAULT_AUDIO_SINK@ 0.70
        subprocess.Popen(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{val/100:.2f}"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def on_brightness_changed(self, val):
        self.lbl_bri_val.setText(f"{val}%")
        subprocess.Popen(["brightnessctl", "set", f"{val}%"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def set_power_mode(self, mode):
        self.set_power_ui(mode)
        subprocess.Popen(["/usr/bin/fusion-power-mode", mode], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def set_power_ui(self, active_mode):
        style_active = "background: #5B8BFF; color: white; border-radius: 6px; font-weight: bold; font-size: 10px; border: none;"
        style_inactive = "background: #1F2538; color: #8F9CAE; border-radius: 6px; font-size: 10px; border: 1px solid #2A314A;"
        self.btn_eco.setStyleSheet(style_active if active_mode == "powersave" else style_inactive)
        self.btn_multi.setStyleSheet(style_active if active_mode == "multitask" else style_inactive)
        self.btn_perf.setStyleSheet(style_active if active_mode == "performance" else style_inactive)
        self.btn_game.setStyleSheet(style_active if active_mode == "gaming" else style_inactive)

    def launch_app(self, cmd):
        subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.close()

    def update_metrics(self):
        try:
            # Memory
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            mem_total = 0
            mem_avail = 0
            for l in lines:
                if l.startswith('MemTotal:'):
                    mem_total = int(l.split()[1])
                elif l.startswith('MemAvailable:'):
                    mem_avail = int(l.split()[1])
            if mem_total > 0:
                used_gb = (mem_total - mem_avail) / 1024 / 1024
                tot_gb = mem_total / 1024 / 1024
                self.lbl_ram.setText(f"RAM: {used_gb:.1f} / {tot_gb:.0f} GB")
        except Exception:
            pass

def main():
    app = QApplication(sys.argv)
    ctrl = FusionControlCenter()
    ctrl.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
