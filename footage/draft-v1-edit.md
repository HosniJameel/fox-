# Reel Draft v1 — Edit Decision List

- **Draft media_id:** `7b4e6c48-8986-4d9f-b5b8-e4f0d66ef891`
- **Spec:** 1080×1920 · 23.976 fps · H.264 High · AAC 48 kHz · 20.98 s · −14.1 LUFS / −1.5 dBTP
- **Credits used:** 0 · Originals untouched (10/10 SHA-256 OK after render)

## Timeline (frame-accurate @ 23.976 fps)

| # | Reel time | Video source | Audio source | Role |
|---|---|---|---|---|
| 1 | 0.00–2.59 | C2707 0.71–3.30 (push-in 100→106%) | C2707 sync | Hook |
| 2 | 2.59–3.38 | C2712 0.58–1.38 (walk-in) | C2708 0.00–0.79 (J-cut) | Energy |
| 3 | 3.38–8.22 | C2708 0.79–5.63 | C2708 sync | Product name |
| 4 | 8.22–12.05 | C2709 5.13–8.97 (push-in 100→108%) | C2709 sync | Titanium claim |
| 5 | 12.05–14.68 | C2716 0.00–2.63 | C2716 sync | Health intro |
| 6 | 14.68–16.93 | C2710 4.00–6.26 (B-roll, HUAWEI counter) | C2716 2.63–4.88 | Health features |
| 7 | 16.93–18.94 | C2716 4.88–6.88 | C2716 sync | 10 medical reports |
| 8 | 18.94–20.94 | C2714 13.01–15.01 (dimmed) | silence (off-take chatter removed) | End card |

## Dialogue & captions (verified across takes)

| Reel time | Spoken (as captioned) | Confidence |
|---|---|---|
| 0.30–2.55 | وأخيراً راح نبيع **طيارات** (+ store name, not captioned) | High; store name unclear |
| 2.60–4.50 | إي نعم… مثل ما سمعت | High |
| 4.52–6.64 | لأنو هاي **الطيارة** اسمها | High |
| 6.66–8.20 | **الواتش فايف** من هواوي | High |
| 8.24–10.08 | مصنوعة من سبائك **تيتانيوم** | Medium ("سبائك" inferred) |
| 10.11–12.00 | اللي نفسه مصنوعة منه **هالطيارات** | High |
| 12.04–13.84 | وكلنا نعرف / ماكو **أدق** من هواوي | High (5 takes agree) |
| 13.86–14.58 | بسوالف **الصحة** | Medium ("بسوالف" inferred) |
| 14.60–16.00 | مثل قياس **الأوكسجين** | High |
| 16.02–16.88 | وقياس **ضغط الدم** | High (C2713 confirms) |
| 16.92–18.85 | وبيها أكثر من / **10 تقارير طبية** | High |
| 19.05–20.94 | End card: هواوي واتش 5 / مصنوعة من التيتانيوم | From dialogue |

## Processing
- **Grade:** levels 0.04–0.95 → S-curve → saturation ×1.2 → slight warm mids / cool shadows → vignette.
- **Audio:** high-pass 80 Hz → light denoise → 3:1 compression → loudnorm −14 LUFS → limiter.
- **Captions:** Tajawal ExtraBold (OFL) + Montserrat digits, rendered in Chromium for correct Arabic shaping and RTL; red #E3262E keyword highlight; 0.15 s fade and rise animation.
- **Music:** none (Option A, add a trending track in Instagram when posting).
