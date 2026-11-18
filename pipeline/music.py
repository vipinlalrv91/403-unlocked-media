"""Original Indian-style background music, composed in code (no samples, no copyright).

score(moods_with_durations, seed) -> float32 numpy array (mono, 44.1 kHz), crossfaded per scene.
Moods: devotional | happy | sad | adventure | calm
Instruments: tanpura drone, bansuri (flute) melody in a raga, temple bells, tabla-like percussion, soft strings pad.
"""
import math, random, wave
import numpy as np

SR = 44100
SA = 146.83  # D3 tonic

RAGAS = {  # semitones from Sa
    "bhupali": [0, 2, 4, 7, 9],            # bright, devotional/happy
    "mohanam": [0, 2, 4, 7, 9],
    "bhairavi": [0, 1, 3, 5, 7, 8, 10],    # tender / sad
    "hamsadhwani": [0, 2, 4, 7, 11],       # festive
    "kafi": [0, 2, 3, 5, 7, 9, 10],        # adventurous / folk
}
MOODS = {
    "devotional": dict(raga="bhupali", tempo=66, flute=0.9, bells=1.0, tabla=0.0, pad=0.6),
    "calm":       dict(raga="mohanam", tempo=60, flute=0.7, bells=0.4, tabla=0.0, pad=0.7),
    "happy":      dict(raga="hamsadhwani", tempo=96, flute=1.0, bells=0.5, tabla=0.8, pad=0.4),
    "sad":        dict(raga="bhairavi", tempo=54, flute=0.8, bells=0.2, tabla=0.0, pad=0.8),
    "adventure":  dict(raga="kafi", tempo=104, flute=0.8, bells=0.2, tabla=1.0, pad=0.5),
}


def _env(n, a, r):
    e = np.ones(n, np.float32)
    a = min(a, n // 2); r = min(r, n - a)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] = np.linspace(1, 0, r)
    return e


def tanpura(dur, rng):
    n = int(dur * SR); out = np.zeros(n, np.float32)
    seq = [SA * 1.5, SA * 2, SA * 2, SA]          # Pa Sa' Sa' Sa
    t_pluck, step, k = 0.0, 0.62, 0
    while t_pluck < dur:
        f = seq[k % 4]; m = int(min(3.2, dur - t_pluck) * SR); t = np.arange(m) / SR
        tone = np.zeros(m, np.float32)
        for h in range(1, 12):  # rich harmonics, upper ones shimmer (jawari)
            amp = (1 / h) * (1 + 0.6 * np.sin(2 * math.pi * (0.7 + 0.13 * h) * t)) if h > 3 else 1 / h
            tone += (amp * np.sin(2 * math.pi * f * h * t * (1 + 0.0004 * rng.uniform(-1, 1)))).astype(np.float32)
        tone *= np.exp(-t * 1.1).astype(np.float32) * _env(m, 200, 2000)
        s = int(t_pluck * SR); out[s:s + m] += tone[:n - s] * 0.09
        t_pluck += step; k += 1
    return out


def flute(dur, raga, tempo, rng):
    n = int(dur * SR); out = np.zeros(n, np.float32)
    scale = RAGAS[raga]; beat = 60 / tempo
    deg, t0 = 0, 0.6
    while t0 < dur - 0.5:
        phrase = rng.randint(3, 6)
        for i in range(phrase):
            deg = max(-2, min(7, deg + rng.choice([-2, -1, -1, 1, 1, 2, 0])))
            if i == phrase - 1: deg = rng.choice([0, 0, 3 if len(scale) > 3 else 0])  # resolve to Sa/Pa
            octv, idx = divmod(deg, len(scale))
            f = SA * 2 * 2 ** ((scale[idx] + 12 * octv) / 12)
            L = beat * rng.choice([1, 1, 2, 2, 3]) if i < phrase - 1 else beat * 4
            m = int(min(L, dur - t0) * SR)
            if m <= 0: break
            t = np.arange(m) / SR
            vib = 1 + 0.006 * np.sin(2 * math.pi * 5.2 * t) * np.clip(t / 0.3, 0, 1)
            ph = 2 * math.pi * f * np.cumsum(vib) / SR
            tone = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
            breath = np.convolve(np.random.default_rng(rng.randint(0, 1 << 30)).standard_normal(m), np.ones(12) / 12, "same") * 0.06
            note = (tone + breath).astype(np.float32) * _env(m, int(0.06 * SR), int(0.12 * SR))
            s = int(t0 * SR); out[s:s + m] += note[:n - s] * 0.11
            t0 += L
        t0 += beat * rng.choice([2, 3, 4])  # breathe between phrases
    return out


def bells(dur, density, rng):
    n = int(dur * SR); out = np.zeros(n, np.float32)
    if density <= 0: return out
    t0 = 0.3
    while t0 < dur:
        m = int(min(3.0, dur - t0) * SR); t = np.arange(m) / SR; f = SA * 4 * rng.choice([1, 1.5, 2])
        tone = sum(a * np.sin(2 * math.pi * f * p * t) for p, a in ((1, 1), (2.76, 0.5), (5.4, 0.25), (8.9, 0.1)))
        s = int(t0 * SR); out[s:s + m] += (tone * np.exp(-t * 2.2)).astype(np.float32)[:n - s] * 0.05
        t0 += rng.uniform(4, 8) / density
    return out


def tabla(dur, tempo, level):
    n = int(dur * SR); out = np.zeros(n, np.float32)
    if level <= 0: return out
    beat = 60 / tempo / 2
    pattern = ["dha", "dhin", "dhin", "dha", "dha", "dhin", "dhin", "dha", "dha", "tin", "tin", "ta", "ta", "dhin", "dhin", "dha"]
    i, t0 = 0, 0.0
    while t0 < dur:
        b = pattern[i % 16]; m = int(0.35 * SR); t = np.arange(m) / SR
        bayan = np.sin(2 * math.pi * (95 - 25 * t / 0.35) * t) * np.exp(-t * 9) if b in ("dha", "dhin") else 0
        dayan = np.sin(2 * math.pi * SA * 2 * t) * np.exp(-t * (22 if b in ("ta", "tin") else 14))
        hit = (0.9 * bayan + 0.5 * dayan).astype(np.float32)
        s = int(t0 * SR)
        if s < n: out[s:s + m] += hit[:n - s] * 0.12 * level * (1.0 if i % 4 == 0 else 0.75)
        t0 += beat; i += 1
    return out


def pad(dur, raga, level):
    n = int(dur * SR); t = np.arange(n) / SR
    third = RAGAS[raga][2]
    out = sum(np.sin(2 * math.pi * SA * 2 ** (iv / 12) * t * (1 + d)) for iv in (0, 7, third + 12) for d in (-0.002, 0.002))
    lfo = 0.6 + 0.4 * np.sin(2 * math.pi * 0.08 * t)
    return (out * lfo * 0.018 * level).astype(np.float32)


def segment(mood, dur, rng):
    m = MOODS.get(mood, MOODS["calm"])
    y = tanpura(dur, rng) + pad(dur, m["raga"], m["pad"]) + bells(dur, m["bells"], rng) + tabla(dur, m["tempo"], m["tabla"])
    if m["flute"]: y += flute(dur, m["raga"], m["tempo"], rng) * m["flute"]
    # simple room reverb (multi-tap echo)
    for dly, g in ((0.031, 0.35), (0.067, 0.25), (0.113, 0.18), (0.197, 0.12)):
        k = int(dly * SR); y[k:] += y[:-k] * g
    return y


def score(scenes, seed=0):
    """scenes: list of (mood, seconds). Returns crossfaded mono track."""
    rng = random.Random(seed); xf = int(0.8 * SR)
    total = int(sum(d for _, d in scenes) * SR); out = np.zeros(total + xf, np.float32); pos = 0
    for mood, d in scenes:
        seg = segment(mood, d + 0.8, rng); n = len(seg)
        seg[:xf] *= np.linspace(0, 1, xf); seg[-xf:] *= np.linspace(1, 0, xf)
        out[pos:pos + n] += seg[:len(out) - pos]; pos += int(d * SR)
    out = out[:total]
    peak = np.max(np.abs(out)) or 1
    return (out / peak * 0.8).astype(np.float32)


def write_wav(path, y):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
