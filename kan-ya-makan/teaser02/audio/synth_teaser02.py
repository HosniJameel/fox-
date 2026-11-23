"""
كان يا مكان — Teaser 02 «من الورق للواقع» · procedural score + sound design
8.000 s · 48 kHz · 24-bit stereo · cues locked to 240 frames @ 30 fps.
Outputs in ./out: Background_Music.wav, Sound_Design.wav, Final_Mix.wav, cue_sheet.tsv
Everything is synthesised here; no samples or library audio.
"""
import os, sys, wave, json
import numpy as np
from scipy import signal
from scipy.ndimage import minimum_filter1d

SR, DUR = 48000, 8.0
N = int(SR * DUR)
rng = np.random.default_rng(2402)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)

# ---- sync table (frames @ 30 fps), tuned to the generated footage ----------
SYNC = {
    "cut_paper_to_craft": 90,     # match cut
    "pencil_start": 93,           # graphite touches the oak
    "pencil_end": 146,            # stroke ends (or the cut)
    "cut_craft_to_detail": 150,
    "slogan_in": 178,
    "logo_in": 204,
}
cfg = os.path.join(HERE, "sync.json")
if os.path.exists(cfg):
    SYNC.update(json.load(open(cfg)))

def T(f): return f / 30.0
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12.0)
def db(x): return 10 ** (x / 20.0)
def blank(): return np.zeros((N, 2))
def pan(x, p):
    a = (np.asarray(p) + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1)
def add(bus, st, t0):
    i = int(round(t0 * SR))
    if i < 0: st = st[-i:]; i = 0
    j = min(N, i + len(st))
    if j > i: bus[i:j] += st[:j - i]
def env(points, n, t0=0.0):
    t = t0 + np.arange(n) / SR
    xs = np.array([p[0] for p in points]); ys = np.array([p[1] for p in points])
    idx = np.clip(np.searchsorted(xs, t) - 1, 0, len(xs) - 2)
    u = np.clip((t - xs[idx]) / np.maximum(xs[idx + 1] - xs[idx], 1e-9), 0, 1)
    u = 0.5 - 0.5 * np.cos(np.pi * u)
    out = ys[idx] + (ys[idx + 1] - ys[idx]) * u
    out[t < xs[0]] = ys[0]; out[t > xs[-1]] = ys[-1]
    return out
def filt(x, kind, fc, order=2):
    return signal.sosfilt(signal.butter(order, fc, kind, fs=SR, output="sos"), x, axis=0)
def svf(x, fc, q=0.8):
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    g = np.tan(np.pi * np.clip(fc, 20, SR * 0.45) / SR); k = 1 / q
    a1 = 1 / (1 + g * (g + k)); a2 = g * a1; a3 = g * a2
    ic1 = ic2 = 0.0; y = np.empty_like(x)
    for i in range(len(x)):
        v3 = x[i] - ic2; v1 = a1[i] * ic1 + a2[i] * v3; v2 = ic2 + a2[i] * ic1 + a3[i] * v3
        ic1 = 2 * v1 - ic1; ic2 = 2 * v2 - ic2; y[i] = v1
    return y
def noise(n): return rng.standard_normal(n)
def pink(n):
    w = np.fft.rfft(noise(n)); f = np.fft.rfftfreq(n, 1 / SR); f[0] = 1
    return np.fft.irfft(w / np.sqrt(f), n) * 30

def piano(midi, vel=0.4, dur=3.5):
    f0 = mtof(midi); n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for k in range(1, 14):
        fk = k * f0 * np.sqrt(1 + 0.00032 * k * k)
        if fk > 15000: break
        amp = (1 / k ** 1.35) * (0.55 + 0.45 * vel) ** (k * 0.4)
        dec = (0.55 + 0.42 * k) * (f0 / 330) ** 0.35
        for c in (-0.9, 0.9):
            out += 0.5 * amp * np.exp(-dec * t) * np.sin(2 * np.pi * fk * 2 ** (c / 1200) * t + rng.uniform(0, 6.28))
    out *= 1 - np.exp(-t / 0.0025)
    out += filt(noise(n), "low", 2500) * np.exp(-t / 0.005) * 0.015 * vel
    return out * env([(0, 1), (dur - 0.4, 1), (dur, 0)], n) * vel

def oud(midi, vel=0.5, dur=1.0, bright=0.55, vibrato=0.0):
    f0 = mtof(midi); n = int(dur * SR); ex_len = int(SR / f0)
    ex = filt(noise(ex_len) * np.hanning(ex_len) ** 0.5, "low", 1200 + 5000 * bright)
    L = int(SR / f0) + 2052; line = np.zeros(L); out = np.zeros(n)
    damp = 0.996 - 0.004 * (1 - bright); last = 0.0; tt = np.arange(n) / SR
    vib = 1 + vibrato * np.sin(2 * np.pi * 5.6 * tt) * np.clip(tt / 0.35, 0, 1)
    for i in range(n):
        r = i - SR / (f0 * vib[i]); ri = int(np.floor(r)); fr = r - ri
        s = line[ri % L] + (line[(ri + 1) % L] - line[ri % L]) * fr
        y = damp * 0.5 * (s + last); last = s
        if i < ex_len: y += ex[i]
        line[i % L] = y; out[i] = y
    body = filt(out, "band", [180, 260], 1) * 0.6 + filt(out, "band", [420, 560], 1) * 0.35
    out = filt(out + body, "high", 85) * env([(0, 1), (dur - 0.15, 1), (dur, 0)], n)
    return out / (np.max(np.abs(out)) + 1e-9) * vel

def pad_chord(midis, n, cutoff=1250):
    t = np.arange(n) / SR; st = np.zeros((n, 2))
    for j, m in enumerate(midis):
        for i, c in enumerate((-6, 0, 6)):
            f = mtof(m) * 2 ** (c / 1200); s = np.zeros(n)
            for k in range(1, 9):
                if k * f > 5000: break
                s += np.sin(2 * np.pi * k * f * t + rng.uniform(0, 6.28)) / k ** 1.1
            st += pan(s, (-0.55, 0, 0.55)[i] * (1 if j % 2 else -1))
    return filt(st, "low", cutoff) / (len(midis) * 3)

def bell(midi, vel=0.2, dur=1.6):
    f0 = mtof(midi); n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for r, a, d in ((1, 1, 2.2), (2.76, 0.45, 4.5), (5.40, 0.22, 8), (8.93, 0.1, 12)):
        out += a * np.exp(-d * t) * np.sin(2 * np.pi * f0 * r * t)
    return out * (1 - np.exp(-t / 0.004)) * vel

def make_ir(rt=2.3, length=3.0, pre=0.022, seed=3):
    r = np.random.default_rng(seed); n = int(length * SR); t = np.arange(n) / SR; ir = np.zeros((n, 2))
    for c in range(2):
        ir[:, c] = 0.55 * filt(r.standard_normal(n), "low", 6000) * np.exp(-6.9 * t / rt) + \
                   0.9 * filt(r.standard_normal(n), "low", 900) * np.exp(-6.9 * t / (rt * 1.35))
    p = int(pre * SR); ir[:p] = 0; ir[p:p + 480] *= np.linspace(0, 1, 480)[:, None]
    return ir / np.sqrt(np.sum(ir ** 2) / 2)
def reverb(st, ir, wet):
    return st + np.stack([signal.fftconvolve(st[:, c], ir[:, c])[:N] for c in range(2)], 1) * wet

cues = []
def cue(stem, a, b, name, sync): cues.append((stem, int(a), int(b), name, sync))
S = SYNC

# =============================== MUSIC =====================================
music = blank()
for midis, pts, name, a, b, why in [
    ([50, 57, 62, 64, 65], [(0, 0), (1.8, 0.7), (2.9, 0.75), (3.15, 0)], "Pad · D minor add9 (the idea)", 0, 95, "paper scene"),
    ([50, 58, 62, 65, 69], [(2.9, 0), (3.2, 0.8), (4.8, 0.95), (5.1, 0)], "Pad · B♭ add9 lift (becoming real)", 87, 153, "the cut to the craftsman"),
    ([50, 57, 62, 66, 69], [(4.95, 0), (5.25, 0.9), (6.6, 0.85), (7.6, 0.55), (8.0, 0)], "Pad · D major (resolution)", 148, 240, "the reveal"),
]:
    music += pad_chord(midis, N) * env(pts, N)[:, None] * db(-14); cue("Music", a, b, name, why)
music += pan(np.sin(2 * np.pi * mtof(38) * np.arange(N) / SR), 0) * env([(0, 0), (2.0, 0.4), (3.2, 0.7), (7.2, 0.6), (8, 0)], N)[:, None] * db(-31)

for t0, m, v, name, fr, why in [
    (T(10), 74, 0.26, "Piano D5", 10, "paper settles in the light"), (T(40), 69, 0.22, "Piano A4", 40, "push-in"),
    (T(68), 77, 0.20, "Piano F5", 68, "approaching the words"),
    (T(150), 62, 0.22, "Piano chord D–F♯–A", 150, "cut to the crafted detail"), (T(150) + .02, 66, .2, None, 0, ""), (T(150) + .04, 69, .2, None, 0, ""),
    (T(S["logo_in"]), 50, 0.28, "Piano D3 + D2 under the logo", S["logo_in"], "logo"), (T(S["logo_in"]) + .01, 38, .2, None, 0, ""),
    (T(S["logo_in"] + 8), 86, 0.09, "Piano D6 air", S["logo_in"] + 8, "logo settles"),
]:
    add(music, pan(piano(m, v, min(3.5, DUR - t0 + .4)), .15 if m > 70 else -.1) * db(-8), t0)
    if name: cue("Music", fr, min(240, fr + 40), name, why)

# oud pulse while the craftsman works: gentle, under the tool sounds
ost = [(0, 62, .26), (7, 57, .22), (15, 62, .28), (22, 65, .26), (30, 64, .28), (37, 62, .3), (45, 57, .3), (52, 58, .32)]
for d, m, v in ost:
    add(music, pan(oud(m, v, .5, .45), -.2) * db(-14), T(S["cut_paper_to_craft"] + d))
cue("Music", S["cut_paper_to_craft"], S["cut_craft_to_detail"], "Oud pulse D–A–D–F–E–D–A–B♭", "the craftsman at work")
for fr, m, v, d in [(0, 69, .5, .55), (6, 67, .45, .5), (11, 66, .45, .5), (17, 63, .5, .55)]:
    add(music, pan(oud(m, v, d + .25, .55), -.2) * db(-10), T(S["slogan_in"] + fr))
add(music, pan(oud(62, .58, DUR - T(S["logo_in"]) , .55, vibrato=.0045), -.2) * db(-10), T(S["logo_in"]))
cue("Music", S["slogan_in"], 240, "Oud Hijaz descent A–G–F♯–E♭ → D", "slogan in, resolves on the logo")
lt = np.arange(N - int(T(S["logo_in"]) * SR)) / SR
add(music, pan((np.sin(2 * np.pi * mtof(38) * lt) + .25 * np.sin(2 * np.pi * mtof(50) * lt)) * (1 - np.exp(-lt / .35)), 0) * db(-25), T(S["logo_in"]))
cue("Music", S["logo_in"], 240, "Warm low D tone", "logo")

# ============================ SOUND DESIGN ==================================
sfx = blank()
c1 = S["cut_paper_to_craft"]
study = filt(pink(N), "low", 500) * db(-12)
shop = filt(pink(N), "band", [90, 1800]) * db(-9) + filt(noise(N), "band", [3000, 8000]) * db(-34)
sfx += pan(study, 0) * env([(0, 0), (.4, 1), (T(c1) - .05, 1), (T(c1) + .1, 0)], N)[:, None] * db(-27)
sfx += pan(shop, 0) * env([(T(c1) - .1, 0), (T(c1) + .08, 1), (7.4, .9), (8, 0)], N)[:, None] * db(-26)
cue("SFX", 0, c1, "Quiet study room tone", "paper scene"); cue("SFX", c1, 240, "Workshop ambience (soft, wide)", "the real space")

def paper_flex(dur, p, lvl, t0):
    n = int(dur * SR); x = np.zeros(n)
    for _ in range(int(dur * 40)):
        i = rng.integers(0, n - 1800); ln = rng.integers(300, 1500)
        x[i:i + ln] += noise(ln) * np.hanning(ln) * rng.uniform(.2, 1)
    x = filt(x, "band", [1500, 7500]) * env([(0, 0), (dur * .2, 1), (dur, 0)], n)
    add(sfx, pan(x, p) * db(lvl), t0)
paper_flex(.55, .1, -25, T(3)); paper_flex(.45, -.1, -28, T(44))
cue("SFX", 3, 60, "Paper movement texture ×2", "the sheet in the light, the push-in")

n = int(T(30) * SR); tt = np.arange(n) / SR
add(sfx, pan(np.sin(2 * np.pi * mtof(50) * tt) * env([(0, 0), (.9, 1), (T(30), 0)], n), 0) * db(-36), 0)
cue("SFX", 0, 30, "Intro tone (very low D)", "opening")

# transition into reality: reverse swell + tonal air, peak on the cut
n = int(.5 * SR); tt = np.arange(n) / SR
src = filt(noise(n), "band", [500, 3500]) * np.exp(-tt / .05) + .5 * np.sin(2 * np.pi * mtof(74) * tt) * np.exp(-tt / .1)
tail = signal.fftconvolve(src, make_ir(1.0, .5, seed=9)[:, 0])[:n][::-1]
add(sfx, pan(tail / np.max(np.abs(tail)) * env([(0, 0), (.42, 1), (.49, 1), (.5, 0)], n), 0) * db(-18), T(c1) - .5)
n = int(.45 * SR); tt = np.arange(n) / SR
air = svf(noise(n), 2500 * np.exp(-tt * 3) + 400, q=1.1) * env([(0, 1), (.08, .8), (.45, 0)], n)
add(sfx, pan(air, np.linspace(.2, -.2, n)) * db(-19), T(c1))
cue("SFX", c1 - 15, c1 + 13, "Reverse swell → tonal air", "the match cut paper → oak")

# graphite on oak, along the steel ruler (follows the visible stroke)
a, b = T(S["pencil_start"]), T(S["pencil_end"])
n = int((b - a) * SR); tt = np.arange(n) / SR
grain = noise(n) * (.6 + .4 * np.abs(np.sin(2 * np.pi * 37 * tt + rng.uniform(0, 6))))
scr = svf(grain, 3200 + 600 * np.sin(2 * np.pi * .9 * tt), q=1.6) + filt(noise(n), "band", [700, 1600]) * .25
scr *= env([(0, 0), (.04, 1), ((b - a) * .7, .85), (b - a, 0)], n)
add(sfx, pan(scr, .05) * db(-20), a)
n = int(.2 * SR); tt = np.arange(n) / SR
tick = filt(noise(n), "band", [2500, 6000]) * np.exp(-tt / .004) + sum(A * np.sin(2 * np.pi * f * tt) * np.exp(-tt / d) for f, A, d in ((1900, .4, .05), (3400, .25, .03)))
add(sfx, pan(tick, .1) * db(-23), a - .02)
cue("SFX", S["pencil_start"], S["pencil_end"], "Graphite on oak + steel-ruler tick", "the pencil line")

c2 = S["cut_craft_to_detail"]
n = int(.4 * SR); tt = np.arange(n) / SR
add(sfx, pan(svf(noise(n), 900 + 1200 * np.exp(-tt * 5), q=.9) * env([(0, 0), (.05, 1), (.4, 0)], n), 0) * db(-30), T(c2) - .05)
n = int(.6 * SR); tt = np.arange(n) / SR
knock = sum(A * np.sin(2 * np.pi * f * tt) * np.exp(-tt / d) for f, A, d in ((160, 1, .07), (380, .6, .05), (900, .25, .03))) + filt(noise(n), "band", [1500, 5000]) * np.exp(-tt / .003) * .5
add(sfx, pan(knock, -.15) * db(-22), T(c2))
cue("SFX", c2, c2 + 12, "Soft air + gentle wood resonance", "cut to the crafted detail")

n = int((DUR - T(S["slogan_in"])) * SR); tt = np.arange(n) / SR; sh = np.zeros(n)
for m in (86, 90, 93, 98):
    sh += np.sin(2 * np.pi * mtof(m) * tt + rng.uniform(0, 6)) * (.6 + .4 * np.sin(2 * np.pi * rng.uniform(4, 7) * tt))
add(sfx, pan(sh * env([(0, 0), (.45, 1), (1.2, .5), (n / SR, 0)], n), .1) * db(-42), T(S["slogan_in"]))
add(sfx, pan(bell(86, 1, 1.6) + .5 * bell(93, 1, 1.6), -.1) * db(-31), T(S["logo_in"]))
cue("SFX", S["slogan_in"], 240, "Warm tonal shimmer", "slogan rises in")
cue("SFX", S["logo_in"], 240, "Soft bell accent D6/A6", "logo")

# ============================ BUS + MASTER ==================================
music = reverb(filt(music, "high", 32), make_ir(2.4, 3.0, seed=4), .32)
sfx = reverb(filt(sfx, "high", 32), make_ir(1.4, 2.0, seed=5), .14)
fade = env([(0, 1), (7.55, 1), (7.985, 0)], N)[:, None]; music *= fade; sfx *= fade

def lufs(x):
    hs = np.array([[1.53512485958697, -2.69169618940638, 1.19839281085285, 1, -1.69065929318241, .73248077421585]])
    hp = np.array([[1., -2., 1., 1, -1.99004745483398, .99007225036621]])
    y = signal.sosfilt(hp, signal.sosfilt(hs, x, axis=0), axis=0)
    blk, hop = int(.4 * SR), int(.1 * SR)
    ms = np.array([np.mean(np.sum(y[i:i + blk] ** 2, 1)) for i in range(0, len(y) - blk + 1, hop)])
    l = -.691 + 10 * np.log10(ms + 1e-12); g = ms[l > -70]
    rel = -.691 + 10 * np.log10(np.mean(g)) - 10
    return -.691 + 10 * np.log10(np.mean(ms[(l > -70) & (l > rel)]))
def tp_gain(x, ceiling=-1.3):
    up = signal.resample_poly(x, 4, 1, axis=0)
    pk = np.max(np.abs(up), 1).reshape(-1, 4).max(1)[:len(x)]
    need = minimum_filter1d(np.minimum(1, db(ceiling) / np.maximum(pk, 1e-9)), size=2 * int(.003 * SR) + 1)
    g = np.empty_like(need); cur = 1.0; rel = np.exp(-1 / (.09 * SR))
    for i in range(len(need)):
        cur = need[i] if need[i] < cur else need[i] + (cur - need[i]) * rel; g[i] = cur
    return signal.filtfilt(*signal.butter(1, 400, fs=SR), g)

mix = music + sfx; gain = 1.0; genv = np.ones(N)
for _ in range(6):
    gain *= db(-14 - lufs(mix * gain * genv[:, None])); genv = tp_gain(mix * gain)
def write24(path, x):
    x = np.clip(x + (rng.random(x.shape) - rng.random(x.shape)) / 2 ** 23, -1, 1 - 2 ** -23)
    q = np.round(x * (2 ** 23 - 1)).astype("<i4")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR); w.writeframes(q.view(np.uint8).reshape(-1, 4)[:, :3].tobytes())
G = gain * genv[:, None]
write24(os.path.join(OUT, "Background_Music.wav"), music * G)
write24(os.path.join(OUT, "Sound_Design.wav"), sfx * G)
write24(os.path.join(OUT, "Final_Mix.wav"), (music + sfx) * G)
with open(os.path.join(OUT, "cue_sheet.tsv"), "w", encoding="utf-8") as fh:
    fh.write("stem\tframe_in\tframe_out\ttc_in\ttc_out\telement\tsynced_to\n")
    tc = lambda f: f"00:0{f // 30}:{f % 30:02d}"
    for st, a, b, nm, why in sorted(cues, key=lambda c: (c[1], c[0])):
        fh.write(f"{st}\t{a}\t{b}\t{tc(a)}\t{tc(b)}\t{nm}\t{why}\n")
print("LUFS", round(lufs((music + sfx) * G), 2), "sync", SYNC)
