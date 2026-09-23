#!/usr/bin/env python3
import sys
import subprocess
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QStackedWidget, 
                             QGridLayout, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon

class WorkerThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, commands):
        super().__init__()
        self.commands = commands

    def run(self):
        total = len(self.commands)
        for i, cmd in enumerate(self.commands):
            self.log.emit(f"Executando: {cmd}")
            try:
                # Usa sudo para rodar como root silenciosamente, 
                # visto que adicionamos NOPASSWD para o liveuser.
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in process.stdout:
                    self.log.emit(line.strip())
                process.wait()
                if process.returncode != 0:
                    self.finished.emit(False, f"Erro no comando: {cmd}")
                    return
            except Exception as e:
                self.finished.emit(False, str(e))
                return
            
            p = int(((i + 1) / total) * 100)
            self.progress.emit(p)
        self.finished.emit(True, "Todos os processos concluidos com sucesso!")

class FusionWelcome(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bem-vindo ao Fusion OS")
        self.setMinimumSize(850, 550)
        self.resize(900, 600)
        
        # Tema Escuro Premium com cores de alto contraste
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QLabel { color: #f8fafc; font-family: 'Inter', 'Noto Sans', sans-serif; }
            QPushButton {
                background-color: #3b82f6; color: white; border: none;
                border-radius: 8px; padding: 12px 24px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #2563eb; }
            QPushButton[type="secondary"] { background-color: #334155; }
            QPushButton[type="secondary"]:hover { background-color: #475569; }
            QProgressBar {
                border: 2px solid #334155; border-radius: 6px; text-align: center;
                background-color: #0f172a; color: white; font-weight: bold;
            }
            QProgressBar::chunk { background-color: #3b82f6; border-radius: 4px; }
            QToolTip { background-color: #1e293b; color: white; border: 1px solid #334155; }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Header / Stepper (Passos)
        self.header_layout = QHBoxLayout()
        self.step_label = QLabel("Passo 1 de 3 - Boas-vindas")
        self.step_label.setStyleSheet("color: #cbd5e1; font-size: 12px; font-weight: bold;")
        self.header_layout.addWidget(self.step_label)
        self.header_layout.addStretch()
        self.layout.addLayout(self.header_layout)
        
        self.stacked = QStackedWidget()
        self.layout.addWidget(self.stacked)
        
        self.init_welcome_page()
        self.init_apps_page()
        self.init_progress_page()
        self.init_finish_page()

        self.apps_to_install = []

    def update_step(self, step_num, title):
        self.step_label.setText(f"Passo {step_num} de 3 - {title}")

    def init_welcome_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Bem-vindo ao Fusion OS")
        title.setFont(QFont("Inter", 34, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("O sistema de alto desempenho para criadores e gamers.")
        subtitle.setFont(QFont("Inter", 15))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #cbd5e1;") # Melhor contraste
        
        btn_start = QPushButton("Começar Configuração")
        btn_start.setFixedSize(250, 50)
        btn_start.clicked.connect(lambda: [self.stacked.setCurrentIndex(1), self.update_step(2, "Aplicativos")])
        
        l.addStretch()
        l.addWidget(title)
        l.addWidget(subtitle)
        l.addSpacing(40)
        l.addWidget(btn_start, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addStretch()
        self.stacked.addWidget(page)

    def init_apps_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        
        title = QLabel("Aplicativos Essenciais")
        title.setFont(QFont("Inter", 26, QFont.Weight.Bold))
        
        subtitle = QLabel("Selecione os programas que deseja instalar agora:")
        subtitle.setFont(QFont("Inter", 13))
        subtitle.setStyleSheet("color: #cbd5e1;")
        
        grid = QGridLayout()
        grid.setSpacing(15)
        
        self.app_checkboxes = {}
        # Lista com icones padrao do Linux (Freedesktop/Papirus)
        apps = [
            ("Google Chrome", "com.google.Chrome", "Navegador Web", "google-chrome"),
            ("Brave Browser", "com.brave.Browser", "Navegador c/ Adblock", "brave-browser"),
            ("Steam", "com.valvesoftware.Steam", "Plataforma de Jogos", "steam"),
            ("Heroic Games", "com.heroicgameslauncher.hgl", "Jogos Epic/GOG", "heroic"),
            ("Discord", "com.discordapp.Discord", "Chat para Gamers", "discord"),
            ("VLC Media", "org.videolan.VLC", "Reprodutor", "vlc"),
            ("Spotify", "com.spotify.Client", "Streaming", "spotify"),
            ("OBS Studio", "com.obsproject.Studio", "Streaming", "obs")
        ]
        
        row = col = 0
        for name, flatpak_id, desc, icon_name in apps:
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setMinimumSize(220, 85)
            btn.setProperty("type", "secondary")
            
            # Layout interno do botão para suportar título e descrição
            btn_layout = QVBoxLayout(btn)
            btn_layout.setContentsMargins(10, 10, 10, 10)
            
            header_layout = QHBoxLayout()
            icon_label = QLabel()
            icon_label.setPixmap(QIcon.fromTheme(icon_name, QIcon.fromTheme("application-x-executable")).pixmap(24, 24))
            
            name_label = QLabel(name)
            name_label.setFont(QFont("Inter", 12, QFont.Weight.Bold))
            name_label.setStyleSheet("color: white; background: transparent;")
            
            header_layout.addWidget(icon_label)
            header_layout.addWidget(name_label)
            header_layout.addStretch()
            
            desc_label = QLabel(desc)
            desc_label.setFont(QFont("Inter", 10))
            desc_label.setStyleSheet("color: #cbd5e1; background: transparent;")
            
            btn_layout.addLayout(header_layout)
            btn_layout.addWidget(desc_label)
            
            btn.setStyleSheet("""
                QPushButton { background-color: #1e293b; border: 2px solid #334155; text-align: left; }
                QPushButton:checked { background-color: #1e3a8a; border: 2px solid #60a5fa; }
            """)
            
            self.app_checkboxes[flatpak_id] = btn
            grid.addWidget(btn, row, col)
            
            col += 1
            if col > 3:
                col = 0
                row += 1

        nav_layout = QHBoxLayout()
        btn_back = QPushButton("Voltar")
        btn_back.setProperty("type", "secondary")
        btn_back.clicked.connect(lambda: [self.stacked.setCurrentIndex(0), self.update_step(1, "Boas-vindas")])
        
        btn_next = QPushButton("Instalar Selecionados")
        btn_next.clicked.connect(self.start_installation)
        
        nav_layout.addWidget(btn_back)
        nav_layout.addStretch()
        nav_layout.addWidget(btn_next)
        
        l.addWidget(title)
        l.addWidget(subtitle)
        l.addSpacing(20)
        l.addLayout(grid)
        l.addStretch()
        l.addLayout(nav_layout)
        
        self.stacked.addWidget(page)

    def init_progress_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.prog_title = QLabel("Configurando o Fusion OS...")
        self.prog_title.setFont(QFont("Inter", 26, QFont.Weight.Bold))
        self.prog_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedSize(650, 35)
        self.progress_bar.setValue(0)
        
        self.prog_log = QLabel("Iniciando processos...")
        self.prog_log.setStyleSheet("color: #cbd5e1;")
        self.prog_log.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        l.addStretch()
        l.addWidget(self.prog_title)
        l.addSpacing(20)
        l.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addSpacing(10)
        l.addWidget(self.prog_log)
        l.addStretch()
        
        self.stacked.addWidget(page)

    def init_finish_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Tudo Pronto!")
        title.setFont(QFont("Inter", 34, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #4ade80;")
        
        subtitle = QLabel("O Fusion OS foi configurado com sucesso e está pronto para uso.")
        subtitle.setFont(QFont("Inter", 15))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #cbd5e1;")
        
        btn_finish = QPushButton("Começar a Usar")
        btn_finish.setFixedSize(200, 50)
        btn_finish.clicked.connect(self.close)
        
        l.addStretch()
        l.addWidget(title)
        l.addWidget(subtitle)
        l.addSpacing(40)
        l.addWidget(btn_finish, alignment=Qt.AlignmentFlag.AlignCenter)
        l.addStretch()
        
        self.stacked.addWidget(page)

    def start_installation(self):
        selected = [f for f, btn in self.app_checkboxes.items() if btn.isChecked()]
        if not selected:
            QMessageBox.information(self, "Aviso", "Nenhum aplicativo foi selecionado. Pulando instalação.")
            self.stacked.setCurrentIndex(3)
            self.update_step(3, "Finalizado")
            self.step_label.hide()
            return

        self.stacked.setCurrentIndex(2)
        self.update_step(3, "Instalando")
        
        cmds = []
        cmds.append("sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
        
        for flatpak_id in selected:
            # sudo flatpak run to ensure system-wide install works without prompts
            cmds.append(f"sudo flatpak install -y flathub {flatpak_id}")
                
        self.worker = WorkerThread(cmds)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.log.connect(self.prog_log.setText)
        self.worker.finished.connect(self.on_installation_finished)
        self.worker.start()

    def on_installation_finished(self, success, msg):
        self.step_label.hide()
        if success:
            self.stacked.setCurrentIndex(3)
        else:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro durante a configuração:\\n{msg}")
            self.stacked.setCurrentIndex(1)
            self.step_label.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Previne que o app rode como root de forma acidental corrompendo X11/Wayland
    os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"
    window = FusionWelcome()
    window.show()
    sys.exit(app.exec())
