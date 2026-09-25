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


def strip():
    samples = 700
    noise = band_limited_noise(1, samples)[0]
    ys = np.linspace(0, 1000, samples)
    trace = noise * 7
    trace = trace + 18 * np.exp(-(((ys - 620) / 45) ** 2)) * np.sin(ys / 2.7) * (ys > 580)
    points = " ".join(f"{30 + x:.1f},{y:.1f}" for x, y in zip(trace, ys))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 1000" preserveAspectRatio="none">\n'
        f'<polyline points="{points}" fill="none" stroke="{LINE_COLOR}" stroke-width="1" stroke-opacity="0.6" vector-effect="non-scaling-stroke"/>\n'
        "</svg>\n"
    )


def main():
    IMAGES.mkdir(exist_ok=True)
    (IMAGES / "helicorder.svg").write_text(helicorder())
    (IMAGES / "strip.svg").write_text(strip())
    print("wrote images/helicorder.svg and images/strip.svg")


if __name__ == "__main__":
    main()
