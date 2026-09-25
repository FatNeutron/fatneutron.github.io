import sys
from pathlib import Path

import numpy as np

SITE = Path(__file__).resolve().parent.parent

MAX_LAG = 60.0
SAMPLE_INTERVAL = 0.25
DAYS = 365
FRAMES = 16
DURATION = 5.0
DELAY = 0.4
WIDTH = 480
HEIGHT = 100
TRACE_COLOR = "#d6cfbf"
ZERO_LINE_COLOR = "#3a3730"
NOISE_LEVEL = 0.8
SEED = 7

rng = np.random.default_rng(SEED)
lags = np.arange(-MAX_LAG, MAX_LAG + SAMPLE_INTERVAL / 2, SAMPLE_INTERVAL)


def band_limited_noise(rows, samples):
    white = rng.standard_normal((rows, samples))
    freqs = np.fft.rfftfreq(samples, SAMPLE_INTERVAL)
    band = np.clip((freqs - 0.06) / 0.04, 0, 1) * np.clip((0.5 - freqs) / 0.1, 0, 1)
    noise = np.fft.irfft(np.fft.rfft(white, axis=1) * band, samples, axis=1)
    return noise / noise.std(axis=1, keepdims=True)


def wave_packet(t, arrival, frequency=0.17, chirp=0.006, width=5.5):
    tau = t - arrival
    return np.exp(-((tau / width) ** 2)) * np.cos(2 * np.pi * (frequency * tau + 0.5 * chirp * tau**2))


def synthetic_signal():
    arrival = 22.0
    direct = wave_packet(lags, arrival) + 0.7 * wave_packet(-lags, arrival)
    after = np.clip(np.abs(lags) - arrival, 0, None)
    envelope = (1 - np.exp(-after / 3)) * np.exp(-after / 20)
    coda = band_limited_noise(1, lags.size)[0] * envelope * np.where(lags > 0, 0.22, 0.15)
    return direct + coda


def with_synthetic_noise(signal):
    signal = signal / np.abs(signal).max()
    return signal + NOISE_LEVEL * band_limited_noise(DAYS, signal.size)


def load_days(path):
    data = np.load(path)
    if data.ndim == 1:
        return with_synthetic_noise(data)
    return data


def resample(days, points):
    old = np.linspace(0, 1, days.shape[1])
    new = np.linspace(0, 1, points)
    return np.array([np.interp(new, old, day) for day in days])


def running_stacks(days):
    counts = np.round(1 + (len(days) - 1) * np.linspace(0, 1, FRAMES) ** 3).astype(int)
    totals = np.cumsum(days, axis=0)
    return [totals[n - 1] / n for n in counts]


def to_path(stack):
    amplitude = stack / np.abs(stack).max()
    xs = np.linspace(0, WIDTH, stack.size)
    ys = HEIGHT / 2 - amplitude * (HEIGHT / 2 - 3)
    points = [f"{round(x, 1):g} {y:.1f}" for x, y in zip(xs, ys)]
    return "M" + points[0] + "L" + " ".join(points[1:])


def build_svg(frames):
    values = ";".join(frames)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" preserveAspectRatio="none">
<style>
:root{{color-scheme:dark}}
line{{stroke:{ZERO_LINE_COLOR};vector-effect:non-scaling-stroke}}
path{{fill:none;stroke:{TRACE_COLOR};stroke-width:1.3;stroke-linejoin:round;vector-effect:non-scaling-stroke}}
.still{{display:none}}
@media (prefers-reduced-motion:reduce){{.moving{{display:none}}.still{{display:inline}}}}
</style>
<line x1="{WIDTH / 2:g}" y1="0" x2="{WIDTH / 2:g}" y2="{HEIGHT}"/>
<path class="moving" d="{frames[0]}"><animate attributeName="d" begin="{DELAY:g}s" dur="{DURATION:g}s" fill="freeze" values="{values}"/></path>
<path class="still" d="{frames[-1]}"/>
</svg>
"""


def main():
    if len(sys.argv) > 1:
        days = load_days(sys.argv[1])
    else:
        days = with_synthetic_noise(synthetic_signal())
    if days.shape[1] > WIDTH + 1:
        days = resample(days, WIDTH + 1)
    frames = [to_path(stack) for stack in running_stacks(days)]
    (SITE / "trace.svg").write_text(build_svg(frames))
    print(f"wrote trace.svg: {len(days)} days, {days.shape[1]} samples per day")
    if len(days) != DAYS:
        print(f"set the day count in style.css to {len(days)} so the counter matches")


if __name__ == "__main__":
    main()
