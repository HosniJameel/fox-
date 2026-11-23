# KAN — Paper Teaser · Production timeline (editable project)

8.000 s · 240 frames @ 30 fps · 1080×1920 · one locked shot of one sheet of paper.

## Picture

| Frames | Time | Event | Layer |
|---|---|---|---|
| f0–f8 | 0.00–0.27 | Fade up on the paper | `compose.html` #fade |
| f10–f26 | | Ink-writes «كان» | per-word RTL ink mask |
| f31–f57 | | Ink-writes «فكرة.» | per-word RTL ink mask |
| f57–f76 | 1.90–2.53 | Hold, ink dries | wet → dry opacity |
| f76–f94 | 2.53–3.13 | One pen line strikes out «فكرة» only (still legible underneath) | SVG path, stroke-dashoffset, drawn right → left |
| f105–f124 | | «والفكرة» | |
| f127–f139 | | «جاي» | |
| f142–f156 | | «يصير» | |
| f159–f168 | | «إلها» | |
| f171–f182 | → 6.07 s | «مكان». Full sentence complete before 6.25 s | |
| f190–f222 | 6.33–7.40 | Official KAN logo appears as brown ink (radial bleed) | `kan-logo-ink.png` (official logo, one-colour brand brown) |
| f222–f239 | 7.40–8.00 | Final composition holds | |
| f0–f239 | | Digital push-in 1.000 → 1.035 applied to plate and type together, so the type stays locked to the paper | #cam |

- **Background:** Higgsfield. Still `gen/plate_a.png` (Nano Banana 2.1, job 48a4c1b2), animated with Kling 3.0 Pro image-to-video (job cf05a973) on a locked camera; only the leaf shadows move. Measured camera drift: 0 px over 8 s.
- **Typography:** Aref Ruqaa Bold, ink #2A1A11 multiplied into the paper with a fine displacement filter for nib-edge texture. Line 1 is 150 px, line 2 is 84 px. Each word is revealed whole, shaped by the browser's Arabic engine, through a feathered right-to-left mask, so joins never break.
- **Grade:** warm balance, gentle contrast, vignette and fine film grain (ffmpeg, see `post/finish.sh`).

## Audio cue sheet

| Frames | Timecode | Stem | Element | Source | Locked to |
|---|---|---|---|---|---|
| f0–f102 | 00:00:00 → 00:03:12 | Music | Intro pad · G major (synth) | synthesised | the first line; hands over to the score |
| f0–f240 | 00:00:00 → 00:08:00 | SFX | Quiet study room tone (synth) | synthesised | the whole shot |
| f1–f28 | 00:00:01 → 00:00:28 | SFX | Paper settling | Mirelo · job be43026e | the shot fades in on the sheet |
| f10–f26 | 00:00:10 → 00:00:26 | SFX | Pen writing «كان» | Mirelo · job 4494ac61 (sliced) | that word's ink reveal |
| f31–f57 | 00:01:01 → 00:01:27 | SFX | Pen writing «فكرة.» | Mirelo · job 4494ac61 (sliced) | that word's ink reveal |
| f48–f240 | 00:01:18 → 00:08:00 | Music | Score · ElevenLabs Music v2.5 (piano, oud, pads) | Higgsfield job e8268f51 | builds under the strike, blooms as «مكان» completes, peaks into the logo |
| f64–f76 | 00:02:04 → 00:02:16 | SFX | Light air lift into the strike (synth) | synthesised | transition accent |
| f76–f94 | 00:02:16 → 00:03:04 | SFX | Decisive pen strike | Mirelo · job 5a2c4561 | the line crossing out «فكرة» |
| f105–f124 | 00:03:15 → 00:04:04 | SFX | Pen writing «والفكرة» | Mirelo · job 4494ac61 (sliced) | that word's ink reveal |
| f127–f139 | 00:04:07 → 00:04:19 | SFX | Pen writing «جاي» | Mirelo · job 4494ac61 (sliced) | that word's ink reveal |
| f142–f156 | 00:04:22 → 00:05:06 | SFX | Pen writing «يصير» | Mirelo · job 4494ac61 (sliced) | that word's ink reveal |
| f159–f168 | 00:05:09 → 00:05:18 | SFX | Pen writing «إلها» | Mirelo · job 4494ac61 (sliced) | that word's ink reveal |
| f171–f182 | 00:05:21 → 00:06:02 | SFX | Pen writing «مكان» | Mirelo · job 4494ac61 (sliced) | that word's ink reveal |
| f190–f240 | 00:06:10 → 00:08:00 | Music | Warm low G under the logo (synth) | synthesised | logo |
| f190–f240 | 00:06:10 → 00:08:00 | SFX | Logo reveal: soft G/D bell + airy shimmer | synthesised bell + Mirelo job 1fe7f7fa | the logo's ink appears |

Music automation: the score's bloom is ridden down about 6 dB from 5.25 s so «مكان» and the logo bell stay clear; the master fades out 7.60 → 7.985 s.

## Rebuild / edit

1. Change words, sizes, timings or positions in `post/compose.html` (the `W`, `STRIKE`, `LINE2` and `LOGO` constants, plus the CSS).
2. `python3 post/encode.py` re-renders all 240 frames and writes `post/timings.json`.
3. `python3 audio/mix_paper.py` re-syncs every sound to the new timings and writes the three WAVs.
4. `sh post/finish.sh` grades, adds grain, muxes and exports `renders/Kan_Paper_Teaser_Final.mp4`.
