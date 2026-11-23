# كان يا مكان — Teaser 03 · Audio timeline

7.000 s · 30 fps · 48 kHz / 24-bit stereo. Frame numbers match the animation exactly (f0–f210).

| Frames | Timecode | Stem | Element | Locked to |
|---|---|---|---|---|
| f0–f70 | 00:00:00 → 00:02:10 | Music | Pad · D minor (nostalgia) | opening, under the reveals |
| f0–f210 | 00:00:00 → 00:07:00 | SFX | Room tone (warm, low-passed) | fades in 0–15, out 192–210 |
| f1–f22 | 00:00:01 → 00:00:22 | SFX | Paper texture | hairline frame breathes in |
| f6–f48 | 00:00:06 → 00:01:18 | SFX | Pen strokes ×4 (f6/14/22/30), panned R→L | each word's mask wipe |
| f10–f55 | 00:00:10 → 00:01:25 | Music | Piano D5 | first word lands |
| f35–f80 | 00:01:05 → 00:02:20 | Music | Piano A4 | between reveals |
| f46–f60 | 00:01:16 → 00:02:00 | SFX | Dot taps D6 / F6 / A6 | each diamond lands |
| f53–f98 | 00:01:23 → 00:03:08 | Music | Piano F5 | line complete |
| f53–f68 | 00:01:23 → 00:02:08 | SFX | Reverse swell | builds into the morph, peaks as the alef lifts |
| f57–f80 | 00:01:27 → 00:02:20 | Music | Oud A3 pickup | the «ما» flag warms |
| f59–f104 | 00:01:29 → 00:03:14 | Music | Pad · B♭/D swell (anticipation) | rises through the morph |
| f68–f94 | 00:02:08 → 00:03:04 | SFX | Granular sparkle + rising air | alef lifts, narrows, blurs out |
| f70–f102 | 00:02:10 → 00:03:12 | SFX | Twin whooshes converging to centre (speed-driven) | meem slides left, kaf slides right, the gap closes |
| f74–f97 | 00:02:14 → 00:03:07 | Music | Oud D4 risha tremolo, crescendo | tension while the gap closes; stops on contact |
| f80–f98 | 00:02:20 → 00:03:08 | SFX | Two falling glints | dots 2–3 drop and fade |
| f98–f210 | 00:03:08 → 00:07:00 | Music | Pad · D major, F→F♯ lift (the new place) | lands on the join |
| f100–f104 | 00:03:10 → 00:03:14 | SFX | Ink tap (click + wood + soft thump) | meem and kaf lock together |
| f100–f150 | 00:03:10 → 00:05:00 | SFX | Tonal ting D6/A6 | full stop brightens and pulses |
| f102–f147 | 00:03:12 → 00:04:27 | Music | Piano chord D–F♯–A + D5 | morph completes: musical lift |
| f122–f152 | 00:04:02 → 00:05:02 | SFX | Air rise + soft felt impact | «كان يا مكان.» rises and settles |
| f138–f166 | 00:04:18 → 00:05:16 | SFX | Fine hiss panned R→L | fatha rule draws right to left |
| f146–f210 | 00:04:26 → 00:07:00 | Music | Oud Hijaz descent A–G–F♯–E♭–D | slogan in → resolves on the logo |
| f146–f200 | 00:04:26 → 00:06:20 | SFX | Warm tonal shimmer + sparkle | slogan rises in |
| f150–f195 | 00:05:00 → 00:06:15 | Music | Piano A5 sparkle | phrase settles |
| f168–f210 | 00:05:18 → 00:07:00 | SFX | Soft air bloom | logo settles |
| f170–f210 | 00:05:20 → 00:07:00 | Music | Piano D3 + D2 bass | logo appears |
| f170–f210 | 00:05:20 → 00:07:00 | Music | Warm low D tone | logo |
| f176–f210 | 00:05:26 → 00:07:00 | Music | Piano D6 air | logo settles |

## Musical arc

- **0–2 s · Nostalgia:** D minor pad and three sparse piano notes (D5, A4, F5) under the pen strokes.
- **2–3.4 s · Anticipation:** the pad lifts to B♭/D while an oud tremolo on D4 builds and stops on the exact contact frame.
- **3.4 s · The new place:** the chord turns D major (F→F♯) as مـ joins كان, and a rolled piano chord lands with the ink tap.
- **4.9–7 s · Resolution:** an oud Hijaz descent (A–G–F♯–E♭–D) enters with the slogan and resolves on D as the logo appears, over a warm low tone; the reverb tail ends by 6.985 s.

## Mix

| File | Integrated | True peak |
|---|---|---|
| Final_Mix.wav / Kan_Ya_Makan_Final.wav | −14.0 LUFS | −1.3 dBTP |
| Background_Music.wav | −15.4 LUFS | −4.2 dBTP |
| Sound_Design.wav | −18.8 LUFS | −3.6 dBTP |

Stems carry the same master gain and limiter envelope as the final mix, so Music + SFX = Final mix.
Bus processing: 32 Hz high-pass, convolution reverb (music 2.4 s at 32 % wet, SFX 1.6 s at 16 %), 4× oversampled true-peak limiter at −1.3 dBTP.

Everything is synthesised by `audio/synth_kan_ya_makan.py` (additive piano, Karplus-Strong oud, detuned pads, filtered and granular noise). No samples or library audio, so there is nothing to license.
