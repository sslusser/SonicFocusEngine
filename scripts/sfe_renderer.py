#!/usr/bin/env python3
"""
Sonic Focus Engine v0.1 renderer
- Frequency-centered ambient generator
- Chunked offline synthesis (fast, low memory)
- Continuous oscillator phase (no chunk seams)
- 50 ms overlap–add crossfade between chunks
- Stereo drift, gentle high-pass, deterministic seeds
- Writes to <repo>/wav/
"""
import argparse, math, random, datetime
from pathlib import Path

import numpy as np
import soundfile as sf

# ----------------- helpers -----------------
def repo_root() -> Path:
    # scripts/sfe_renderer.py -> repo root is parent of scripts/
    return Path(__file__).resolve().parents[1]

def ensure_wav_dir() -> Path:
    out_dir = repo_root() / "wav"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

def db_to_lin(db: float) -> float:
    return 10 ** (db / 20.0)

def lfo_sine(t: np.ndarray, rate_hz: float, depth: float, phase: float = 0.0) -> np.ndarray:
    return depth * np.sin(2 * np.pi * rate_hz * t + phase)

def pink_noise_voss(n: int) -> np.ndarray:
    """
    Simple Voss-McCartney style pink noise approximant.
    For ambience with crossfade, this is sufficient.
    """
    b = np.random.normal(0, 1, (8, n))  # fewer streams for speed
    for i in range(8):
        k = 2 ** i
        b[i] = np.convolve(b[i], np.ones(k) / k, mode="same")
    pn = b.sum(axis=0)
    pn /= (np.max(np.abs(pn)) + 1e-9)
    return pn.astype(np.float32)

def build_out_path(args) -> Path:
    wav_dir = ensure_wav_dir()
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ch = "st" if args.stereo else "mo"
    base = (args.out or f"sfe_{args.freq:.1f}hz_{args.minutes}m_{args.sr}sr_{args.bit}bit_{ch}_{ts}.wav").strip()
    if not base.lower().endswith(".wav"):
        base += ".wav"
    return wav_dir / Path(base).name

# ----------------- engine -----------------
def render(args) -> None:
    sr = int(args.sr)
    total_sec = int(args.minutes) * 60
    ch = 2 if args.stereo else 1
    subtype = "PCM_16" if args.bit == 16 else "PCM_24"

    # Determinism
    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    # v0.1 layer plan (Deep Flow-ish)
    f0 = float(args.freq)
    ratios = [1.0, 2.0, 3.0, 4.0]                  # fundamental + harmonics
    gains_db = [-16, -20, -24, -28]                # relative levels
    detune_hz = [0.00, 0.07, -0.09, 0.12]          # tiny beating
    amp_lfo_rate = [0.010, 0.006, 0.004, 0.003]
    amp_lfo_depth = [0.18, 0.16, 0.12, 0.10]

    # Pink-noise wash
    noise_gain_db = -32
    noise_lfo_rate = 0.005
    noise_lfo_depth = 0.35

    # Headroom and chunking
    master_gain = db_to_lin(-6.0)
    CHUNK_SEC = 5.0
    XF_MS = 50  # overlap-add crossfade
    n_chunk = int(sr * CHUNK_SEC)
    n_xf = max(1, int(sr * XF_MS / 1000.0))
    n_total = int(sr * total_sec)

    out_path = build_out_path(args)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # High-pass one-pole coefficient (25 Hz)
    hp_alpha = math.exp(-2 * math.pi * 25.0 / sr)

    # Fixed per-layer phases (continuous across chunks)
    layer_phase = [random.random() * 2 * np.pi for _ in ratios]

    with sf.SoundFile(out_path, mode="w", samplerate=sr, channels=ch, subtype=subtype) as f:
        written = 0
        t_start = 0.0

        # HP state for stereo
        prev_y_l = prev_x_l = 0.0
        prev_y_r = prev_x_r = 0.0

        # Previous tail for overlap-add
        prev_tail = None  # shape (n_xf, ch)

        while written < n_total:
            frames = min(n_chunk, n_total - written)
            t = (t_start + np.arange(frames)) / sr  # absolute time

            # ---------------- mono bed mix ----------------
            mix = np.zeros(frames, dtype=np.float32)

            # Drone + harmonics (continuous phase)
            for i, ratio in enumerate(ratios):
                freq = ratio * f0 + detune_hz[i]
                osc = np.sin(2 * np.pi * freq * t + layer_phase[i])
                amp = (1.0 + lfo_sine(t, amp_lfo_rate[i], amp_lfo_depth[i])) * 0.5
                mix += (osc * amp * db_to_lin(gains_db[i])).astype(np.float32)

            # Pink-noise wash (per chunk; crossfade masks seams)
            n = pink_noise_voss(frames)
            n_amp = (1.0 + lfo_sine(t, noise_lfo_rate, noise_lfo_depth)) * 0.5
            mix += (n * n_amp * db_to_lin(noise_gain_db)).astype(np.float32)

            # ------------- stereo drift then high-pass -------------
            if ch == 1:
                # Vectorized one-pole HP (mono)
                hp = np.empty_like(mix)
                hp[0] = 0.0
                hp[1:] = hp_alpha * (hp[:-1] + mix[1:] - mix[:-1])
                block = (hp * master_gain)[:, None]
            else:
                # stereo pan drift
                pan = 0.5 + 0.15 * np.sin(2 * np.pi * 0.002 * t + 1.3)  # 0..1
                left = mix * np.cos(pan * math.pi / 2)
                right = mix * np.sin(pan * math.pi / 2)

                # vectorized HP per channel with state carryover
                l = left
                hp_l = np.empty_like(l)
                hp_l[0] = hp_alpha * (prev_y_l + l[0] - prev_x_l)
                hp_l[1:] = hp_alpha * (hp_l[:-1] + l[1:] - l[:-1])
                prev_y_l, prev_x_l = float(hp_l[-1]), float(l[-1])

                r = right
                hp_r = np.empty_like(r)
                hp_r[0] = hp_alpha * (prev_y_r + r[0] - prev_x_r)
                hp_r[1:] = hp_alpha * (hp_r[:-1] + r[1:] - r[:-1])
                prev_y_r, prev_x_r = float(hp_r[-1]), float(r[-1])

                block = np.stack([hp_l, hp_r], axis=1) * master_gain

            # ------------- overlap–add crossfade -------------
            if prev_tail is not None and frames >= n_xf:
                fade_in = np.linspace(0.0, 1.0, n_xf, dtype=np.float32)[:, None]
                fade_out = 1.0 - fade_in
                block[:n_xf, :] = block[:n_xf, :] * fade_in + prev_tail * fade_out

            # prepare tail for next iteration
            if frames >= n_xf:
                prev_tail = block[-n_xf:, :].copy()
            else:
                prev_tail = block.copy()

            # soft safety limiter
            peak = float(np.max(np.abs(block)))
            if peak > 0.995:
                block *= (0.995 / peak)

            f.write(block)
            written += frames
            t_start += frames / sr

    print(f"Wrote: {out_path}  sr={sr}Hz  bit={args.bit}  ch={ch}  dur={args.minutes}m")

# ----------------- cli -----------------
def main():
    ap = argparse.ArgumentParser(description="Sonic Focus Engine v0.1 renderer (outputs to wav/ at repo root)")
    ap.add_argument("--freq", type=float, required=True, help="fundamental frequency in Hz, e.g. 136.1")
    ap.add_argument("--minutes", type=int, default=10, help="duration in minutes")
    ap.add_argument("--sr", type=int, default=44100, help="sample rate")
    ap.add_argument("--bit", type=int, choices=[16, 24], default=16, help="bit depth")
    ap.add_argument("--stereo", action="store_true", help="stereo output (default mono)")
    ap.add_argument("--seed", type=int, help="deterministic seed")
    ap.add_argument("--out", default="", help="basename for output file; saved into wav/")
    args = ap.parse_args()
    render(args)

if __name__ == "__main__":
    main()
