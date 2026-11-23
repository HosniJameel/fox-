"""
KAN paper teaser · audio assembly and mix — 8.000 s, 48 kHz, 24-bit stereo.
Sources: ElevenLabs Music v2.5 take + Mirelo Foley (both generated on Higgsfield),
plus synthesised room tone, intro pad, transition air and logo bell (tuned to the track's G major).
Word/strike/logo timings are read from ../post/timings.json (written by the renderer).
"""
import os, json, wave, subprocess
import numpy as np
from scipy import signal
from scipy.ndimage import minimum_filter1d

SR, DUR = 48000, 8.0
N = int(SR * DUR)
H = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(H, "..", "gen")
OUT = os.path.join(H, "out"); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(88)
TM = json.load(open(os.path.join(H, "..", "post", "timings.json")))
MUSIC_DELAY = 1.6     # bloom of the track (4.0 s) lands at 5.6 s, peaking into the logo

def T(f): return f / 30.0
def db(x): return 10 ** (x / 20.0)
def load(name, mono=False):
    b = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", os.path.join(GEN, name), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True).stdout
    x = np.frombuffer(b, np.float32).reshape(-1, 2).astype(np.float64)
    return x.mean(1) if mono else x
def pan(x, p):
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1)
def add(bus, st, t0):
    i = int(round(t0 * SR)); j = min(N, i + len(st))
    if i < 0: st = st[-i:]; i = 0; j = min(N, len(st))
    if j > i: bus[i:j] += st[:j - i]
def fades(x, a=0.012, b=0.03):
    n = len(x); fa, fb = int(a * SR), int(b * SR)
    e = np.ones(n); e[:fa] = np.linspace(0, 1, fa); e[n - fb:] = np.linspace(1, 0, fb)
    return x * (e[:, None] if x.ndim == 2 else e)
def filt(x, kind, fc, order=2): return signal.sosfilt(signal.butter(order, fc, kind, fs=SR, output="sos"), x, axis=0)
def rms(x): return np.sqrt(np.mean(x ** 2) + 1e-12)
def env(points, n, t0=0.0):
    t = t0 + np.arange(n) / SR; xs = np.array([p[0] for p in points]); ys = np.array([p[1] for p in points])
    return np.interp(t, xs, ys)

cues = []
def cue(stem, a, b, name, src, sync): cues.append((stem, int(a), int(b), name, src, sync))

# ------------------------------------------------------------------ MUSIC
music = np.zeros((N, 2))
trk = load("music_1.mp3")
seg = trk[: N - int(MUSIC_DELAY * SR)]
seg = seg * env([(0, 1), (7.2 - MUSIC_DELAY, 1), (7.98 - MUSIC_DELAY, 0)], len(seg))[:, None]
add(music, seg * db(0), MUSIC_DELAY)
# ride the bloom: smooth ~6 dB dip so the last pen word and the logo bell read clearly
music *= np.interp(np.arange(N) / SR, [0, 5.25, 5.65, 6.5, 7.3, 8.0], db(np.array([0, 0, -6.5, -6, -4.5, -4.5])))[:, None]
cue("Music", int(MUSIC_DELAY * 30), 240, "Score · ElevenLabs Music v2.5 (piano, oud, pads)", "Higgsfield job e8268f51", "builds under the strike, blooms as «مكان» completes, peaks into the logo")
t = np.arange(N) / SR; pad = np.zeros(N)
for midi, a in ((43, .5), (50, .45), (55, .35), (59, .3), (62, .22)):    # G2 D3 G3 B3 D4
    f0 = 440 * 2 ** ((midi - 69) / 12)
    for c in (-5, 5):
        pad += a * sum(np.sin(2 * np.pi * k * f0 * 2 ** (c / 1200) * t + rng.uniform(0, 6)) / k ** 1.2 for k in range(1, 6))
pad = filt(pad, "low", 1100)
padst = np.stack([pad, np.roll(pad, 240)], 1) * env([(0, 0), (1.2, 1), (2.2, 1), (3.4, 0)], N)[:, None]
music += padst / rms(padst[:int(2.5 * SR)]) * db(-30)
cue("Music", 0, 102, "Intro pad · G major (synth)", "synthesised", "the first line; hands over to the score")
lt = np.arange(N - int(T(TM["logo"][0]) * SR)) / SR
low = (np.sin(2 * np.pi * 49.0 * lt) + .3 * np.sin(2 * np.pi * 98.0 * lt)) * (1 - np.exp(-lt / .3)) * np.exp(-lt / 2.5)
add(music, pan(low, 0) * db(-26), T(TM["logo"][0]))
cue("Music", TM["logo"][0], 240, "Warm low G under the logo (synth)", "synthesised", "logo")

# ------------------------------------------------------------------ SOUND DESIGN
sfx = np.zeros((N, 2))
room = filt(np.fft.irfft(np.fft.rfft(rng.standard_normal(N)) / np.sqrt(np.maximum(np.fft.rfftfreq(N, 1 / SR), 1)), N), "low", 600)
room = room / rms(room) * db(-50)
sfx += pan(room, 0) * env([(0, 0), (.4, 1), (7.5, 1), (8, 0)], N)[:, None]
cue("SFX", 0, 240, "Quiet study room tone (synth)", "synthesised", "the whole shot")

paper = load("sfx_paper.mp3", mono=True)[: int(.9 * SR)]
add(sfx, pan(fades(paper, .005, .25) / rms(paper) * db(-38), .1), T(1))
cue("SFX", 1, 28, "Paper settling", "Mirelo · job be43026e", "the shot fades in on the sheet")

pen = load("sfx_pen_a.mp3", mono=True); pen = filt(pen, "high", 180)
win = int(.05 * SR); act = np.array([rms(pen[i:i + win]) for i in range(0, len(pen) - win, win)])
used = np.zeros(len(act), bool)
def pen_slice(dur):
    k = max(1, int(round(dur / .05)))
    best, bi = -1, 0
    for i in range(0, len(act) - k):
        if used[i:i + k].any(): continue
        s = act[i:i + k].mean()
        if s > best: best, bi = s, i
    used[bi:bi + k] = True
    x = pen[bi * win: bi * win + int(dur * SR)]
    return x / rms(x)
words = [("w1a", .35, "كان"), ("w1b", .05, "فكرة."), ("w2a", .45, "والفكرة"), ("w2b", .2, "جاي"), ("w2c", 0, "يصير"), ("w2d", -.2, "إلها"), ("w2e", -.4, "مكان")]
for wid, p, txt in words:
    a, b = TM["words"][wid]
    d = T(b) - T(a) + .05
    x = fades(pen_slice(d), .01, .06)
    add(sfx, pan(x, p) * db(-27 + (5 if wid == "w2e" else 0)), T(a))
    cue("SFX", a, b, f"Pen writing «{txt}»", "Mirelo · job 4494ac61 (sliced)", "that word's ink reveal")

strike = load("sfx_strike.mp3", mono=True)
st = strike[int(1.06 * SR): int(1.54 * SR)]
st = fades(st / rms(st), .004, .12)
s0, s1 = TM["strike"]
add(sfx, pan(st, .05) * db(-24), T(s0) - .01)
cue("SFX", s0, s1, "Decisive pen strike", "Mirelo · job 5a2c4561", "the line crossing out «فكرة»")
n = int(.4 * SR); a_ = filt(rng.standard_normal(n), "band", [1500, 6000]) * np.linspace(0, 1, n) ** 2
add(sfx, pan(a_ / rms(a_), 0) * db(-44), T(s0) - .4)
cue("SFX", s0 - 12, s0, "Light air lift into the strike (synth)", "synthesised", "transition accent")

lg = TM["logo"][0]
n = int(1.8 * SR); tt = np.arange(n) / SR; bell = np.zeros(n)
for f0, amp in ((783.99, 1), (1174.66, .55), (1567.98, .3)):        # G5, D6, G6
    for r, ra, d in ((1, 1, 2.0), (2.76, .35, 4.5), (5.4, .15, 8)):
        bell += amp * ra * np.exp(-d * tt) * np.sin(2 * np.pi * f0 * r * tt)
bell *= 1 - np.exp(-tt / .006)
add(sfx, pan(bell / rms(bell) * db(-27), -.08), T(lg))
mlogo = load("sfx_logo.mp3", mono=True)
add(sfx, pan(fades(mlogo / rms(mlogo), .2, .8) * db(-44), .1), T(lg) - .1)
cue("SFX", lg, 240, "Logo reveal: soft G/D bell + airy shimmer", "synthesised bell + Mirelo job 1fe7f7fa", "the logo's ink appears")

# ------------------------------------------------------------------ BUS + MASTER
ir_n = int(1.6 * SR); irt = np.arange(ir_n) / SR
ir = np.stack([filt(rng.standard_normal(ir_n), "low", 5000) * np.exp(-6.9 * irt / 1.3) for _ in range(2)], 1); ir[:960] = 0
ir /= np.sqrt(np.sum(ir ** 2) / 2)
sfx = sfx + np.stack([signal.fftconvolve(sfx[:, c], ir[:, c])[:N] for c in range(2)], 1) * .12
music = filt(music, "high", 30); sfx = filt(sfx, "high", 60)
fade = env([(0, 1), (7.6, 1), (7.985, 0)], N)[:, None]; music *= fade; sfx *= fade

def lufs(x):
    hs = np.array([[1.53512485958697, -2.69169618940638, 1.19839281085285, 1, -1.69065929318241, .73248077421585]])
    hp = np.array([[1., -2., 1., 1, -1.99004745483398, .99007225036621]])
    y = signal.sosfilt(hp, signal.sosfilt(hs, x, axis=0), axis=0); blk, hop = int(.4 * SR), int(.1 * SR)
    ms = np.array([np.mean(np.sum(y[i:i + blk] ** 2, 1)) for i in range(0, len(y) - blk + 1, hop)])
    l = -.691 + 10 * np.log10(ms + 1e-12); g = ms[l > -70]; rel = -.691 + 10 * np.log10(np.mean(g)) - 10
    return -.691 + 10 * np.log10(np.mean(ms[(l > -70) & (l > rel)]))
def tp_gain(x, ceiling=-1.3):
    up = signal.resample_poly(x, 4, 1, axis=0); pk = np.max(np.abs(up), 1).reshape(-1, 4).max(1)[:len(x)]
    need = minimum_filter1d(np.minimum(1, db(ceiling) / np.maximum(pk, 1e-9)), size=2 * int(.003 * SR) + 1)
    g = np.empty_like(need); cur = 1.0; rel = np.exp(-1 / (.09 * SR))
    for i in range(len(need)): cur = need[i] if need[i] < cur else need[i] + (cur - need[i]) * rel; g[i] = cur
    return signal.filtfilt(*signal.butter(1, 400, fs=SR), g)

mix = music + sfx; gain = 1.0; genv = np.ones(N)
for _ in range(6): gain *= db(-14 - lufs(mix * gain * genv[:, None])); genv = tp_gain(mix * gain)
G = gain * genv[:, None]
def write24(path, x):
    x = np.clip(x + (rng.random(x.shape) - rng.random(x.shape)) / 2 ** 23, -1, 1 - 2 ** -23)
    q = np.round(x * (2 ** 23 - 1)).astype("<i4")
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(3); w.setframerate(SR); w.writeframes(q.view(np.uint8).reshape(-1, 4)[:, :3].tobytes())
write24(os.path.join(OUT, "Kan_Paper_Background_Music.wav"), music * G)
write24(os.path.join(OUT, "Kan_Paper_Sound_Design.wav"), sfx * G)
write24(os.path.join(OUT, "Kan_Paper_Final_Mix.wav"), (music + sfx) * G)
with open(os.path.join(OUT, "cue_sheet.tsv"), "w", encoding="utf-8") as fh:
    fh.write("stem\tframe_in\tframe_out\ttc_in\ttc_out\telement\tsource\tsynced_to\n")
    tc = lambda f: f"00:0{f // 30}:{f % 30:02d}"
    for s, a, b, nm, src, why in sorted(cues, key=lambda c: (c[1], c[0])):
        fh.write(f"{s}\t{a}\t{b}\t{tc(a)}\t{tc(b)}\t{nm}\t{src}\t{why}\n")
print("LUFS", round(lufs((music + sfx) * G), 2))
