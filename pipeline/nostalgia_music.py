"""Original nostalgic background music composed in code (no samples, no copyright), for story reels.
Soft felt-piano arpeggios over a warm string pad, gentle vinyl crackle, slow I-vi-IV-V style progression.
nostalgia(duration_s, seed) -> float32 mono array at 44.1 kHz."""
import math
import numpy as np

SR = 44100
A4 = 440.0
def hz(m): return A4 * 2 ** ((m - 69) / 12)

# key of D major: D  Bm  G  A  |  D  F#m  G  A
PROG = [[62, 66, 69], [59, 62, 66], [55, 59, 62], [57, 61, 64],
        [62, 66, 69], [54, 57, 61], [55, 59, 62], [57, 61, 64]]
MELODY = [  # (bar, beat, midi, beats) gentle motif
    (0, 0, 78, 1.5), (0, 1.5, 76, 0.5), (0, 2, 74, 2),
    (1, 0, 73, 1), (1, 1, 71, 1), (1, 2, 74, 2),
    (2, 0, 71, 1.5), (2, 1.5, 69, 0.5), (2, 2, 67, 2),
    (3, 0, 69, 3), (3, 3, 0, 1),
    (4, 0, 78, 1.5), (4, 1.5, 79, 0.5), (4, 2, 81, 2),
    (5, 0, 78, 1), (5, 1, 76, 1), (5, 2, 73, 2),
    (6, 0, 74, 1.5), (6, 1.5, 76, 0.5), (6, 2, 71, 2),
    (7, 0, 69, 2), (7, 2, 73, 2),
]


def piano(f, dur, vel=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    tone = sum(a * np.sin(2 * math.pi * f * k * t + k) for k, a in ((1, 1.0), (2, 0.35), (3, 0.12), (4, 0.05)))
    env = np.exp(-t * (2.2 + f / 900)) * (1 - np.exp(-t * 300))
    return (tone * env * vel).astype(np.float32)


def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n, np.float32)
    for f in freqs:
        for det in (-0.6, 0.0, 0.7):
            y += np.sin(2 * math.pi * (f + det) * t).astype(np.float32)
    att = min(n, int(1.2 * SR)); rel = min(n, int(1.2 * SR))
    env = np.ones(n, np.float32); env[:att] = np.linspace(0, 1, att); env[-rel:] *= np.linspace(1, 0, rel)
    return y * env / (len(freqs) * 3)


def lowpass(y, a=0.08):
    out = np.empty_like(y); acc = 0.0
    # simple one-pole (vectorised in chunks for speed)
    for i in range(0, len(y), 4096):
        seg = y[i:i + 4096]; o = np.empty_like(seg)
        for j, v in enumerate(seg):
            acc += a * (v - acc); o[j] = acc
        out[i:i + 4096] = o
    return out


def nostalgia(dur, seed=1, bpm=72):
    rng = np.random.default_rng(seed)
    beat = 60 / bpm; bar = beat * 4
    n = int(dur * SR) + SR; y = np.zeros(n, np.float32)
    bars = int(math.ceil(dur / bar)) + 1
    for b in range(bars):
        ch = PROG[b % len(PROG)]; t0 = b * bar; i0 = int(t0 * SR)
        p = pad([hz(m - 12) for m in ch], bar + 0.8) * 0.22
        y[i0:i0 + len(p)] += p[:max(0, n - i0)]
        bass = piano(hz(ch[0] - 24), bar, 0.35); y[i0:i0 + len(bass)] += bass[:max(0, n - i0)]
        arp = [ch[0], ch[1], ch[2], ch[1] + 12 if ch[1] + 12 < 86 else ch[1], ch[2], ch[1], ch[0] + 12, ch[2]]
        for k, m in enumerate(arp):
            ti = int((t0 + k * beat / 2) * SR); note = piano(hz(m), 1.6, 0.16 + 0.04 * rng.random())
            y[ti:ti + len(note)] += note[:max(0, n - ti)]
        if b >= 2:  # melody enters after the intro
            for (mb, bt, m, ln) in MELODY:
                if mb != b % 8 or m == 0: continue
                ti = int((t0 + bt * beat) * SR); note = piano(hz(m), ln * beat + 1.2, 0.26)
                y[ti:ti + len(note)] += note[:max(0, n - ti)]
    y = y[:int(dur * SR)]
    # warmth: soft low-pass blend + vinyl crackle + slow wow
    y = 0.65 * y + 0.35 * np.convolve(y, np.ones(24, np.float32) / 24, mode="same")
    crackle = (rng.random(len(y)) > 0.9993).astype(np.float32) * rng.normal(0, 0.25, len(y)).astype(np.float32)
    hiss = rng.normal(0, 0.004, len(y)).astype(np.float32)
    y = y + crackle * 0.35 + hiss
    fade = min(len(y), int(2.0 * SR)); y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
    return (y / (np.max(np.abs(y)) + 1e-6) * 0.85).astype(np.float32)
