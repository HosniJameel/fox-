"""
كان يا مكان — Teaser 03 · procedural score + sound design
7.000 s · 48 kHz · 24-bit stereo · cues locked to the 30 fps animation frames.

Outputs (next to this file, in ./out):
  Background_Music.wav   music stem (mastered gain, same limiter envelope as the mix)
  Sound_Design.wav       SFX stem   (same)
  Final_Mix.wav          music + SFX, -14 LUFS integrated, <= -1 dBTP
  Kan_Ya_Makan_Final.wav identical copy of Final_Mix.wav
Everything is synthesised here (additive piano, Karplus-Strong oud, detuned pads,
filtered/granular noise, convolution reverb). No samples, no third-party audio.
Run:  python3 synth_kan_ya_makan.py
"""
import os, wave
import numpy as np
from scipy import signal

SR = 48000
DUR = 7.0
N = int(SR * DUR)
rng = np.random.default_rng(1977)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)


# ----------------------------------------------------------------- helpers
def T(frame):            # animation frame -> seconds
    return frame / 30.0

def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)

def db(x):
    return 10 ** (x / 20.0)

def blank():
    return np.zeros((N, 2))

def pan(x, p):           # equal-power, p in [-1, 1], p may be an array
    a = (np.asarray(p) + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1)

def add(bus, st, t0):
    i = int(round(t0 * SR))
    if i < 0:
        st = st[-i:]; i = 0
    j = min(N, i + len(st))
    if j > i:
        bus[i:j] += st[: j - i]

def env(points, n, t0=0.0):
    """points [(t_sec_absolute, gain)], cosine-interpolated, sampled for n samples from t0."""
    t = t0 + np.arange(n) / SR
    xs = np.array([p[0] for p in points]); ys = np.array([p[1] for p in points])
    idx = np.clip(np.searchsorted(xs, t) - 1, 0, len(xs) - 2)
    x0, x1 = xs[idx], xs[idx + 1]; y0, y1 = ys[idx], ys[idx + 1]
    u = np.clip((t - x0) / np.maximum(x1 - x0, 1e-9), 0, 1)
    u = 0.5 - 0.5 * np.cos(np.pi * u)
    out = y0 + (y1 - y0) * u
    out[t < xs[0]] = ys[0]; out[t > xs[-1]] = ys[-1]
    return out

def filt(x, kind, fc, order=2):
    sos = signal.butter(order, fc, kind, fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0)

def svf(x, fc, q=0.8, mode="band"):
    """TPT state-variable filter with per-sample cutoff (array or scalar)."""
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape)
    g = np.tan(np.pi * np.clip(fc, 20, SR * 0.45) / SR)
    k = 1.0 / q
    a1 = 1 / (1 + g * (g + k)); a2 = g * a1; a3 = g * a2
    ic1 = ic2 = 0.0
    y = np.empty_like(x)
    for i in range(len(x)):
        v3 = x[i] - ic2
        v1 = a1[i] * ic1 + a2[i] * v3
        v2 = ic2 + a2[i] * ic1 + a3[i] * v3
        ic1 = 2 * v1 - ic1; ic2 = 2 * v2 - ic2
        y[i] = v1 if mode == "band" else (v2 if mode == "low" else x[i] - k * v1 - v2)
    return y

def noise(n):
    return rng.standard_normal(n)

def pink(n):
    w = np.fft.rfft(noise(n)); f = np.fft.rfftfreq(n, 1 / SR); f[0] = 1
    return np.fft.irfft(w / np.sqrt(f), n) * 30

def speed_curve(f0, f1, kind="io", n=None, t_start=None):
    """|velocity| of the animation easing between frames f0..f1, normalised to 1 at peak."""
    t = (t_start if t_start is not None else T(f0)) + np.arange(n) / SR
    u = np.clip((t - T(f0)) / (T(f1) - T(f0)), 0, 1)
    if kind == "io":
        v = np.where(u < 0.5, 12 * u ** 2, 3 * (2 - 2 * u) ** 2)
    else:  # out (quartic ease-out)
        v = 4 * (1 - u) ** 3
    v[(t < T(f0)) | (t > T(f1))] = 0
    return v / v.max()


# ----------------------------------------------------------------- instruments
def piano(midi, vel=0.4, dur=3.5):
    f0 = mtof(midi); n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n); B = 0.00032
    for k in range(1, 14):
        fk = k * f0 * np.sqrt(1 + B * k * k)
        if fk > 15000:
            break
        amp = (1.0 / k ** 1.35) * (0.55 + 0.45 * vel) ** (k * 0.4)
        dec = (0.55 + 0.42 * k) * (f0 / 330) ** 0.35
        for cents in (-0.9, 0.9):
            out += 0.5 * amp * np.exp(-dec * t) * np.sin(2 * np.pi * fk * 2 ** (cents / 1200) * t + rng.uniform(0, 6.28))
    out *= 1 - np.exp(-t / 0.0025)
    out += filt(noise(n), "low", 2500) * np.exp(-t / 0.005) * 0.015 * vel
    out *= env([(0, 1), (dur - 0.4, 1), (dur, 0)], n)
    return out * vel

def oud(midi, vel=0.5, dur=1.2, bright=0.55, vibrato=0.0):
    """Karplus-Strong with fractional delay, risha-style excitation and a small wooden body."""
    f0 = mtof(midi); n = int(dur * SR)
    ex_len = int(SR / f0)
    ex = noise(ex_len) * np.hanning(ex_len) ** 0.5
    ex = filt(ex, "low", 1200 + 5000 * bright)
    buf_len = int(SR / f0) + 4
    line = np.zeros(buf_len + 2048)
    out = np.zeros(n)
    w = 0; damp = 0.996 - 0.004 * (1 - bright)
    last = 0.0
    tt = np.arange(n) / SR
    vib = 1 + vibrato * np.sin(2 * np.pi * 5.6 * tt) * np.clip(tt / 0.35, 0, 1)
    L = len(line)
    for i in range(n):
        d = SR / (f0 * vib[i])
        r = w - d
        ri = int(np.floor(r)); fr = r - ri
        a = line[ri % L]; b = line[(ri + 1) % L]
        s = a + (b - a) * fr
        y = damp * 0.5 * (s + last)
        last = s
        if i < ex_len:
            y += ex[i]
        line[w % L] = y
        out[i] = y
        w += 1
    body = filt(out, "band", [180, 260], 1) * 0.6 + filt(out, "band", [420, 560], 1) * 0.35
    out = filt(out + body, "high", 85)
    out *= env([(0, 1), (dur - 0.15, 1), (dur, 0)], n)
    pk = np.max(np.abs(out)) + 1e-9
    return out / pk * vel

def pad_chord(midis, n, spread=0.55, cutoff=1250):
    t = np.arange(n) / SR
    st = np.zeros((n, 2))
    for j, m in enumerate(midis):
        f0 = mtof(m)
        for i, cents in enumerate((-6, 0, 6)):
            f = f0 * 2 ** (cents / 1200)
            s = np.zeros(n)
            for k in range(1, 9):
                if k * f > 5000:
                    break
                s += np.sin(2 * np.pi * k * f * t + rng.uniform(0, 6.28)) / k ** 1.1
            p = (-spread, 0.0, spread)[i] * (1 if j % 2 else -1)
            st += pan(s, p)
    st = filt(st, "low", cutoff)
    return st / (len(midis) * 3)

def bell(midi, vel=0.2, dur=1.6):
    f0 = mtof(midi); n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    for ratio, amp, dec in ((1, 1, 2.2), (2.76, 0.45, 4.5), (5.40, 0.22, 8), (8.93, 0.1, 12)):
        out += amp * np.exp(-dec * t) * np.sin(2 * np.pi * f0 * ratio * t)
    out *= 1 - np.exp(-t / 0.004)
    return out * vel

def grain_cloud(t0, t1, pitches, dens, amp_env, pan_c, rise_cents=0):
    n = int((t1 - t0) * SR); st = np.zeros((n, 2)); tt = 0.0
    while True:
        local = tt / (t1 - t0)
        rate = np.interp(local, [0, 1], dens)
        tt += rng.exponential(1 / rate)
        if tt >= t1 - t0:
            break
        g = rng.uniform(0.025, 0.06); gn = int(g * SR)
        f = mtof(rng.choice(pitches)) * 2 ** (rise_cents * local / 1200)
        x = np.sin(2 * np.pi * f * np.arange(gn) / SR) * np.hanning(gn)
        a = np.interp(local, np.linspace(0, 1, len(amp_env)), amp_env) * rng.uniform(0.5, 1)
        i = int(tt * SR); j = min(n, i + gn)
        st[i:j] += pan(x[: j - i] * a, np.clip(pan_c + rng.uniform(-0.25, 0.25), -1, 1))
    return st

def make_ir(rt=2.3, length=3.0, pre=0.022, bright=6000, seed=3):
    r = np.random.default_rng(seed)
    n = int(length * SR); t = np.arange(n) / SR
    ir = np.zeros((n, 2))
    for c in range(2):
        hi = filt(r.standard_normal(n), "low", bright) * np.exp(-6.9 * t / rt)
        lo = filt(r.standard_normal(n), "low", 900) * np.exp(-6.9 * t / (rt * 1.35))
        ir[:, c] = 0.55 * hi + 0.9 * lo
    p = int(pre * SR); ir[:p] = 0
    ir[p:p + 480] *= np.linspace(0, 1, 480)[:, None]
    for d, g in ((0.011, 0.5), (0.019, 0.35), (0.031, 0.28), (0.043, 0.2)):
        k = int(d * SR); ir[k, 0] += g; ir[int(k * 1.13), 1] += g
    return ir / np.sqrt(np.sum(ir ** 2) / 2)

def reverb(st, ir, wet):
    y = np.stack([signal.fftconvolve(st[:, c], ir[:, c])[:N] for c in range(2)], axis=1)
    return st + y * wet


# ----------------------------------------------------------------- MUSIC
music = blank()
cue_log = []
def cue(stem, frame_in, frame_out, name, sync):
    cue_log.append((stem, frame_in, frame_out, name, sync))

# Pad: Dm -> Bb/D (lift) -> D major (Hijaz colour) at the join
pad_specs = [
    ([50, 57, 62, 65], [(0.0, 0), (1.5, 0.75), (2.0, 0.75), (2.35, 0)], "Pad · D minor (nostalgia)", 0, 70, "opening, under the reveals"),
    ([50, 58, 62, 65], [(1.95, 0), (2.4, 0.7), (3.2, 1.0), (3.47, 0)], "Pad · B♭/D swell (anticipation)", 59, 104, "rises through the morph"),
    ([50, 57, 62, 66], [(3.25, 0), (3.52, 0.95), (5.0, 0.85), (6.3, 0.6), (7.0, 0)], "Pad · D major, F→F♯ lift (the new place)", 98, 210, "lands on the join"),
]
for midis, pts, name, fi, fo, sync in pad_specs:
    music += pad_chord(midis, N) * env(pts, N)[:, None] * db(-14)
    cue("Music", fi, fo, name, sync)
sub = np.sin(2 * np.pi * mtof(38) * np.arange(N) / SR)
music += pan(sub, 0) * env([(0, 0), (1.8, 0.5), (3.2, 0.7), (3.5, 0.9), (6.2, 0.6), (7.0, 0)], N)[:, None] * db(-30)

# Piano
piano_notes = [
    (0.35, 74, 0.30, "Piano D5", 10, "first word lands"), (1.15, 69, 0.24, "Piano A4", 35, "between reveals"),
    (1.75, 77, 0.22, "Piano F5", 53, "line complete"),
    (T(102), 62, 0.26, "Piano chord D–F♯–A + D5", 102, "morph completes: musical lift"),
    (T(102) + 0.018, 66, 0.24, None, 0, ""), (T(102) + 0.036, 69, 0.24, None, 0, ""), (T(102) + 0.05, 74, 0.26, None, 0, ""),
    (T(150), 81, 0.16, "Piano A5 sparkle", 150, "phrase settles"),
    (T(170), 50, 0.30, "Piano D3 + D2 bass", 170, "logo appears"), (T(170) + 0.01, 38, 0.22, None, 0, ""),
    (T(176), 86, 0.10, "Piano D6 air", 176, "logo settles"),
]
for t0, m, v, name, fr, sync in piano_notes:
    st = pan(piano(m, v, dur=min(3.5, DUR - t0 + 0.4)), 0.15 if m > 70 else -0.1)
    add(music, st * db(-8), t0)
    if name:
        cue("Music", fr, min(210, fr + 45), name, sync)

# Oud: pickup, risha tremolo through the morph, Hijaz descent into the logo
add(music, pan(oud(57, 0.35, 1.0, 0.4), -0.2) * db(-12), T(57)); cue("Music", 57, 80, "Oud A3 pickup", "the «ما» flag warms")
trem_t = np.arange(T(74), T(97), 1 / 13.0)
for i, t0 in enumerate(trem_t):
    v = 0.12 + 0.38 * (i / (len(trem_t) - 1)) ** 1.6
    add(music, pan(oud(62, v, 0.22, 0.45 + 0.2 * (i % 2)), -0.15) * db(-12), t0)
cue("Music", 74, 97, "Oud D4 risha tremolo, crescendo", "tension while the gap closes; stops on contact")
phrase = [(146, 69, 0.50, 0.55), (152, 67, 0.45, 0.5), (157, 66, 0.45, 0.5), (163, 63, 0.50, 0.55), (170, 62, 0.58, 1.3)]
for fr, m, v, d in phrase:
    add(music, pan(oud(m, v, d + 0.25, 0.55, vibrato=0.0045 if m == 62 else 0.0), -0.2) * db(-10), T(fr))
cue("Music", 146, 210, "Oud Hijaz descent A–G–F♯–E♭–D", "slogan in → resolves on the logo")

# warm low tone under the logo
lt = np.arange(N - int(T(170) * SR)) / SR
tone = (np.sin(2 * np.pi * mtof(38) * lt) + 0.25 * np.sin(2 * np.pi * mtof(50) * lt)) * (1 - np.exp(-lt / 0.35))
add(music, pan(tone, 0) * db(-24), T(170)); cue("Music", 170, 210, "Warm low D tone", "logo")


# ----------------------------------------------------------------- SOUND DESIGN
sfx = blank()

# room tone
amb = filt(pink(N), "low", 650) * db(-12) + filt(noise(N), "band", [6000, 11000]) * db(-38)
sfx += pan(amb, 0) * env([(0, 0), (0.5, 1), (6.4, 1), (7.0, 0)], N)[:, None] * db(-26)
cue("SFX", 0, 210, "Room tone (warm, low-passed)", "fades in 0–15, out 192–210")

# paper rustle as the frame breathes in
n = int(0.7 * SR); rust = np.zeros(n)
for _ in range(38):
    i = rng.integers(0, n - 2000); ln = rng.integers(300, 1600)
    rust[i:i + ln] += noise(ln) * np.hanning(ln) * rng.uniform(0.2, 1) * np.exp(-i / (0.35 * SR))
rust = filt(rust, "band", [1800, 7000])
add(sfx, pan(rust, 0.1) * db(-27), T(1)); cue("SFX", 1, 22, "Paper texture", "hairline frame breathes in")

# calligraphy strokes, one per word, panned to the word's position (RTL)
for i, (fr, p) in enumerate(((6, 0.38), (14, 0.14), (22, -0.1), (30, -0.32))):
    n = int(0.42 * SR); t = np.arange(n) / SR
    grit = noise(n) * (0.55 + 0.45 * np.abs(np.sin(2 * np.pi * rng.uniform(28, 46) * t + rng.uniform(0, 6))))
    hiss = svf(grit, 2600 + 1400 * np.sin(np.pi * t / 0.42) + 300 * i, q=1.4)
    body = filt(noise(n), "band", [250, 600]) * 0.25
    stroke = (hiss + body) * env([(0, 0), (0.03, 1), (0.16, 0.75), (0.3, 0.35), (0.42, 0)], n)
    add(sfx, pan(stroke, p) * db(-21), T(fr))
cue("SFX", 6, 48, "Pen strokes ×4 (f6/14/22/30), panned R→L", "each word's mask wipe")

# the three diamond dots: tiny tuned ink taps
for fr, m in ((46, 86), (51, 89), (56, 93)):
    n = int(0.25 * SR); t = np.arange(n) / SR
    tap = np.sin(2 * np.pi * mtof(m) * t) * np.exp(-t / 0.045) + filt(noise(n), "high", 3000) * np.exp(-t / 0.003) * 0.4
    add(sfx, pan(tap, -0.42) * db(-28), T(fr))
cue("SFX", 46, 60, "Dot taps D6 / F6 / A6", "each diamond lands")

# reverse swell into the morph (ends exactly as the alef starts to lift)
n = int(0.5 * SR); t = np.arange(n) / SR
src = filt(noise(n), "band", [400, 3000]) * np.exp(-t / 0.05) + 0.5 * np.sin(2 * np.pi * mtof(62) * t) * np.exp(-t / 0.08)
ir_s = make_ir(rt=1.0, length=0.5, seed=9)
tail = signal.fftconvolve(src, ir_s[:, 0])[:n]
swell = tail[::-1] * env([(0, 0), (0.4, 1), (0.47, 1), (0.5, 0)], n)
add(sfx, pan(swell / np.max(np.abs(swell)), 0) * db(-20), T(68) - 0.5); cue("SFX", 53, 68, "Reverse swell", "builds into the morph, peaks as the alef lifts")

# alef dissolving upward: granular sparkle + rising air
gc = grain_cloud(T(68), T(94), [86, 87, 90, 91, 93, 94, 96, 98], dens=[18, 45], amp_env=[0.2, 1, 0.8, 0], pan_c=-0.05, rise_cents=500)
add(sfx, gc * db(-26), T(68))
n = int((T(94) - T(68)) * SR); t = np.arange(n) / SR; u = t / t[-1]
air = svf(noise(n), 1500 + 5500 * u ** 1.3, q=1.6) * env([(0, 0), (0.25, 1), (0.6, 0.7), (0.87, 0)], n)
add(sfx, pan(air, -0.05) * db(-27), T(68)); cue("SFX", 68, 94, "Granular sparkle + rising air", "alef lifts, narrows, blurs out")

# convergence whooshes: loudness follows the real speed of the slide (f70-102)
n = int((T(104) - T(68)) * SR)
spd = speed_curve(70, 102, "io", n=n, t_start=T(68))
for p0, seed_shift in ((0.45, 0), (-0.45, 1)):        # meem from the right, kaf from the left
    x = svf(noise(n), 350 + 2600 * spd ** 0.9 + 80 * seed_shift, q=0.9)
    p = p0 * (1 - np.clip(np.arange(n) / n * 1.1, 0, 1))
    add(sfx, pan(x * (0.08 + spd ** 0.85), p) * db(-15), T(68))
low = filt(noise(n), "low", 160) * spd
add(sfx, pan(low, 0) * db(-19), T(68)); cue("SFX", 70, 102, "Twin whooshes converging to centre (speed-driven)", "meem slides left, kaf slides right, the gap closes")

# dots 2-3 drop away
for k, (fr, pp) in enumerate(((80, -0.4), (83, -0.5))):
    n = int(0.32 * SR); t = np.arange(n) / SR
    f = 950 * np.exp(-t * 2.2)
    drip = np.sin(2 * np.pi * np.cumsum(f) / SR) * env([(0, 0), (0.02, 1), (0.32, 0)], n)
    add(sfx, pan(drip, pp) * db(-37), T(fr))
cue("SFX", 80, 98, "Two falling glints", "dots 2–3 drop and fade")

# contact: the ink tap
n = int(0.6 * SR); t = np.arange(n) / SR
click = filt(noise(n), "band", [2500, 7000]) * np.exp(-t / 0.0025)
wood = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in ((190, 1, 0.06), (430, 0.6, 0.04), (960, 0.3, 0.025)))
thump = np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.07)
tap = 0.7 * click + 0.5 * wood + 0.7 * thump
add(sfx, pan(tap, 0) * db(-14), T(100)); cue("SFX", 100, 104, "Ink tap (click + wood + soft thump)", "meem and kaf lock together")

# period pulse: tonal ting
add(sfx, pan(bell(86, 1, 1.8) + 0.6 * bell(93, 1, 1.8), -0.15) * db(-27), T(100)); cue("SFX", 100, 150, "Tonal ting D6/A6", "full stop brightens and pulses")

# rise + soft cinematic settle
n = int((T(152) - T(122)) * SR)
spd = speed_curve(122, 150, "io", n=n, t_start=T(122))
rise = svf(noise(n), 300 + 1300 * spd, q=0.9) * spd
add(sfx, pan(rise, 0) * db(-29), T(122))
n = int(1.6 * SR); t = np.arange(n) / SR
boom = np.sin(2 * np.pi * np.cumsum(62 * np.exp(-t * 1.2) + 46) / SR) * (1 - np.exp(-t / 0.015)) * np.exp(-t / 0.55)
boom += filt(noise(n), "low", 400) * np.exp(-t / 0.12) * 0.35
add(sfx, pan(boom, 0) * db(-17), T(149)); cue("SFX", 122, 152, "Air rise + soft felt impact", "«كان يا مكان.» rises and settles")

# rule draws right to left
n = int((T(168) - T(138)) * SR)
spd = speed_curve(138, 166, "out", n=n, t_start=T(138))
hiss = svf(noise(n), 6500, q=2.5) * (spd ** 0.7) * (1 - np.exp(-np.arange(n) / (0.02 * SR)))
add(sfx, pan(hiss, np.linspace(0.3, -0.3, n)) * db(-28), T(138)); cue("SFX", 138, 166, "Fine hiss panned R→L", "fatha rule draws right to left")

# slogan shimmer
n = int((DUR - T(146)) * SR); t = np.arange(n) / SR
sh = np.zeros(n)
for m in (86, 90, 93, 98):
    sh += np.sin(2 * np.pi * mtof(m) * t + rng.uniform(0, 6)) * (0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(4, 7) * t))
sh *= env([(0, 0), (0.45, 1), (1.3, 0.55), (n / SR, 0)], n)
add(sfx, pan(sh, 0.12) * db(-42), T(146))
add(sfx, grain_cloud(T(146), T(186), [93, 95, 98, 100], dens=[10, 4], amp_env=[0, 1, 0.3], pan_c=0.1) * db(-31), T(146))
cue("SFX", 146, 200, "Warm tonal shimmer + sparkle", "slogan rises in")

# logo bloom
n = int((DUR - T(168)) * SR)
bloom = filt(noise(n), "low", 900) * env([(0, 0), (0.6, 1), (1.0, 0.6), (n / SR, 0)], n)
add(sfx, pan(bloom, 0) * db(-33), T(168)); cue("SFX", 168, 210, "Soft air bloom", "logo settles")


# ----------------------------------------------------------------- buses, reverb, master
for st in (music, sfx):
    st[:] = filt(st, "high", 32)
music = reverb(music, make_ir(2.4, 3.0, seed=4), 0.32)
sfx = reverb(sfx, make_ir(1.6, 2.2, seed=5), 0.16)

end_fade = env([(0, 1), (6.55, 1), (6.985, 0)], N)[:, None]
music *= end_fade; sfx *= end_fade

def lufs(x):
    b1 = signal.butter(2, 1500, "high", fs=SR, output="sos")  # approximate K-weighting shelf
    hs = np.array([[1.53512485958697, -2.69169618940638, 1.19839281085285, 1, -1.69065929318241, 0.73248077421585]])
    hp = np.array([[1.0, -2.0, 1.0, 1, -1.99004745483398, 0.99007225036621]])
    y = signal.sosfilt(hp, signal.sosfilt(hs, x, axis=0), axis=0)
    blk = int(0.4 * SR); hop = int(0.1 * SR)
    ms = np.array([np.mean(np.sum(y[i:i + blk] ** 2, axis=1)) for i in range(0, len(y) - blk + 1, hop)])
    l = -0.691 + 10 * np.log10(ms + 1e-12)
    g = ms[l > -70]
    rel = -0.691 + 10 * np.log10(np.mean(g)) - 10
    g = ms[(l > -70) & (l > rel)]
    return -0.691 + 10 * np.log10(np.mean(g))

def tp_gain(x, ceiling_db=-1.3):
    """lookahead true-peak limiter gain envelope (4x oversampled detection)."""
    up = signal.resample_poly(x, 4, 1, axis=0)
    pk = np.max(np.abs(up), axis=1).reshape(-1, 4).max(axis=1)[: len(x)]
    c = db(ceiling_db)
    need = np.minimum(1.0, c / np.maximum(pk, 1e-9))
    la = int(0.003 * SR)
    need = np.minimum.accumulate(np.concatenate([need[la:], np.ones(la)])[::-1])[::-1] if False else need
    # lookahead min filter
    from scipy.ndimage import minimum_filter1d
    need = minimum_filter1d(need, size=2 * la + 1)
    # smooth: instant attack via min filter, 90 ms release
    g = np.empty_like(need); cur = 1.0; rel = np.exp(-1 / (0.09 * SR))
    for i in range(len(need)):
        cur = need[i] if need[i] < cur else need[i] + (cur - need[i]) * rel
        g[i] = cur
    return signal.filtfilt(*signal.butter(1, 400, fs=SR), g)

mix = music + sfx
gain = 1.0; genv = np.ones(N)
for _ in range(6):
    cur = lufs(mix * gain * genv[:, None])
    gain *= db(-14.0 - cur)
    genv = tp_gain(mix * gain)
final = mix * gain * genv[:, None]
print("integrated LUFS (internal):", round(lufs(final), 2))

def write24(path, x):
    x = np.clip(x + (rng.random(x.shape) - rng.random(x.shape)) / 2 ** 23, -1, 1 - 2 ** -23)
    q = np.round(x * (2 ** 23 - 1)).astype("<i4")
    b = q.view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR); w.writeframes(b)

write24(os.path.join(OUT, "Background_Music.wav"), music * gain * genv[:, None])
write24(os.path.join(OUT, "Sound_Design.wav"), sfx * gain * genv[:, None])
write24(os.path.join(OUT, "Final_Mix.wav"), final)
write24(os.path.join(OUT, "Kan_Ya_Makan_Final.wav"), final)

with open(os.path.join(OUT, "cue_sheet.tsv"), "w", encoding="utf-8") as fh:
    fh.write("stem\tframe_in\tframe_out\ttc_in\ttc_out\telement\tsynced_to\n")
    for stem, a, b, name, sync in sorted(cue_log, key=lambda c: (c[1], c[0])):
        tc = lambda f: f"00:0{f // 30}:{f % 30:02d}"
        fh.write(f"{stem}\t{a}\t{b}\t{tc(a)}\t{tc(b)}\t{name}\t{sync}\n")
print("done")
