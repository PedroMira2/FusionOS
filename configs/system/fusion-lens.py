#!/usr/bin/env python3
"""
FusionOS Lens • OCR Instantâneo e Leitor Visual
Captura texto diretamente de áreas da tela ou imagens e copia para a Área de Transferência.
"""

import sys
import os
import subprocess
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

def run_ocr(image_path):
    text = ""
    # 1. Tentar via Tesseract se disponível
    if subprocess.run(["which", "tesseract"], capture_output=True).returncode == 0:
        res = subprocess.run(["tesseract", image_path, "stdout", "-l", "por+eng", "--oem", "1"],
                             capture_output=True, text=True, check=False)
        text = res.stdout.strip()
    
    # Se tesseract não retornar ou não estiver instalado, fornecer aviso amigável
    if not text:
        text = f"[FusionOS Lens] Imagem capturada: {os.path.basename(image_path)}"

    # Copiar para o clipboard do sistema (Wayland/X11)
    app = QApplication(sys.argv)
    clipboard = app.clipboard()
    clipboard.setText(text)

    # Notificar usuário
    preview = text[:80] + ("..." if len(text) > 80 else "")
    if command_exists("notify-send"):
        subprocess.Popen([
            "notify-send", "-a", "Fusion Lens", "-i", "edit-copy",
            "Texto Copiado (OCR)", f"{preview}"
        ])

def capture_and_ocr():
    tmp_img = "/tmp/fusion_lens_capture.png"
    # Capturar área da tela via spectacle ou grim
    if command_exists("spectacle"):
        subprocess.run(["spectacle", "-r", "-b", "-n", "-o", tmp_img], check=False)
    elif command_exists("grim"):
        if command_exists("slurp"):
            geom = subprocess.run(["slurp"], capture_output=True, text=True).stdout.strip()
            if geom:
                subprocess.run(["grim", "-g", geom, tmp_img], check=False)
        else:
            subprocess.run(["grim", tmp_img], check=False)
    
    if os.path.exists(tmp_img):
        run_ocr(tmp_img)

def command_exists(cmd):
    return subprocess.run(["which", cmd], capture_output=True).returncode == 0

def main():
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        run_ocr(sys.argv[1])
    else:
        capture_and_ocr()

if __name__ == "__main__":
    main()
