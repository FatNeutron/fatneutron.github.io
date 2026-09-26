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


def rule(horizontal):
    samples = 600
    wobble = band_limited_noise(1, samples)[0] * 0.5
    blip = np.zeros(samples)
    blip[410:440] = np.sin(np.arange(30) / 1.6) * np.hanning(30) * 2.2
    offsets = 3 + wobble + blip
    along = np.linspace(0, 1200, samples)
    if horizontal:
        points = " ".join(f"{a:.1f},{o:.2f}" for a, o in zip(along, offsets))
        box = "0 0 1200 6"
    else:
        points = " ".join(f"{o:.2f},{a:.1f}" for a, o in zip(along, offsets))
        box = "0 0 6 1200"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box}">\n'
        f'<polyline points="{points}" fill="none" stroke="#000" stroke-width="1"/>\n'
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
