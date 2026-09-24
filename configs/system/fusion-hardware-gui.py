#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FusionOS - Hardware & Driver Assistant GUI
Interface gráfica moderna em PyQt6 para diagnosticar hardware e instalar drivers NVIDIA.
"""

import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QProgressBar, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint, QThread, pyqtSignal
from PyQt6.QtGui import QColor

class DriverInstallThread(QThread):
    finished_signal = pyqtSignal(bool, str)

    def run(self):
        try:
            cmd = ["pkexec", "dnf", "install", "-y", "akmod-nvidia", "xorg-x11-drv-nvidia-cuda"]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                self.finished_signal.emit(True, "Driver NVIDIA instalado com sucesso! Reinicie o sistema.")
            else:
                self.finished_signal.emit(False, f"Falha na instalacao: {res.stderr[:100]}")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class HardwareAssistantGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.old_pos = QPoint()

        self.setWindowTitle("FusionOS Hardware & Drivers")
        self.setFixedSize(620, 430)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()

    def get_hardware_info(self):
        gpu = "Desconhecida"
        cpu = "Processador Generico"
        ram = "Nao identificado"

        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        cpu = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass

        try:
            out = subprocess.check_output("lspci", shell=True, text=True)
            for line in out.splitlines():
                if any(x in line.lower() for x in ["vga", "3d", "display"]):
                    gpu = line.split(":", 2)[-1].strip()
                    break
        except Exception:
            pass

        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemTotal" in line:
                        kb = int(line.split()[1])
                        ram = f"{round(kb / (1024 * 1024), 1)} GB"
                        break
        except Exception:
            pass

        return cpu, gpu, ram

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
        main_vbox.setContentsMargins(26, 20, 26, 22)
        main_vbox.setSpacing(16)

        # Header
        header_hbox = QHBoxLayout()
        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(2)

        title = QLabel("Hardware & Central de Drivers")
        title.setStyleSheet("font-size: 19px; font-weight: bold; color: #E8ECF5;")

        subtitle = QLabel("Diagnóstico automático de placa gráfica e aceleração do sistema")
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

        # Informacoes do Hardware
        cpu_str, gpu_str, ram_str = self.get_hardware_info()

        spec_card = QFrame()
        spec_card.setStyleSheet("""
            QFrame {
                background-color: #141724;
                border: 1px solid #2E3452;
                border-radius: 12px;
                padding: 12px;
            }
        """)
        spec_layout = QVBoxLayout(spec_card)
        spec_layout.setSpacing(8)

        def make_row(icon, label, val):
            h = QHBoxLayout()
            lbl_icon = QLabel(icon)
            lbl_icon.setStyleSheet("font-size: 16px;")
            lbl_name = QLabel(label)
            lbl_name.setStyleSheet("font-weight: bold; color: #9CA3AF; font-size: 12px;")
            lbl_val = QLabel(val)
            lbl_val.setStyleSheet("color: #E8ECF5; font-size: 12px;")
            lbl_val.setWordWrap(True)
            h.addWidget(lbl_icon)
            h.addWidget(lbl_name)
            h.addWidget(lbl_val, 1)
            return h

        spec_layout.addLayout(make_row("🖥️", "Processador:", cpu_str))
        spec_layout.addLayout(make_row("🎮", "Placa de Vídeo:", gpu_str))
        spec_layout.addLayout(make_row("⚡", "Memória RAM:", ram_str))

        main_vbox.addWidget(spec_card)

        # Painel de Status do Driver
        self.driver_card = QFrame()
        self.driver_card.setStyleSheet("""
            QFrame {
                background-color: #1A1F33;
                border: 1px solid #3F476C;
                border-radius: 12px;
                padding: 14px;
            }
        """)
        d_layout = QVBoxLayout(self.driver_card)
        d_layout.setSpacing(6)

        is_nvidia = "nvidia" in gpu_str.lower()
        if is_nvidia:
            status_title = QLabel("⚠️ Placa NVIDIA Detectada - Driver Oficial Recomendado")
            status_title.setStyleSheet("font-weight: bold; color: #FFB347; font-size: 13px;")
            status_desc = QLabel("Para habilitar Ray Tracing, NVENC e CUDA, instale o driver proprietário oficial.")
            status_desc.setStyleSheet("color: #CBD5E1; font-size: 11px;")

            self.btn_install = QPushButton("Instalar Drivers Oficiais NVIDIA")
            self.btn_install.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_install.setStyleSheet("""
                QPushButton {
                    background-color: #10B981;
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            self.btn_install.clicked.connect(self.install_nvidia)

            d_layout.addWidget(status_title)
            d_layout.addWidget(status_desc)
            d_layout.addWidget(self.btn_install, alignment=Qt.AlignmentFlag.AlignLeft)
        else:
            status_title = QLabel("✨ Drivers de Aceleração Gráfica Otimizados")
            status_title.setStyleSheet("font-weight: bold; color: #5B8BFF; font-size: 13px;")
            status_desc = QLabel("O seu hardware está utilizando os drivers modernos Mesa Vulkan (RADV/Iris) com aceleração total ativa.")
            status_desc.setStyleSheet("color: #CBD5E1; font-size: 11px;")
            d_layout.addWidget(status_title)
            d_layout.addWidget(status_desc)

        main_vbox.addWidget(self.driver_card)

        # Progresso
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 0)
        self.progress.setStyleSheet("QProgressBar { border-radius: 4px; height: 6px; }")
        main_vbox.addWidget(self.progress)

        main_vbox.addStretch()
        root_layout.addWidget(container)

    def install_nvidia(self):
        self.btn_install.setEnabled(False)
        self.btn_install.setText("Instalando pacotes via DNF...")
        self.progress.setVisible(True)

        self.thread = DriverInstallThread()
        self.thread.finished_signal.connect(self.on_installed)
        self.thread.start()

    def on_installed(self, success, msg):
        self.progress.setVisible(False)
        if success:
            self.btn_install.setText("✔ Concluído com Sucesso!")
            self.btn_install.setStyleSheet("background-color: #059669; color: white; border-radius: 8px;")
        else:
            self.btn_install.setText("Erro na instalação")
            self.btn_install.setEnabled(True)

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
    win = HardwareAssistantGUI()
    win.show()
    sys.exit(app.exec())
