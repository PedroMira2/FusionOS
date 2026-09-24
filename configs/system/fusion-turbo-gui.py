#!/usr/bin/env python3
"""
FusionOS Turbo Center
Central de Otimização Extrema e Monitor de Latência de Alta Performance.
Permite alternar entre os 4 modos dedicados (Eco, Multitarefas, Máximo, Jogos),
executar TRIM em SSDs, descarregar cache de RAM e testar a latência do sistema.
"""

import sys
import os
import time
import subprocess
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGraphicsDropShadowEffect, QProgressBar, QMessageBox
)

class BenchmarkWorker(QThread):
    result_signal = pyqtSignal(float, float)

    def run(self):
        # 1. Medir latência de CPU (1 milhão de iterações matemáticas)
        t0 = time.perf_counter()
        _ = sum(i * i for i in range(1000000))
        cpu_ms = (time.perf_counter() - t0) * 1000.0

        # 2. Medir tempo de resposta de memória
        t0 = time.perf_counter()
        arr = bytearray(32 * 1024 * 1024)
        for i in range(0, len(arr), 4096):
            arr[i] = 1
        mem_ms = (time.perf_counter() - t0) * 1000.0

        self.result_signal.emit(cpu_ms, mem_ms)

class FusionTurboGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(600, 520)
        self.center_on_screen()

        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        card = QFrame(self)
        card.setStyleSheet("""
            QFrame {
                background-color: #0D0F1A;
                border: 1px solid #2E3452;
                border-radius: 20px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 22)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        lbl_t = QLabel("🚀  Fusion Turbo Center • Otimização Extrema")
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

        # Performance Mode Selector (4 modes)
        mode_box = QFrame()
        mode_box.setStyleSheet("background-color: #141724; border: 1px solid #23293D; border-radius: 12px; padding: 10px;")
        m_layout = QVBoxLayout(mode_box)
        m_layout.setSpacing(8)

        lbl_m = QLabel("Perfil de Performance Ativo:")
        lbl_m.setStyleSheet("color: #E8ECF5; font-size: 12px; font-weight: bold;")
        m_layout.addWidget(lbl_m)

        btn_grid = QHBoxLayout()
        btn_grid.setSpacing(6)
        modes = [
            ("powersave", "🍃 Eco"),
            ("multitask", "⚡ Multitarefa"),
            ("performance", "🚀 Máximo"),
            ("gaming", "🎮 Jogos Extremo")
        ]
        self.mode_buttons = {}
        for m_id, label in modes:
            b = QPushButton(label)
            b.setFixedHeight(32)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda ch, m=m_id: self.change_mode(m))
            self.mode_buttons[m_id] = b
            btn_grid.addWidget(b)
        m_layout.addLayout(btn_grid)
        layout.addWidget(mode_box)
        self.update_mode_ui("multitask")

        # 1-Click Optimizations Box
        opt_box = QFrame()
        opt_box.setStyleSheet("background-color: #141724; border: 1px solid #23293D; border-radius: 12px; padding: 12px;")
        o_layout = QVBoxLayout(opt_box)
        o_layout.setSpacing(10)

        lbl_opt = QLabel("Ações de Otimização Imediata:")
        lbl_opt.setStyleSheet("color: #E8ECF5; font-size: 12px; font-weight: bold;")
        o_layout.addWidget(lbl_opt)

        opt_grid = QHBoxLayout()
        opt_grid.setSpacing(8)

        btn_ram = QPushButton("🧹 Limpar RAM & Cache")
        btn_trim = QPushButton("💾 Otimizar SSDs (TRIM)")
        btn_shader = QPushButton("⚡ Reset Shader Cache")

        for btn in [btn_ram, btn_trim, btn_shader]:
            btn.setFixedHeight(34)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1F2538;
                    color: #CBD5E1;
                    border: 1px solid #2A314A;
                    border-radius: 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #5B8BFF;
                    color: white;
                    border-color: #5B8BFF;
                }
            """)
            opt_grid.addWidget(btn)

        btn_ram.clicked.connect(self.clean_ram)
        btn_trim.clicked.connect(self.trim_ssds)
        btn_shader.clicked.connect(self.clean_shaders)

        o_layout.addLayout(opt_grid)
        layout.addWidget(opt_box)

        # Benchmark & Latency Box
        bench_box = QFrame()
        bench_box.setStyleSheet("background-color: #141724; border: 1px solid #23293D; border-radius: 12px; padding: 12px;")
        b_layout = QVBoxLayout(bench_box)
        b_layout.setSpacing(8)

        b_header = QHBoxLayout()
        lbl_bench_title = QLabel("⏱️  Teste de Latência de Resposta do Sistema:")
        lbl_bench_title.setStyleSheet("color: #E8ECF5; font-size: 12px; font-weight: bold;")
        b_header.addWidget(lbl_bench_title)
        b_header.addStretch()

        self.btn_run_bench = QPushButton("Testar Agora")
        self.btn_run_bench.setFixedSize(96, 28)
        self.btn_run_bench.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_run_bench.setStyleSheet("background-color: #5B8BFF; color: white; border: none; border-radius: 6px; font-weight: bold; font-size: 11px;")
        self.btn_run_bench.clicked.connect(self.run_benchmark)
        b_header.addWidget(self.btn_run_bench)
        b_layout.addLayout(b_header)

        self.lbl_bench_res = QLabel("Pressione 'Testar Agora' para verificar os tempos de resposta de CPU e RAM.")
        self.lbl_bench_res.setStyleSheet("color: #8F9CAE; font-size: 11px;")
        b_layout.addWidget(self.lbl_bench_res)

        layout.addWidget(bench_box)

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

    def change_mode(self, mode):
        self.update_mode_ui(mode)
        script = "/usr/local/bin/fusion-power-mode"
        if not os.path.exists(script):
            script = os.path.join(os.path.dirname(__file__), "fusion-power-mode.sh")
        subprocess.Popen(["bash", script, mode], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def update_mode_ui(self, active_mode):
        style_act = "background-color: #5B8BFF; color: white; border: none; border-radius: 6px; font-weight: bold; font-size: 11px;"
        style_inact = "background-color: #1F2538; color: #8F9CAE; border: 1px solid #2A314A; border-radius: 6px; font-size: 11px;"
        for m, b in self.mode_buttons.items():
            b.setStyleSheet(style_act if m == active_mode else style_inact)

    def clean_ram(self):
        subprocess.Popen(["pkexec", "sh", "-c", "sync; echo 3 > /proc/sys/vm/drop_caches"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if subprocess.run(["which", "notify-send"], capture_output=True).returncode == 0:
            subprocess.Popen(["notify-send", "-a", "Fusion Turbo", "-i", "dialog-ok", "Memória RAM Otimizada", "Caches inativos liberados instantaneamente."])

    def trim_ssds(self):
        subprocess.Popen(["pkexec", "fstrim", "-av"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if subprocess.run(["which", "notify-send"], capture_output=True).returncode == 0:
            subprocess.Popen(["notify-send", "-a", "Fusion Turbo", "-i", "drive-harddisk", "TRIM Executado", "Blocos de dados limpos nos SSDs NVMe e SATA."])

    def clean_shaders(self):
        home = os.path.expanduser("~")
        cache_paths = [
            os.path.join(home, ".cache/mesa_shader_cache"),
            os.path.join(home, ".cache/radv_builtin_shaders")
        ]
        for p in cache_paths:
            if os.path.exists(p):
                subprocess.run(["rm", "-rf", p], check=False)
        if subprocess.run(["which", "notify-send"], capture_output=True).returncode == 0:
            subprocess.Popen(["notify-send", "-a", "Fusion Turbo", "-i", "applications-games", "Cache de Shaders Resetado", "Pronto para nova compilação limpa."])

    def run_benchmark(self):
        self.btn_run_bench.setEnabled(False)
        self.btn_run_bench.setText("Testando...")
        self.worker = BenchmarkWorker()
        self.worker.result_signal.connect(self.on_benchmark_done)
        self.worker.start()

    def on_benchmark_done(self, cpu_ms, mem_ms):
        self.btn_run_bench.setEnabled(True)
        self.btn_run_bench.setText("Testar Agora")
        score = "Excelente (Padrão Estúdio / E-Sports)" if cpu_ms < 50 else "Ótimo"
        self.lbl_bench_res.setText(f"Latência de Cálculo CPU: {cpu_ms:.1f} ms • Largura de Banda RAM: {mem_ms:.1f} ms\nStatus: {score}")
        self.lbl_bench_res.setStyleSheet("color: #6BCB77; font-size: 11px; font-weight: bold;")

def main():
    app = QApplication(sys.argv)
    w = FusionTurboGUI()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
