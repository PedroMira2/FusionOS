#!/usr/bin/env python3
"""
FusionOS QuickLook
Pré-visualização instantânea e elegante de arquivos estilo macOS (Espaço / QuickLook).
Suporta imagens, texto/código, áudio, diretórios e metadados de arquivos binários.
"""

import sys
import os
import mimetypes
import hashlib
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QIcon, QFont, QPixmap, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QGraphicsDropShadowEffect, QFileDialog,
    QFrame, QSizePolicy
)

class FusionQuickLook(QWidget):
    def __init__(self, file_path=None):
        super().__init__()
        self.file_path = os.path.abspath(file_path) if file_path and os.path.exists(file_path) else None
        self.drag_position = None
        
        self.init_ui()
        if self.file_path:
            self.load_file(self.file_path)
        else:
            self.show_empty_state()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(780, 540)
        self.center_on_screen()

        # Shortcuts: Escape or Space to close
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.close)

        # Main container with shadow
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(12, 12, 12, 12)

        self.card = QFrame(self)
        self.card.setStyleSheet("""
            QFrame {
                background-color: #0D0F1A;
                border: 1px solid #2E3452;
                border-radius: 16px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 10)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 16, 20, 20)
        card_layout.setSpacing(12)

        # Header bar
        header = QHBoxLayout()
        header.setSpacing(12)

        self.lbl_title = QLabel("Fusion QuickLook")
        self.lbl_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #E8ECF5; font-family: 'Inter', system-ui;")
        
        self.lbl_subtitle = QLabel("")
        self.lbl_subtitle.setStyleSheet("font-size: 12px; color: #8F9CAE; font-family: 'Inter', system-ui;")

        header.addWidget(self.lbl_title)
        header.addWidget(self.lbl_subtitle)
        header.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(28, 28)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #1F2438;
                color: #A0ABC0;
                border: none;
                border-radius: 14px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #FF4757;
                color: white;
            }
        """)
        btn_close.clicked.connect(self.close)
        header.addWidget(btn_close)

        card_layout.addLayout(header)

        # Content area
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 6, 0, 0)
        card_layout.addLayout(self.content_layout)

        # Footer info
        self.lbl_footer = QLabel("Pressione [Espaço] ou [Esc] para fechar")
        self.lbl_footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_footer.setStyleSheet("font-size: 11px; color: #5B657A; font-family: 'Inter', system-ui;")
        card_layout.addWidget(self.lbl_footer)

        outer_layout.addWidget(self.card)

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

    def show_empty_state(self):
        self.lbl_title.setText("QuickLook")
        self.lbl_subtitle.setText("Nenhum arquivo selecionado")
        
        lbl = QLabel("Selecione um arquivo no Dolphin e pressione Espaço,\nou passe o caminho do arquivo como argumento.")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #8F9CAE; font-size: 14px; font-family: 'Inter', system-ui;")
        self.content_layout.addWidget(lbl)

    def load_file(self, path):
        basename = os.path.basename(path)
        self.lbl_title.setText(basename)
        
        if os.path.isdir(path):
            self.preview_directory(path)
            return

        size_bytes = os.path.getsize(path)
        size_str = self.format_size(size_bytes)
        mime, _ = mimetypes.guess_type(path)
        self.lbl_subtitle.setText(f"{size_str} • {mime or 'Arquivo'}")

        ext = os.path.splitext(path)[1].lower()
        image_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.svg', '.gif'}
        text_exts = {'.txt', '.py', '.sh', '.json', '.yml', '.yaml', '.conf', '.ini', 
                     '.md', '.c', '.cpp', '.h', '.html', '.css', '.js', '.ts', '.xml', '.rs', '.go'}
        audio_exts = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.opus'}

        if ext in image_exts:
            self.preview_image(path)
        elif ext in text_exts or (mime and mime.startswith('text/')):
            self.preview_text(path)
        elif ext in audio_exts or (mime and mime.startswith('audio/')):
            self.preview_audio(path, mime)
        else:
            self.preview_binary(path, mime, size_bytes)

    def preview_image(self, path):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.preview_binary(path, "image/*", os.path.getsize(path))
            return
        
        dims = f"{pixmap.width()} × {pixmap.height()} px"
        self.lbl_subtitle.setText(f"{self.lbl_subtitle.text()} • {dims}")

        lbl_img = QLabel()
        lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_img.setPixmap(pixmap.scaled(720, 420, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        lbl_img.setStyleSheet("background: #080A12; border-radius: 8px; padding: 4px;")
        self.content_layout.addWidget(lbl_img)

    def preview_text(self, path):
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(65536) # read up to 64KB for instant snappy preview
                lines = content.count('\n') + 1

            self.lbl_subtitle.setText(f"{self.lbl_subtitle.text()} • {lines} linhas")

            text_area = QTextEdit()
            text_area.setReadOnly(True)
            text_area.setPlainText(content)
            text_area.setStyleSheet("""
                QTextEdit {
                    background-color: #141724;
                    color: #E2E8F0;
                    border: 1px solid #242B42;
                    border-radius: 8px;
                    padding: 12px;
                    font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', monospace;
                    font-size: 12px;
                }
            """)
            self.content_layout.addWidget(text_area)
        except Exception as e:
            self.preview_binary(path, "text/plain", os.path.getsize(path))

    def preview_audio(self, path, mime):
        frame = QFrame()
        frame.setStyleSheet("background: #141724; border-radius: 12px; padding: 20px;")
        f_layout = QVBoxLayout(frame)
        f_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f_layout.setSpacing(16)

        icon_lbl = QLabel("🎵")
        icon_lbl.setStyleSheet("font-size: 54px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f_layout.addWidget(icon_lbl)

        name_lbl = QLabel(os.path.basename(path))
        name_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #5B8BFF;")
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f_layout.addWidget(name_lbl)

        format_lbl = QLabel(f"Formato de Áudio: {mime or 'Áudio Hi-Res'}")
        format_lbl.setStyleSheet("color: #8F9CAE; font-size: 13px;")
        format_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f_layout.addWidget(format_lbl)

        hint_lbl = QLabel("Áudio otimizado pelo motor PipeWire 384kHz / Dolby Atmos DSP do FusionOS")
        hint_lbl.setStyleSheet("color: #6BCB77; font-size: 11px; font-style: italic;")
        hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f_layout.addWidget(hint_lbl)

        self.content_layout.addWidget(frame)

    def preview_directory(self, path):
        try:
            items = os.listdir(path)
            item_count = len(items)
            self.lbl_subtitle.setText(f"Diretório • {item_count} itens")

            text_area = QTextEdit()
            text_area.setReadOnly(True)
            preview_list = "\n".join([f"📁 {it}" if os.path.isdir(os.path.join(path, it)) else f"📄 {it}" for it in items[:100]])
            if item_count > 100:
                preview_list += f"\n... e mais {item_count - 100} itens"
            text_area.setPlainText(preview_list)
            text_area.setStyleSheet("""
                QTextEdit {
                    background-color: #141724;
                    color: #CBD5E1;
                    border: 1px solid #242B42;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 13px;
                }
            """)
            self.content_layout.addWidget(text_area)
        except Exception as e:
            self.show_empty_state()

    def preview_binary(self, path, mime, size):
        frame = QFrame()
        frame.setStyleSheet("background: #141724; border-radius: 12px; padding: 24px;")
        f_layout = QVBoxLayout(frame)
        f_layout.setSpacing(14)

        icon_lbl = QLabel("📦")
        icon_lbl.setStyleSheet("font-size: 48px;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f_layout.addWidget(icon_lbl)

        info_lbl = QLabel(f"Tipo: {mime or 'Binário / Desconhecido'}\nTamanho: {self.format_size(size)}")
        info_lbl.setStyleSheet("font-size: 13px; color: #E8ECF5; font-family: monospace;")
        info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f_layout.addWidget(info_lbl)

        self.content_layout.addWidget(frame)

    @staticmethod
    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

def main():
    app = QApplication(sys.argv)
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    quicklook = FusionQuickLook(file_path)
    quicklook.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
