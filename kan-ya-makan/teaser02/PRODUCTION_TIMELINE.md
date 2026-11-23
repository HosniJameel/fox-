# كان يا مكان — Teaser 02 «من الورق للواقع» · Production timeline

8.000 s · 240 frames @ 30 fps · 1080×1920 · H.264 18 Mbps + AAC 320 kbps / 48 kHz

## Edit decision list

| Frames | Shot | Source | Treatment |
|---|---|---|---|
| f0–f89 | 01 · The idea on paper | `gen/paper_a.png` (Higgsfield · Nano Banana 2.1, job 951c433b) | «كان فكرة.» set in post in Aref Ruqaa Bold as ink (multiply into the paper fibre, −1.4°), 10 % eased push-in, window light breathing, 12-frame fade from black |
| f85–f96 | Match cut | n/a | Written line → pencil line; warm light bloom peaking on f90 |
| f90–f149 | 02 · The idea becomes real | `gen/vid_craft_b.mp4` (Kling 3.0 Pro i2v, job 9207896a), source 0.8–2.8 s | 24 → 30 fps motion-compensated, exposure matched |
| f150–f239 | 03 · The reveal | `gen/vid_detail_a.mp4` (Kling 3.0 Pro i2v, job 7277c1d3), source 0.1–2.35 s only (grain drifts after ~2.5 s) | Retimed to 3 s with motion interpolation; scrim from f166 |
| f178–f202 | Slogan | Reem Kufi SemiBold 64 px, #F0DDBE | Opacity + 26 px rise + blur 6 → 0 |
| f204–f226 | Logo | `post/kan-logo.png` (keyed from the official logo file) | Opacity, 12 px rise, 96 → 100 % |
| f0–f239 | Grade | n/a | Matched exposure on shots 2–3, warm shadow/highlight balance, vignette, fine film grain |

Reference stills generated and kept for continuity: `craft_a`, `craft_b` (start frame of shot 2), `detail_a` (start frame of shot 3, made with craft_b as reference), `detail_b`, `paper_b`. Higgsfield spend: ≈ 38 credits.

## Audio cue sheet

| Frames | Timecode | Stem | Element | Locked to |
|---|---|---|---|---|
| f0–f95 | 00:00:00 → 00:03:05 | Music | Pad · D minor add9 (the idea) | paper scene |
| f0–f90 | 00:00:00 → 00:03:00 | SFX | Quiet study room tone | paper scene |
| f0–f30 | 00:00:00 → 00:01:00 | SFX | Intro tone (very low D) | opening |
| f3–f60 | 00:00:03 → 00:02:00 | SFX | Paper movement texture ×2 | the sheet in the light, the push-in |
| f10–f50 | 00:00:10 → 00:01:20 | Music | Piano D5 | paper settles in the light |
| f40–f80 | 00:01:10 → 00:02:20 | Music | Piano A4 | push-in |
| f68–f108 | 00:02:08 → 00:03:18 | Music | Piano F5 | approaching the words |
| f75–f103 | 00:02:15 → 00:03:13 | SFX | Reverse swell → tonal air | the match cut paper → oak |
| f87–f153 | 00:02:27 → 00:05:03 | Music | Pad · B♭ add9 lift (becoming real) | the cut to the craftsman |
| f90–f150 | 00:03:00 → 00:05:00 | Music | Oud pulse D–A–D–F–E–D–A–B♭ | the craftsman at work |
| f90–f240 | 00:03:00 → 00:08:00 | SFX | Workshop ambience (soft, wide) | the real space |
| f93–f146 | 00:03:03 → 00:04:26 | SFX | Graphite on oak + steel-ruler tick | the pencil line |
| f148–f240 | 00:04:28 → 00:08:00 | Music | Pad · D major (resolution) | the reveal |
| f150–f190 | 00:05:00 → 00:06:10 | Music | Piano chord D–F♯–A | cut to the crafted detail |
| f150–f162 | 00:05:00 → 00:05:12 | SFX | Soft air + gentle wood resonance | cut to the crafted detail |
| f178–f240 | 00:05:28 → 00:08:00 | Music | Oud Hijaz descent A–G–F♯–E♭ → D | slogan in, resolves on the logo |
| f178–f240 | 00:05:28 → 00:08:00 | SFX | Warm tonal shimmer | slogan rises in |
| f204–f240 | 00:06:24 → 00:08:00 | Music | Piano D3 + D2 under the logo | logo |
| f204–f240 | 00:06:24 → 00:08:00 | Music | Warm low D tone | logo |
| f204–f240 | 00:06:24 → 00:08:00 | SFX | Soft bell accent D6/A6 | logo |
| f212–f240 | 00:07:02 → 00:08:00 | Music | Piano D6 air | logo settles |

## Mix

| File | Integrated | True peak |
|---|---|---|
| Final_Mix.wav | −14.0 LUFS | −1.5 dBTP |
| Background_Music.wav | −15.0 LUFS | −2.0 dBTP |
| Sound_Design.wav | −18.6 LUFS | −5.4 dBTP |

All audio is synthesised by `audio/synth_teaser02.py` (no samples, nothing to license). Sync points live in its `SYNC` table; edit `audio/sync.json` to retime and re-run.

## Rebuild

1. `node post/render_layers.js` renders the paper scene and the typography overlay.
2. `python3 audio/synth_teaser02.py` renders the stems and the mix.
3. Run the ffmpeg retime and composite commands recorded in this session to produce `renders/Kan_Ya_Makan_Teaser_02_Final.mp4`.
