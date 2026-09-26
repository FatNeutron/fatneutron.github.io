from pathlib import Path

import numpy as np

from make_trace import band_limited_noise

IMAGES = Path(__file__).resolve().parent.parent / "images"

LINE_COLOR = "#8d877a"
OPACITY = 0.35
ROWS = 12
SAMPLES = 400


def polyline(xs, ys):
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    return f'<polyline points="{points}" fill="none" stroke="{LINE_COLOR}" stroke-width="1" stroke-opacity="{OPACITY}" stroke-linejoin="round"/>'


def helicorder():
    noise = band_limited_noise(ROWS, SAMPLES)
    xs = np.linspace(0, 1200, SAMPLES)
    lines = []
    for row in range(ROWS):
        trace = noise[row] * 5
        if row == 10:
            trace = trace + 22 * np.exp(-(((xs - 1040) / 50) ** 2)) * np.sin(xs / 3.1) * (xs > 990)
        lines.append(polyline(xs, 30 + row * 50 + trace))
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600" preserveAspectRatio="none">\n' + "\n".join(lines) + "\n</svg>\n"


def periodic_noise(samples, fastest, seed):
    spectrum = np.random.default_rng(seed).standard_normal(samples // 2 + 1) * (1 + 1j)
    freqs = np.arange(spectrum.size)
    spectrum[freqs < 20] = 0
    spectrum[freqs > fastest] = 0
    noise = np.fft.irfft(spectrum, samples)
    return noise / noise.std()


def rule(horizontal):
    samples = 1200
    along = np.arange(samples + 1)
    noise = periodic_noise(samples, fastest=420, seed=11)
    wobble = np.append(noise, noise[0]) * 0.9
    for centre, size in ((330, 3.2), (870, 2.2)):
        width = np.clip(along - centre, 0, None)
        wobble += size * np.exp(-width / 18) * np.sin(width / 1.3) * (along >= centre)
    offsets = 5 + np.clip(wobble, -4.5, 4.5)
    if horizontal:
        points = " ".join(f"{a},{o:.2f}" for a, o in zip(along, offsets))
        box = "0 0 1200 10"
    else:
        points = " ".join(f"{o:.2f},{a}" for a, o in zip(along, offsets))
        box = "0 0 10 1200"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box}">\n'
        f'<polyline points="{points}" fill="none" stroke="#000" stroke-width="1" stroke-linejoin="round"/>\n'
        "</svg>\n"
    )


def main():
    IMAGES.mkdir(exist_ok=True)
    (IMAGES / "helicorder.svg").write_text(helicorder())
    (IMAGES / "rule.svg").write_text(rule(horizontal=True))
    (IMAGES / "rule-vertical.svg").write_text(rule(horizontal=False))
    print("wrote images/helicorder.svg, images/rule.svg and images/rule-vertical.svg")


if __name__ == "__main__":
    main()
