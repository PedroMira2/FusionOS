import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QComboBox, QCheckBox,
    QProgressBar, QGridLayout, QGraphicsDropShadowEffect, QFrame
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QThread
from PyQt6.QtGui import QColor, QCursor

class InstallThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    
    def __init__(self, apps):
        super().__init__()
        self.apps = apps
        
    def run(self):
        total = len(self.apps)
        if total == 0:
            self.progress.emit(100)
            self.finished.emit()
            return
            
        for i, app_id in enumerate(self.apps):
            try:
                subprocess.run(['flatpak', 'install', 'flathub', app_id, '-y', '--noninteractive'], check=False)
            except:
                pass
            self.progress.emit(int(((i + 1) / total) * 100))
            
        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(900, 620)
        
        self.old_pos = None
        self.current_step = 0
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        
        self.container = QFrame()
        self.container.setObjectName("container")
        self.container.setStyleSheet("""
            QFrame#container {
                background-color: #1A1D27;
                border-radius: 12px;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 127))
        shadow.setOffset(0, 0)
        self.container.setGraphicsEffect(shadow)
        
        main_layout.addWidget(self.container)
        
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(40)
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setStyleSheet("""
            QFrame#titleBar {
                background-color: #0D0F1A;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(16, 0, 16, 0)
        
        title_label = QLabel("FusionOS")
        title_label.setStyleSheet("color: #E8ECF5; font-family: Inter, system-ui; font-size: 13px; font-weight: 600;")
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("btnClose")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.setStyleSheet("""
            QPushButton#btnClose {
                color: #6B7280;
                background: transparent;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#btnClose:hover {
                color: #FF6B7A;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_btn)
        
        self.title_bar.mousePressEvent = self.title_press
        self.title_bar.mouseMoveEvent = self.title_move
        
        container_layout.addWidget(self.title_bar)
        
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setStyleSheet("""
            QFrame#sidebar {
                background-color: #0D0F1A;
                border-bottom-left-radius: 12px;
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(24, 24, 24, 24)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        logo_label = QLabel("FusionOS")
        logo_label.setStyleSheet("color: #E8ECF5; font-family: Inter, system-ui; font-size: 16px; font-weight: bold; margin-bottom: 24px;")
        sidebar_layout.addWidget(logo_label)
        
        self.step_labels = []
        steps = ["⧉ Bem-vindo", "🌐 Idioma", "✨ Aparência", "⧗ Aplicativos", "✔ Concluir"]
        
        for i, text in enumerate(steps):
            lbl = QLabel(text)
            lbl.setObjectName(f"step_{i}")
            lbl.setFixedHeight(36)
            sidebar_layout.addWidget(lbl)
            self.step_labels.append(lbl)
            
        sidebar_layout.addStretch()
        
        body_layout.addWidget(self.sidebar)
        
        content_container = QFrame()
        content_container.setObjectName("contentContainer")
        content_container.setStyleSheet("""
            QFrame#contentContainer {
                background-color: #1A1D27;
                border-bottom-right-radius: 12px;
            }
        """)
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #1A1D27; border: none;")
        
        self.setup_page_1()
        self.setup_page_2()
        self.setup_page_3()
        self.setup_page_4()
        self.setup_page_5()
        
        content_layout.addWidget(self.stack)
        
        self.footer = QFrame()
        self.footer.setFixedHeight(60)
        self.footer.setObjectName("footer")
        self.footer.setStyleSheet("""
            QFrame#footer {
                background-color: #14172A;
                border-bottom-right-radius: 12px;
            }
        """)
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(24, 0, 24, 0)
        
        self.btn_back = QPushButton("Voltar")
        self.btn_back.setObjectName("btnBack")
        self.btn_back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_back.clicked.connect(self.prev_step)
        
        self.btn_next = QPushButton("Avançar")
        self.btn_next.setObjectName("btnNext")
        self.btn_next.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_next.clicked.connect(self.next_step)
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_back)
        footer_layout.addWidget(self.btn_next)
        
        content_layout.addWidget(self.footer)
        
        body_layout.addWidget(content_container)
        
        container_layout.addLayout(body_layout)
        
        self.update_sidebar()
        self.update_footer()
        
        self.setStyleSheet("""
            QWidget {
                font-family: Inter, Segoe UI, system-ui;
                color: #E8ECF5;
            }
            QPushButton#btnNext {
                background-color: #5B8BFF;
                color: white;
                border-radius: 8px;
                padding: 10px 28px;
                font-size: 14px;
                font-weight: 600;
                border: none;
            }
            QPushButton#btnNext:hover {
                background-color: #4A7AEE;
            }
            QPushButton#btnBack {
                background: transparent;
                color: #9CA3AF;
                border-radius: 8px;
                padding: 10px 20px;
                border: none;
                font-size: 14px;
            }
            QPushButton#btnBack:hover {
                color: #E8ECF5;
            }
        """)

    def title_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def title_move(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def update_sidebar(self):
        for i, lbl in enumerate(self.step_labels):
            if i == self.current_step:
                lbl.setStyleSheet("""
                    background-color: #5B8BFF;
                    border-radius: 8px;
                    color: white;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 14px;
                """)
            else:
                lbl.setStyleSheet("""
                    background-color: transparent;
                    color: #6B7280;
                    padding: 8px 16px;
                    font-size: 14px;
                """)

    def update_footer(self):
        if self.current_step == 0:
            self.btn_back.hide()
        else:
            self.btn_back.show()
            
        if self.current_step == 4:
            self.footer.hide()
        else:
            self.footer.show()

    def next_step(self):
        if self.current_step < 4:
            self.current_step += 1
            self.stack.setCurrentIndex(self.current_step)
            self.update_sidebar()
            self.update_footer()

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.stack.setCurrentIndex(self.current_step)
            self.update_sidebar()
            self.update_footer()

    def create_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        return page, layout

    def setup_page_1(self):
        page, layout = self.create_page()
        
        title = QLabel("Bem-vindo ao FusionOS.")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #E8ECF5;")
        
        subtitle = QLabel("Um sistema feito para você.")
        subtitle.setStyleSheet("font-size: 16px; color: #9CA3AF; margin-bottom: 32px;")
        
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #14172A;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)
        
        items = [
            "✨  Simples e sofisticado",
            "⚡  Ultra rápido e moderno",
            "🎨  Completamente personalizável"
        ]
        for item in items:
            lbl = QLabel(item)
            lbl.setStyleSheet("font-size: 15px; color: #E8ECF5;")
            card_layout.addWidget(lbl)
            
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(card)
        layout.addStretch()
        
        self.stack.addWidget(page)

    def setup_page_2(self):
        page, layout = self.create_page()
        
        title = QLabel("Selecionar Idioma")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #E8ECF5; margin-bottom: 24px;")
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            "Português (Brasil)", "English", "Español", "Français", "Deutsch", "Italiano"
        ])
        
        self.lang_map = {
            "Português (Brasil)": "pt_BR.UTF-8",
            "English": "en_US.UTF-8",
            "Español": "es_ES.UTF-8",
            "Français": "fr_FR.UTF-8",
            "Deutsch": "de_DE.UTF-8",
            "Italiano": "it_IT.UTF-8"
        }
        
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background-color: #14172A;
                color: #E8ECF5;
                border: 1px solid #2E3452;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #14172A;
                color: #E8ECF5;
                selection-background-color: #5B8BFF;
            }
        """)
        self.lang_combo.currentTextChanged.connect(self.change_language)
        
        layout.addWidget(title)
        layout.addWidget(self.lang_combo)
        layout.addStretch()
        
        self.stack.addWidget(page)
        
    def change_language(self, text):
        locale = self.lang_map.get(text, "en_US.UTF-8")
        try:
            subprocess.Popen(['localectl', 'set-locale', f'LANG={locale}'])
        except:
            pass

    def setup_page_3(self):
        page, layout = self.create_page()
        
        title = QLabel("Modo de Aparência")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #E8ECF5; margin-bottom: 24px;")
        
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(24)
        
        self.dark_card = QFrame()
        self.dark_card.setFixedSize(200, 140)
        self.dark_card.setStyleSheet("background-color: #14172A; border-radius: 12px; border: 2px solid #5B8BFF;")
        self.dark_card.mousePressEvent = lambda e: self.set_theme("dark")
        self.dark_card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        dark_layout = QVBoxLayout(self.dark_card)
        dark_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl1 = QLabel("Escuro")
        lbl1.setStyleSheet("border: none; font-size: 16px; font-weight: bold;")
        dark_layout.addWidget(lbl1)
        
        self.light_card = QFrame()
        self.light_card.setFixedSize(200, 140)
        self.light_card.setStyleSheet("background-color: #14172A; border-radius: 12px; border: 2px solid #2E3452;")
        self.light_card.mousePressEvent = lambda e: self.set_theme("light")
        self.light_card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        light_layout = QVBoxLayout(self.light_card)
        light_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl2 = QLabel("Claro")
        lbl2.setStyleSheet("border: none; font-size: 16px; font-weight: bold;")
        light_layout.addWidget(lbl2)
        
        cards_layout.addWidget(self.dark_card)
        cards_layout.addWidget(self.light_card)
        cards_layout.addStretch()
        
        layout.addWidget(title)
        layout.addLayout(cards_layout)
        layout.addStretch()
        
        self.stack.addWidget(page)
        
    def set_theme(self, theme):
        if theme == "dark":
            self.dark_card.setStyleSheet("background-color: #14172A; border-radius: 12px; border: 2px solid #5B8BFF;")
            self.light_card.setStyleSheet("background-color: #14172A; border-radius: 12px; border: 2px solid #2E3452;")
            cmd = ['lookandfeeltool', '-a', 'org.kde.breezedark.desktop']
        else:
            self.light_card.setStyleSheet("background-color: #14172A; border-radius: 12px; border: 2px solid #5B8BFF;")
            self.dark_card.setStyleSheet("background-color: #14172A; border-radius: 12px; border: 2px solid #2E3452;")
            cmd = ['lookandfeeltool', '-a', 'org.kde.breeze.desktop']
            
        try:
            subprocess.Popen(cmd)
        except:
            pass

    def setup_page_4(self):
        page, layout = self.create_page()
        
        title = QLabel("Instalar Aplicativos")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #E8ECF5;")
        
        subtitle = QLabel("Escolha o que quer instalar")
        subtitle.setStyleSheet("font-size: 16px; color: #9CA3AF; margin-bottom: 24px;")
        
        apps = [
            ("com.valvesoftware.Steam", "🎮 Steam Games", "Plataforma de jogos"),
            ("com.discordapp.Discord", "💬 Discord", "Chat e comunidade"),
            ("com.google.Chrome", "🌐 Google Chrome", "Navegador web"),
            ("com.spotify.Client", "🎵 Spotify", "Musica"),
            ("com.visualstudio.code", "💻 VS Code", "Editor de codigo"),
            ("com.heroicgameslauncher.hgl", "🎮 Heroic Games", "Epic Games no Linux")
        ]
        
        grid = QGridLayout()
        grid.setSpacing(16)
        
        self.app_checkboxes = []
        
        for i, app in enumerate(apps):
            app_id, name, desc = app
            
            card = QFrame()
            card.setStyleSheet("background-color: #14172A; border-radius: 12px;")
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(16, 16, 16, 16)
            
            text_layout = QVBoxLayout()
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("font-weight: bold; font-size: 15px;")
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("color: #9CA3AF; font-size: 13px;")
            
            text_layout.addWidget(name_lbl)
            text_layout.addWidget(desc_lbl)
            
            cb = QCheckBox()
            cb.setProperty("app_id", app_id)
            cb.setStyleSheet("QCheckBox::indicator { width: 18px; height: 18px; } QCheckBox { color: #5B8BFF; }")
            
            card_layout.addLayout(text_layout)
            card_layout.addStretch()
            card_layout.addWidget(cb)
            
            self.app_checkboxes.append(cb)
            
            row = i // 2
            col = i % 2
            grid.addWidget(card, row, col)
            
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(grid)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #14172A;
                border-radius: 4px;
                height: 8px;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                background-color: #5B8BFF;
                border-radius: 4px;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        self.btn_install = QPushButton("Instalar Selecionados")
        self.btn_install.setStyleSheet("""
            QPushButton {
                background-color: #5B8BFF;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
                border: none;
                margin-top: 16px;
            }
            QPushButton:hover {
                background-color: #4A7AEE;
            }
        """)
        self.btn_install.clicked.connect(self.start_install)
        self.btn_install.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        layout.addWidget(self.btn_install)
        layout.addStretch()
        
        self.stack.addWidget(page)
        
    def start_install(self):
        selected_apps = []
        for cb in self.app_checkboxes:
            if cb.isChecked():
                selected_apps.append(cb.property("app_id"))
                
        if not selected_apps:
            return
            
        self.btn_install.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        self.thread = InstallThread(selected_apps)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.install_finished)
        self.thread.start()
        
    def install_finished(self):
        self.btn_install.setEnabled(True)
        self.btn_install.setText("Instalado com sucesso!")
        self.progress_bar.hide()

    def setup_page_5(self):
        page, layout = self.create_page()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon = QLabel("✔")
        icon.setStyleSheet("color: #6BCB77; font-size: 72px; font-weight: bold;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Tudo pronto!")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #E8ECF5; margin-top: 24px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("O FusionOS está configurado e pronto para usar.")
        subtitle.setStyleSheet("font-size: 16px; color: #9CA3AF; margin-bottom: 48px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_start = QPushButton("Começar a Usar")
        btn_start.setFixedWidth(200)
        btn_start.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_start.setStyleSheet("""
            QPushButton {
                background-color: #5B8BFF;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #4A7AEE;
            }
        """)
        btn_start.clicked.connect(self.close)
        
        layout.addStretch()
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        center_btn_layout = QHBoxLayout()
        center_btn_layout.addStretch()
        center_btn_layout.addWidget(btn_start)
        center_btn_layout.addStretch()
        
        layout.addLayout(center_btn_layout)
        layout.addStretch()
        
        self.stack.addWidget(page)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
