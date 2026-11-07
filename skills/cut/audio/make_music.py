"""Builds lofi-76bpm.mp3 from sine waves and noise, so no third party owns it.

Run from the repo root: python3 skills/cut/audio/make_music.py
"""
import subprocess
import wave
import numpy as np

SR, BPM, BARS = 44100, 76, 16
BEAT = 60 / BPM
TOTAL = int(SR * BEAT * 4 * BARS)
rng = np.random.default_rng(76)
mix = np.zeros((TOTAL, 2))
CHORDS = [
    [146.83, 220.00, 261.63, 349.23],
    [130.81, 196.00, 246.94, 329.63],
    [110.00, 196.00, 261.63, 329.63],
    [116.54, 174.61, 220.00, 293.66],
]


def add(sound, at, left=1.0, right=1.0):
    # Wrapping the tail back to the start makes the loop seamless.
    idx = (int(at * SR) + np.arange(len(sound))) % TOTAL
    np.add.at(mix[:, 0], idx, sound * left)
    np.add.at(mix[:, 1], idx, sound * right)


def keys(freq, secs):
    t = np.arange(int(secs * SR)) / SR
    tone = sum(a * np.sin(2 * np.pi * freq * n * t) for n, a in ((1, 1), (2, 0.28), (3, 0.08)))
    return tone * np.exp(-t * 1.4) * np.minimum(t / 0.012, 1)


def bass(freq, secs):
    t = np.arange(int(secs * SR)) / SR
    return np.sin(2 * np.pi * freq / 2 * t) * np.exp(-t * 1.8) * np.minimum(t / 0.01, 1)


def kick():
    t = np.arange(int(0.28 * SR)) / SR
    return np.sin(2 * np.pi * (48 * t + 9 * (1 - np.exp(-t * 28)))) * np.exp(-t * 15)


def noise_hit(secs, decay):
    t = np.arange(int(secs * SR)) / SR
    return np.diff(rng.normal(size=len(t)), prepend=0) * np.exp(-t * decay)


for bar in range(BARS):
    start = bar * BEAT * 4
    chord = CHORDS[bar % 4]
    for i, freq in enumerate(chord):
        pan = 0.35 + 0.3 * i / 3
        add(keys(freq, BEAT * 4) * 0.17, start + i * 0.012, 1 - pan, pan)
    add(keys(chord[3] * 2, BEAT * 1.5) * 0.05, start + BEAT * 2.5, 0.4, 0.6)
    add(bass(chord[0], BEAT * 2) * 0.3, start)
    add(bass(chord[0], BEAT) * 0.22, start + BEAT * 2.5)
    add(kick() * 0.5, start)
    add(kick() * 0.42, start + BEAT * 2.5)
    for beat in (1, 3):
        add(noise_hit(0.18, 24) * 0.035, start + BEAT * beat)
    for step in range(8):
        swing = 0.035 if step % 2 else 0
        add(noise_hit(0.05, 90) * 0.012, start + step * BEAT / 2 + swing)

mix += rng.normal(0, 0.0016, mix.shape)

# A gentle FFT roll-off gives the dull, warm sound of lo-fi.
freqs = np.fft.rfftfreq(TOTAL, 1 / SR)
curve = 1 / np.sqrt(1 + (freqs / 2600) ** 4)
mix = np.fft.irfft(np.fft.rfft(mix, axis=0) * curve[:, None], n=TOTAL, axis=0)
mix = np.tanh(mix * 1.2)
mix *= 0.7 / np.abs(mix).max()

wav = "/tmp/lofi-76bpm.wav"
with wave.open(wav, "wb") as f:
    f.setnchannels(2)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes((mix * 32767).astype("<i2").tobytes())
subprocess.run(
    ["ffmpeg", "-y", "-v", "error", "-i", wav, "-c:a", "libmp3lame", "-b:a", "128k",
     "-metadata", "title=Studio lo-fi 76 BPM", "skills/cut/audio/lofi-76bpm.mp3"],
    check=True,
)
