"""Gera a trilha de efeitos sonoros (sem música) sincronizada com motion.html.
Uso: python3 sfx.py saida.wav"""
import sys
import wave
import numpy as np

SR = 48000
DUR = 45.0
rng = np.random.default_rng(7)


def env(n, a=0.005, r=0.1):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / r)
    return e


def lowpass(x, k):
    # média móvel simples, suficiente para suavizar ruído
    return np.convolve(x, np.ones(k) / k, mode="same")


def whoosh(d=0.45, up=True):
    n = int(SR * d)
    t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    shape = np.sin(np.pi * t) ** 2
    lo = lowpass(noise, 40)
    hi = noise - lowpass(noise, 6)
    mix = t if up else 1 - t
    return (lo * (1 - mix) * 2.5 + hi * mix * 0.35) * shape * 0.5


def pop(f=520, d=0.12):
    n = int(SR * d)
    t = np.arange(n) / SR
    freq = f * (1 + 1.2 * np.exp(-t / 0.012))
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * env(n, 0.002, 0.035) * 0.55


def ding(f=1320, d=0.7, vol=0.3):
    n = int(SR * d)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.01 * t) + 0.12 * np.sin(2 * np.pi * f * 3.0 * t)
    return s * env(n, 0.003, 0.22) * vol


def chime():
    out = np.zeros(int(SR * 1.4))
    for i, f in enumerate([784, 988, 1175, 1568]):
        x = ding(f, 1.0, 0.18)
        o = int(SR * 0.08 * i)
        out[o:o + len(x)] += x
    return out


def nope():
    # dois tons graves e curtos, suaves ("não")
    out = np.zeros(int(SR * 0.4))
    for i, f in enumerate([220, 185]):
        n = int(SR * 0.16)
        t = np.arange(n) / SR
        x = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t)) * env(n, 0.004, 0.06) * 0.35
        o = int(SR * 0.13 * i)
        out[o:o + n] += x
    return out


def click(f=2400):
    n = int(SR * 0.05)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) * 0.6 + rng.standard_normal(n) * 0.4) * env(n, 0.0005, 0.008)
    return s * 0.5


def thud():
    n = int(SR * 0.35)
    t = np.arange(n) / SR
    freq = 90 + 80 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * env(n, 0.002, 0.09) * 0.8


def rattle(d=1.2):
    # leve "chacoalhar" da dentadura solta
    out = np.zeros(int(SR * d))
    for k in range(9):
        c = click(1400 + rng.integers(0, 900)) * 0.35
        o = int(SR * (k * d / 9 + rng.uniform(0, 0.03)))
        out[o:o + len(c)] += c[: len(out) - o]
    return out


def sparkle():
    out = np.zeros(int(SR * 0.9))
    for i, f in enumerate([2093, 2637, 3136, 2637, 3520]):
        x = ding(f, 0.5, 0.07)
        o = int(SR * 0.07 * i)
        out[o:o + len(x)] += x
    return out


# (tempo em s, som, ganho, pan -1..1)
CUES = [
    # 1. gancho
    (0.1, pop(480), 0.8, 0), (0.4, pop(380), 1.0, 0), (0.8, whoosh(0.3, False), 0.4, 0), (1.2, rattle(2.4), 0.55, 0),
    (2.4, pop(500), 0.8, 0), (2.8, ding(1175, 0.6, 0.25), 1.0, 0), (4.15, whoosh(0.5), 0.8, 0),
    # 2. Nº 1
    (4.55, pop(520), 0.7, 0), (5.3, thud(), 0.9, 0), (5.35, sparkle(), 0.9, 0), (5.6, pop(460), 0.8, 0), (6.0, pop(400), 0.8, 0),
    (8.15, whoosh(0.5), 0.8, 0),
    # 3. antes x depois
    (8.55, pop(520), 0.6, 0), (8.8, whoosh(0.35, False), 0.6, -0.5), (9.5, whoosh(0.35, False), 0.6, 0.5), (10.2, thud(), 0.8, 0),
    (11.1, sparkle(), 0.8, 0.4), (13.65, whoosh(0.5), 0.8, 0),
]
for k in range(4):
    CUES.append((10.9 + k * 0.12, click(2000), 0.6, 0.3))
# 4. comparativos
for i in range(4):
    a = 14 + i * 3.5
    CUES += [(a + 0.02, pop(560), 0.6, 0), (a + 0.35, whoosh(0.3, False), 0.45, -0.4), (a + 0.58, nope(), 0.8, 0),
             (a + 1.2, whoosh(0.3, False), 0.45, 0.4), (a + 1.47, ding(1320, 0.6, 0.28), 1.0, 0)]
    if i < 3:
        CUES.append((a + 3.15, whoosh(0.4), 0.55, 0))
CUES += [(27.65, whoosh(0.5), 0.8, 0)]
# 5. montagem do protocolo
for k in range(4):
    CUES.append((29.05 + k * 0.45, click(), 0.9, -0.45 + k * 0.3))
CUES += [(31.3, whoosh(0.55, False), 0.6, 0), (31.9, thud(), 0.7, 0)]
for k in range(4):
    CUES.append((31.95 + k * 0.12, click(1800), 0.75, -0.45 + k * 0.3))
CUES += [(32.6, pop(480), 0.7, 0), (32.8, sparkle(), 1.0, 0), (35.15, whoosh(0.5), 0.8, 0)]
# 6. implante unitário
CUES += [(35.55, pop(520), 0.6, 0), (35.9, pop(420), 0.8, 0), (36.33, click(), 0.9, 0),
         (36.99, thud(), 0.5, 0), (37.0, click(1600), 0.8, 0), (37.4, sparkle(), 0.9, 0), (37.5, pop(500), 0.6, 0)]
# CTA
CUES += [(38.95, whoosh(0.8), 1.0, 0), (39.7, chime(), 1.0, 0), (40.2, pop(560), 0.6, 0), (40.5, pop(480), 0.7, 0),
         (40.8, pop(400), 0.8, 0), (41.3, pop(440), 0.8, 0), (41.9, pop(520), 0.6, 0), (42.3, pop(600), 0.6, 0), (42.7, pop(640), 0.5, 0)]

mix = np.zeros((int(SR * DUR), 2))
for t0, snd, g, pan in CUES:
    o = int(SR * t0)
    x = snd[: len(mix) - o] * g
    mix[o:o + len(x), 0] += x * np.sqrt((1 - pan) / 2) * np.sqrt(2)
    mix[o:o + len(x), 1] += x * np.sqrt((1 + pan) / 2) * np.sqrt(2)

mix *= 10 ** (-6 / 20) / np.max(np.abs(mix))  # pico em -6 dBFS: presente, mas sem exagero
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else "sfx.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("ok")
