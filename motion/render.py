"""Motion design 15s — Mercado financeiro 26/10/2026 x Terra.
Gera frames (PIL), efeitos sonoros sintetizados (numpy) e junta com ffmpeg.
Uso: python3 render.py  ->  out/mercado_terra_15s.mp4
"""
import math, os, subprocess, wave
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 15.0
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FRAMES = os.path.join(OUT, "frames")

# Paleta — troque aqui pelos hex da sua paleta
BG = (0, 0, 0)
RED = (255, 45, 45)
GREEN = (0, 214, 110)
WHITE = (255, 255, 255)
GRAY = (140, 140, 140)
DARK = (22, 22, 22)

FD = "/usr/share/fonts/opentype/inter/"
_fc = {}
def F(size, w="Black"):
    k = (size, w)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(f"{FD}Inter-{w}.otf", size)
    return _fc[k]

SOURCE = "Fontes: InfoMoney, SpaceMoney, Gazeta Brasil · 26/10/2026"

# ---------- easing ----------
def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def p(t, a, b): return cl((t - a) / (b - a)) if b > a else float(t >= a)
def eo(x): return 1 - (1 - x) ** 3
def eio(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eback(x, s=1.8): x -= 1; return x * x * ((s + 1) * x + s) + 1
def col(c, a): return (c[0], c[1], c[2], int(255 * cl(a)))
def mix(c1, c2, k): return tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))

def text(d, xy, s, f, c, a=1.0, anchor="mm"):
    if a > 0: d.text(xy, s, font=f, fill=col(c, a), anchor=anchor)

def glow(img, xy, s, f, c, a=1.0, r=22, anchor="mm"):
    if a <= 0: return
    L = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(L).text(xy, s, font=f, fill=col(c, a * .9), anchor=anchor)
    img.paste(L.filter(ImageFilter.GaussianBlur(r)), (0, 0), L.filter(ImageFilter.GaussianBlur(r)))
    ImageDraw.Draw(img, "RGBA").text(xy, s, font=f, fill=col(c, a), anchor=anchor)

def slide_text(d, x, y, s, f, c, t, t0, dy=60, dur=.45):
    k = eo(p(t, t0, t0 + dur))
    text(d, (x, y + dy * (1 - k)), s, f, c, k)

def tri(d, cx, cy, size, up, c, a=1.0):
    h = size
    pts = [(cx, cy - h / 2), (cx - h / 1.6, cy + h / 2), (cx + h / 1.6, cy + h / 2)] if up else \
          [(cx, cy + h / 2), (cx - h / 1.6, cy - h / 2), (cx + h / 1.6, cy - h / 2)]
    d.polygon(pts, fill=col(c, a))

def label(d, y, s, c, a):
    f = F(40, "Bold")
    w = d.textlength(s, font=f) + 60
    d.rounded_rectangle([W / 2 - w / 2, y - 34, W / 2 + w / 2, y + 34], 34, outline=col(c, a), width=3)
    text(d, (W / 2, y), s, f, c, a)

def footnote(d, a):
    text(d, (W / 2, 1800), SOURCE, F(28, "Medium"), GRAY, a * .8)

def background(d, t):
    for x in range(0, W + 1, 90):
        d.line([(x, 0), (x, H)], fill=DARK, width=1)
    for y in range(0, H + 1, 90):
        d.line([(0, y), (W, y)], fill=DARK, width=1)

# ---------- cenas (tempo local) ----------
def s_intro(img, d, t, dur):
    text(d, (W / 2, 470), "26 · 10 · 2026", F(44, "SemiBold"), GRAY, p(t, .05, .3))
    for i, w in enumerate(["MERCADO", "FINANCEIRO", "HOJE"]):
        slide_text(d, W / 2, 640 + i * 165, w, F(140), WHITE if i < 2 else RED, t, .15 + i * .18)
    # faixa ticker vermelha
    k = eo(p(t, .6, .9))
    y = 1260
    d.rectangle([0, y - 55, W * k, y + 55], fill=col(RED, 1))
    items = "DÓLAR ▲ 12%   ·   IBOVESPA DESPENCA   ·   CIRCUIT BREAKER   ·   LEILÕES CANCELADOS   ·   "
    f = F(50, "ExtraBold")
    tw = d.textlength(items, font=f)
    off = -(t * 520) % tw
    if k > .95:
        for n in range(-1, 3):
            text(d, (off + n * tw - tw, y), items, f, BG, 1, "lm")
    # pulso de alerta
    if t > .9:
        a = .5 + .5 * math.sin(t * 18)
        d.ellipse([W / 2 - 14, 1460 - 14, W / 2 + 14, 1460 + 14], fill=col(RED, a))
        text(d, (W / 2, 1530), "ALERTA NO MERCADO", F(40, "Bold"), RED, p(t, .9, 1.1))

def s_dolar(img, d, t, dur):
    label(d, 330, "DÓLAR  US$ / R$", RED, p(t, 0, .25))
    k = eo(p(t, .2, 1.7))
    pct = 12 * k
    a = p(t, .15, .35)
    tri(d, 250, 520, 70, True, RED, a)
    glow(img, (600, 520), f"+{pct:.0f}%", F(190), RED, a)
    d = ImageDraw.Draw(img, "RGBA")
    ka = eback(p(t, 1.7, 2.0))
    if t > 1.7:
        f = F(int(120 * (0.6 + 0.4 * ka)))
        text(d, (W / 2, 720), "R$ 5,60", f, WHITE, p(t, 1.7, 1.85))
    # gráfico de barras: fechamento anterior = 100, hoje = 112 (+12%)
    base, hmax, bw = 1450, 560, 230
    h1 = hmax / 1.12 * eo(p(t, .3, .9))
    h2 = hmax / 1.12 * (1 + .12 * k) * eo(p(t, .3, .9))
    d.line([(150, base), (W - 150, base)], fill=col(GRAY, .7), width=3)
    x1, x2 = 380, 700
    d.rectangle([x1 - bw / 2, base - h1, x1 + bw / 2, base], fill=col((70, 70, 70), 1))
    d.rectangle([x2 - bw / 2, base - h2, x2 + bw / 2, base], fill=col(RED, 1))
    # linha tracejada mostrando o nível anterior
    if t > .9:
        for xx in range(x1 - bw // 2, x2 + bw // 2, 26):
            d.line([(xx, base - h1), (xx + 13, base - h1)], fill=col(WHITE, .5), width=3)
    text(d, (x1, base + 50), "fechamento", F(38, "SemiBold"), GRAY, p(t, .5, .8))
    text(d, (x1, base + 95), "anterior", F(38, "SemiBold"), GRAY, p(t, .5, .8))
    text(d, (x2, base + 50), "hoje", F(38, "Bold"), RED, p(t, .5, .8))
    text(d, (x2, base - h2 - 45), f"+{pct:.0f}%", F(48, "ExtraBold"), RED, p(t, .5, .8))
    footnote(d, p(t, .4, .7))

def s_ibov(img, d, t, dur):
    label(d, 330, "IBOVESPA · B3", RED, p(t, 0, .25))
    # seta despencando
    k = eo(p(t, .1, .6))
    y = 430 + 150 * k
    a = p(t, .1, .3)
    d.rectangle([W / 2 - 38, 430, W / 2 + 38, y], fill=col(RED, a))
    tri(d, W / 2, y + 60, 130, False, RED, a)
    slide_text(d, W / 2, 860, "DESPENCA", F(150), RED, t, .35, dy=-60)
    # banner circuit breaker piscando
    if t > .75:
        on = (int((t - .75) * 6) % 2 == 0) or t > 1.6
        kb = eo(p(t, .75, .95))
        bh = 95 * kb
        d.rectangle([60, 1080 - bh, W - 60, 1080 + bh], fill=col(RED if on else (120, 15, 15), 1))
        text(d, (W / 2, 1080), "CIRCUIT BREAKER", F(96), BG, kb)
    # pausa
    a2 = p(t, 1.3, 1.55)
    cx = 300
    d.rounded_rectangle([cx - 30, 1290, cx - 8, 1360], 5, fill=col(WHITE, a2))
    d.rounded_rectangle([cx + 8, 1290, cx + 30, 1360], 5, fill=col(WHITE, a2))
    text(d, (cx + 70, 1325), "pregão interrompido", F(54, "Bold"), WHITE, a2, "lm")
    slide_text(d, W / 2, 1490, "1ª vez desde a pandemia", F(56, "ExtraBold"), WHITE, t, 1.5, dy=30)
    slide_text(d, W / 2, 1560, "(março de 2020)", F(44, "SemiBold"), GRAY, t, 1.6, dy=30)
    footnote(d, p(t, .4, .7))

def doc(img, cx, cy, a, tag):
    d = ImageDraw.Draw(img, "RGBA")
    w, h = 230, 300
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 18, fill=col((18, 18, 18), a), outline=col(WHITE, a * .9), width=4)
    text(d, (cx, cy - 95), tag, F(30, "ExtraBold"), WHITE, a)
    for i in range(5):
        ww = w - 70 if i % 2 == 0 else w - 110
        d.rounded_rectangle([cx - ww / 2, cy - 40 + i * 38, cx + ww / 2, cy - 28 + i * 38], 6, fill=col(GRAY, a * .6))

def s_tesouro(img, d, t, dur):
    label(d, 330, "TESOURO NACIONAL", RED, p(t, 0, .25))
    slide_text(d, W / 2, 470, "LEILÕES DE", F(80), WHITE, t, .1)
    slide_text(d, W / 2, 560, "TÍTULOS", F(80), WHITE, t, .2)
    for i, (cx, tag) in enumerate([(240, "PREFIXADO"), (540, "IPCA+"), (840, "PREFIXADO")]):
        k = eo(p(t, .25 + i * .12, .6 + i * .12))
        doc(img, cx, 870 + 80 * (1 - k), k, tag)
    d = ImageDraw.Draw(img, "RGBA")
    # carimbo
    ts = .95
    if t > ts:
        k = eo(p(t, ts, ts + .18))
        sc = 2.2 - 1.2 * k
        L = Image.new("RGBA", (900, 220), (0, 0, 0, 0))
        ld = ImageDraw.Draw(L)
        ld.rounded_rectangle([10, 10, 890, 210], 24, outline=col(RED, 1), width=14, fill=(0, 0, 0, 170))
        ld.text((450, 112), "CANCELADOS", font=F(130), fill=col(RED, 1), anchor="mm")
        L = L.resize((int(900 * sc), int(220 * sc))).rotate(-10, expand=True, resample=Image.BICUBIC)
        if k < 1:
            alpha = L.split()[3].point(lambda v: int(v * k))
            L.putalpha(alpha)
        img.paste(L, (int(W / 2 - L.width / 2), int(880 - L.height / 2)), L)
        d = ImageDraw.Draw(img, "RGBA")
    slide_text(d, W / 2, 1230, "prefixados e atrelados à inflação", F(48, "Bold"), WHITE, t, 1.2, dy=30)
    slide_text(d, W / 2, 1300, "previstos para 27 e 29 de outubro", F(48, "Bold"), GRAY, t, 1.3, dy=30)
    footnote(d, p(t, .4, .7))

def s_moeda(img, d, t, dur):
    slide_text(d, W / 2, 470, "Quando a moeda", F(92, "ExtraBold"), WHITE, t, 0)
    slide_text(d, W / 2, 575, "perde valor,", F(92, "ExtraBold"), WHITE, t, .1)
    # cédula encolhendo e ficando vermelha (ilustração)
    k = eio(p(t, .5, 1.6))
    a = p(t, .2, .4)
    c = mix(GREEN, RED, k)
    sc = 1 - .3 * k
    cx, cy = W / 2, 900 + 60 * k
    bw, bh = 520 * sc, 250 * sc
    L = Image.new("RGBA", (700, 400), (0, 0, 0, 0))
    ld = ImageDraw.Draw(L)
    ld.rounded_rectangle([350 - bw / 2, 200 - bh / 2, 350 + bw / 2, 200 + bh / 2], 20, outline=col(c, a), width=8)
    ld.ellipse([350 - 70 * sc, 200 - 70 * sc, 350 + 70 * sc, 200 + 70 * sc], outline=col(c, a), width=6)
    ld.text((350, 200), "R$", font=F(int(70 * sc)), fill=col(c, a), anchor="mm")
    L = L.rotate(-14 * k, resample=Image.BICUBIC)
    img.paste(L, (int(cx - 350), int(cy - 200)), L)
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(3):
        kk = p(t, .7 + i * .15, 1.3 + i * .15)
        if 0 < kk < 1:
            tri(d, cx - 260 + i * 260, 1100 + 120 * kk, 40, False, RED, 1 - kk)
    slide_text(d, W / 2, 1360, "quem tem dinheiro parado", F(70, "ExtraBold"), RED, t, 1.0)
    glow(img, (W / 2, 1460), "perde junto.", F(110), RED, eo(p(t, 1.2, 1.5)), r=18)

def s_terra(img, d, t, dur):
    # varredura verde de transição
    k = eio(p(t, 0, .35))
    if k < 1:
        d.rectangle([0, H * (1 - k) - 40, W, H * (1 - k) + 40], fill=col(GREEN, 1 - k))
    slide_text(d, W / 2, 380, "Terra é diferente.", F(66, "ExtraBold"), WHITE, t, .1, dy=30)
    glow(img, (W / 2, 530), "TERRA", F(220), GREEN, eo(p(t, .15, .45)), r=26)
    d = ImageDraw.Draw(img, "RGBA")
    # ilustração: sol, horizonte e linhas de plantio em perspectiva
    a = p(t, .3, .55)
    hy, vx = 800, W / 2
    sk = eo(p(t, .3, .9))
    d.ellipse([vx + 160 - 55, hy - 60 - 110 * sk, vx + 160 + 55, hy + 50 - 110 * sk], outline=col(GREEN, a), width=6)
    d.line([(90, hy), (W - 90, hy)], fill=col(GREEN, a), width=5)
    rows = 9
    gk = eo(p(t, .35, .95))
    for i in range(rows):
        bx = 90 + (W - 180) * i / (rows - 1)
        ex = vx + (bx - vx) * .15
        d.line([(ex, hy), (ex + (bx - ex) * gk, hy + 270 * gk)], fill=col(GREEN, a * .85), width=4)
    d.line([(90, hy + 270), (W - 90, hy + 270)], fill=col(GREEN, a * gk), width=4)
    items = ["Bem físico e limitado", "Não depende de pregão", "Nem de câmbio", "Tende a acompanhar a inflação"]
    for i, s in enumerate(items):
        t0 = .55 + i * .22
        kk = eo(p(t, t0, t0 + .3))
        y = 1210 + i * 105
        x0 = 150 + 40 * (1 - kk)
        d.ellipse([x0 - 30, y - 30, x0 + 30, y + 30], fill=col(GREEN, kk))
        d.line([(x0 - 14, y), (x0 - 3, y + 12), (x0 + 16, y - 12)], fill=col(BG, kk), width=7)
        text(d, (x0 + 60, y), s, F(52, "Bold"), WHITE, kk, "lm")
    text(d, (W / 2, 1680), "Uma das formas mais antigas de proteger patrimônio.", F(34, "SemiBold"), GRAY, p(t, 1.4, 1.7))

def s_contato(img, d, t, dur):
    k = eo(p(t, 0, .4))
    d.line([(W / 2 - 300 * k, 760), (W / 2 + 300 * k, 760)], fill=col(GREEN, 1), width=6)
    slide_text(d, W / 2, 880, "Pedro Bolivar", F(118), WHITE, t, .1)
    glow(img, (W / 2, 1030), "(15) 99661-2946", F(84, "ExtraBold"), GREEN, eo(p(t, .25, .55)), r=16)
    d = ImageDraw.Draw(img, "RGBA")
    slide_text(d, W / 2, 1140, "CRECI 266.761-F", F(52, "SemiBold"), GRAY, t, .4, dy=30)
    d.line([(W / 2 - 300 * k, 1230), (W / 2 + 300 * k, 1230)], fill=col(GREEN, 1), width=6)
    text(d, (W / 2, 1340), "Proteja seu patrimônio com terra.", F(46, "Bold"), GREEN, p(t, .6, .9))

SCENES = [(0.0, 2.0, s_intro), (2.0, 5.0, s_dolar), (5.0, 7.5, s_ibov), (7.5, 9.6, s_tesouro),
          (9.6, 11.6, s_moeda), (11.6, 13.7, s_terra), (13.7, 15.0, s_contato)]
IMPACTS = [2.0 + 1.7, 5.0 + .8, 7.5 + 1.13]  # tremor de câmera

def frame(i):
    t = i / FPS
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    background(d, t)
    for a, b, fn in SCENES:
        if a <= t < b or (fn is s_contato and t >= a):
            lt, dur = t - a, b - a
            layer = Image.new("RGB", (W, H), BG)
            ld = ImageDraw.Draw(layer, "RGBA")
            background(ld, t)
            fn(layer, ld, lt, dur)
            fade = min(p(lt, 0, .12), 1 - p(lt, dur - .12, dur)) if fn is not s_contato else p(lt, 0, .12)
            img = Image.blend(img, layer, fade)
    for ti in IMPACTS:
        if ti <= t < ti + .25:
            amp = 18 * (1 - (t - ti) / .25)
            dx, dy = amp * math.sin(t * 90), amp * math.cos(t * 70)
            img = img.transform(img.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), fillcolor=BG)
    img.save(os.path.join(FRAMES, f"{i:04d}.png"), compress_level=1)

# ---------- efeitos sonoros ----------
SR = 48000
def env(n, att, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(att, 1e-4)) * np.exp(-t / dec)
def lowpass(x, cut):
    cut = np.broadcast_to(cut, x.shape)
    y = np.zeros_like(x); s = 0.0
    a = 1 - np.exp(-2 * np.pi * cut / SR)
    for i in range(len(x)):
        s += a[i] * (x[i] - s); y[i] = s
    return y
def whoosh(dur=.5, f0=300, f1=4000):
    n = int(SR * dur); tt = np.linspace(0, 1, n)
    x = np.random.randn(n)
    shape = np.sin(np.pi * tt) ** 2
    return lowpass(x, f0 + (f1 - f0) * shape) * shape * 1.6
def impact(f=55, dur=.6):
    n = int(SR * dur); tt = np.arange(n) / SR
    body = np.sin(2 * np.pi * (f + 60 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 7)
    click = lowpass(np.random.randn(n), 3000) * np.exp(-tt * 60)
    return body * .9 + click * .8
def tick(f=2200):
    n = int(SR * .03); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * f * tt) * np.exp(-tt * 180) * .5
def sweep(f0, f1, dur, vol=.25):
    n = int(SR * dur); tt = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (tt / dur)) / SR
    return (np.sin(ph) + .3 * np.sin(2 * ph)) * np.minimum(1, tt / .05) * np.minimum(1, (dur - tt) / .08) * vol
def beep(f, dur=.14, vol=.3):
    n = int(SR * dur); tt = np.arange(n) / SR
    sq = np.sign(np.sin(2 * np.pi * f * tt))
    return lowpass(sq, 4000) * np.minimum(1, (dur - tt) / .01) * np.minimum(1, tt / .005) * vol
def chime(freqs, dur=1.2, vol=.22):
    n = int(SR * dur); tt = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * (3 + k)) for k, f in enumerate(freqs)) * vol * np.minimum(1, tt / .005)
def glitch(dur=.35):
    n = int(SR * dur); out = np.zeros(n)
    for _ in range(12):
        s = np.random.randint(0, n - 2000); l = np.random.randint(300, 2000)
        out[s:s + l] = np.sign(np.sin(2 * np.pi * np.random.randint(200, 3000) * np.arange(l) / SR)) * .18
    return lowpass(out, 6000)
def paper():
    return lowpass(np.random.randn(int(SR * .18)), 5000) * env(int(SR * .18), .02, .05) * .5

def audio(path):
    np.random.seed(7)
    buf = np.zeros(int(SR * DUR) + SR)
    def add(t, x, v=1.0):
        s = int(t * SR); buf[s:s + len(x)] += x * v
    # intro
    add(0.0, glitch(), .9); add(0.05, whoosh(.45), .5)
    for i in range(3): add(.2 + i * .18, impact(70, .35), .45)
    add(.65, whoosh(.3, 800, 6000), .4)
    for i in range(4): add(1.0 + i * .25, beep(1200, .06, .12))
    # dólar
    add(1.85, whoosh(.5), .6); add(2.2, sweep(220, 880, 1.5, .18))
    for i in range(12): add(2.2 + i * .125, tick(1800 + i * 80), .8)
    add(3.7, impact(48, .9), 1.0); add(3.7, chime([300, 450], .5, .12))
    # ibovespa
    add(4.85, whoosh(.5, 3000, 300), .6); add(5.1, sweep(700, 120, .7, .2)); add(5.8, impact(40, .9), 1.0)
    for i in range(5): add(5.8 + i * .3, beep(880 if i % 2 == 0 else 660, .2, .22))
    # tesouro
    add(7.35, whoosh(.45), .55)
    for i in range(3): add(7.75 + i * .12, paper(), .9)
    add(8.63, impact(60, .7), 1.0); add(8.63, lowpass(np.random.randn(int(SR * .12)), 2500) * env(int(SR * .12), .001, .03), 1.2)
    # moeda
    add(9.45, whoosh(.45, 200, 2000), .45); add(10.1, sweep(500, 180, 1.1, .16)); add(10.85, impact(45, .6), .6)
    # terra (positivo)
    add(11.5, whoosh(.5, 600, 7000), .55); add(11.7, chime([523.25, 659.25, 783.99, 1046.5], 1.6, .2))
    for i in range(4): add(12.2 + i * .22, chime([1046.5 + i * 130], .3, .18))
    # contato
    add(13.6, whoosh(.4, 400, 5000), .4); add(13.85, chime([783.99, 1174.66, 1567.98], 1.3, .2))
    buf = buf[:int(SR * DUR)]
    buf = np.tanh(buf * 1.2) * .8
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((buf * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    os.makedirs(FRAMES, exist_ok=True)
    wav = os.path.join(OUT, "sfx.wav")
    audio(wav)
    with Pool() as pool:
        pool.map(frame, range(int(FPS * DUR)))
    mp4 = os.path.join(OUT, "mercado_terra_15s.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(FRAMES, "%04d.png"),
                    "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4], check=True)
    print(mp4)
