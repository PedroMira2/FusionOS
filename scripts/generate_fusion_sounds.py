#!/usr/bin/env python3
"""
FusionOS Audio Engine - Gera sintetizadores acusticos de alta fidelidade
Gera ondas PCM 16-bit 44.1kHz para o tema sonoro oficial do FusionOS.
"""

import math
import struct
import wave
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "configs" / "sounds" / "fusionos" / "stereo"
OUT_DIR.mkdir(parents=True, exist_ok=True)

RATE = 44100

def write_wav(filename, samples):
    path = OUT_DIR / filename
    with wave.open(str(path), 'w') as wf:
        wf.setnchannels(2)  # Stereo
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(RATE)
        packed = bytearray()
        for left, right in samples:
            l_int = max(-32767, min(32767, int(left * 32767)))
            r_int = max(-32767, min(32767, int(right * 32767)))
            packed.extend(struct.pack('<hh', l_int, r_int))
        wf.writeframes(packed)
    print(f"Gerado som: {filename}")

def gen_startup():
    # Chime relaxante acorde Major 9th: 174.6Hz (F3), 261.6Hz (C4), 392Hz (G4), 440Hz (A4), 659.2Hz (E5)
    duration = 2.8
    total_frames = int(RATE * duration)
    freqs = [174.6, 261.6, 392.0, 440.0, 659.2]
    weights = [0.35, 0.25, 0.2, 0.15, 0.1]
    samples = []

    for i in range(total_frames):
        t = i / RATE
        envelope = math.exp(-t * 1.5)
        # Ataque suave
        if t < 0.15:
            envelope *= (t / 0.15)

        val = 0.0
        for f, w in zip(freqs, weights):
            val += math.sin(2 * math.pi * f * t) * w

        val *= envelope * 0.7
        samples.append((val, val))
    write_wav("desktop-login.wav", samples)

def gen_notification():
    # Gota d'agua harmônica 784Hz (G5) -> 1046Hz (C6)
    duration = 0.4
    total_frames = int(RATE * duration)
    samples = []
    for i in range(total_frames):
        t = i / RATE
        envelope = math.exp(-t * 9.0)
        freq = 784.0 + (1046.0 - 784.0) * (t / duration)
        val = math.sin(2 * math.pi * freq * t) * envelope * 0.6
        samples.append((val, val))
    write_wav("message-new-instant.wav", samples)

def gen_device_added():
    # Tom ascendente suave 587Hz -> 880Hz
    duration = 0.25
    total_frames = int(RATE * duration)
    samples = []
    for i in range(total_frames):
        t = i / RATE
        envelope = math.exp(-t * 6.0)
        freq = 587.3 if t < 0.1 else 880.0
        val = math.sin(2 * math.pi * freq * t) * envelope * 0.5
        samples.append((val * 0.9, val * 1.1))
    write_wav("device-added.wav", samples)

def gen_device_removed():
    # Tom descendente suave 880Hz -> 587Hz
    duration = 0.25
    total_frames = int(RATE * duration)
    samples = []
    for i in range(total_frames):
        t = i / RATE
        envelope = math.exp(-t * 6.0)
        freq = 880.0 if t < 0.1 else 587.3
        val = math.sin(2 * math.pi * freq * t) * envelope * 0.5
        samples.append((val * 1.1, val * 0.9))
    write_wav("device-removed.wav", samples)

def gen_bell():
    # Toque acustico discreto 440Hz com harmonicos
    duration = 0.2
    total_frames = int(RATE * duration)
    samples = []
    for i in range(total_frames):
        t = i / RATE
        envelope = math.exp(-t * 12.0)
        val = (math.sin(2 * math.pi * 440 * t) * 0.7 + math.sin(2 * math.pi * 880 * t) * 0.3) * envelope * 0.4
        samples.append((val, val))
    write_wav("bell-window-system.wav", samples)

if __name__ == "__main__":
    gen_startup()
    gen_notification()
    gen_device_added()
    gen_device_removed()
    gen_bell()
    print("Todos os sons sintetizados com sucesso!")
