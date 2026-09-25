from pathlib import Path

import numpy as np

from make_trace import band_limited_noise, lags, synthetic_signal

IMAGES = Path(__file__).resolve().parent.parent / "images"

TRACE = "#d6cfbf"
MUTED = "#8d877a"
ACCENT = "#cf6a50"
FAINT = "#2e2c27"
FONT = "B612 Mono, ui-monospace, monospace"


def polyline(xs, ys, color, width=1.2, opacity=1):
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    return f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{width}" stroke-opacity="{opacity}" stroke-linejoin="round"/>'


def label(x, y, text, color=MUTED, anchor="start", size=16):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{FONT}" font-size="{size}" text-anchor="{anchor}">{text}</text>'


def svg(width, height, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">\n' + "\n".join(body) + "\n</svg>\n"


def lag_axis(x0, x1, y, lag_min, lag_max, ticks):
    body = [f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{FAINT}"/>']
    for t in ticks:
        x = x0 + (t - lag_min) / (lag_max - lag_min) * (x1 - x0)
        body.append(f'<line x1="{x:.1f}" y1="{y}" x2="{x:.1f}" y2="{y + 5}" stroke="{MUTED}"/>')
        body.append(label(f"{x:.1f}", y + 24, f"{t:g}", anchor="middle", size=15))
    return body


def noise_figure():
    rng = np.random.default_rng(3)
    samples = 700
    xs = np.linspace(20, 620, samples)
    common = band_limited_noise(1, samples + 120)[0]
    a = common[:samples] + 0.2 * rng.standard_normal(samples)
    b = common[80:80 + samples] + 0.2 * rng.standard_normal(samples)
    signal = synthetic_signal()
    ccf = signal / np.abs(signal).max()
    body = [
        label(20, 22, "station A"),
        polyline(xs, 60 - 18 * a / np.abs(a).max() * 1.6, TRACE, 1),
        label(20, 112, "station B"),
        polyline(xs, 150 - 18 * b / np.abs(b).max() * 1.6, TRACE, 1),
        label(20, 212, "cross-correlation of A and B", ACCENT),
        polyline(np.linspace(20, 620, ccf.size), 260 - 34 * ccf, TRACE, 1.4),
    ]
    body += lag_axis(20, 620, 310, -60, 60, [-60, -30, 0, 30, 60])
    body.append(label(620, 350, "lag time (s)", anchor="end", size=15))
    return svg(640, 360, body)


def stack_figure():
    days = 24
    signal = synthetic_signal()
    signal = signal / np.abs(signal).max()
    daily = signal + 0.8 * band_limited_noise(days, signal.size)
    daily = daily[:, ::2]
    xs = np.linspace(20, 620, daily.shape[1])
    body = [label(20, 18, "daily cross-correlations")]
    top, spacing = 40, 11
    for day in range(days):
        y0 = top + day * spacing
        trace = daily[day] / np.abs(daily[day]).max()
        body.append(polyline(xs, y0 - 8 * trace, TRACE, 0.8, 0.6))
    stacked = daily.mean(axis=0)
    y0 = top + days * spacing + 42
    body.append(label(20, y0 - 34, f"stack of {days} days", ACCENT))
    body.append(polyline(xs, y0 - 26 * stacked / np.abs(stacked).max(), TRACE, 1.5))
    axis_y = y0 + 38
    body += lag_axis(20, 620, axis_y, -60, 60, [-60, -30, 0, 30, 60])
    body.append(label(620, axis_y + 40, "lag time (s)", anchor="end", size=15))
    return svg(640, axis_y + 50, body)


def dvv_figure():
    signal = synthetic_signal()
    window = (lags >= 18) & (lags <= 60)
    t = lags[window]
    reference = signal[window]
    stretch = 0.03
    current = np.interp(t / (1 + stretch), lags, signal)
    scale = 70 / np.abs(reference).max()
    xs = 20 + (t - 18) / 42 * 600
    body = [
        label(20, 22, "reference", MUTED),
        label(130, 22, "after a velocity drop", ACCENT),
        polyline(xs, 120 - scale * reference, MUTED, 1.2),
        polyline(xs, 120 - scale * current, ACCENT, 1.2),
        label(620, 210, "same wave, arriving later → dv/v &lt; 0", anchor="end", size=15),
    ]
    body += lag_axis(20, 620, 232, 18, 60, [20, 30, 40, 50, 60])
    body.append(label(620, 272, "lag time (s), coda", anchor="end", size=15))
    return svg(640, 282, body)


def helicorder():
    rows, samples = 12, 400
    noise = band_limited_noise(rows, samples)
    xs = np.linspace(0, 1200, samples)
    body = []
    for row in range(rows):
        y0 = 30 + row * 50
        trace = noise[row] * 5
        if row == 1:
            trace = trace + 22 * np.exp(-((xs - 1040) / 50) ** 2) * np.sin(xs / 3.1) * (xs > 990)
        body.append(polyline(xs, y0 + trace, "#8d877a", 1, 0.16))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600" preserveAspectRatio="none">\n' + "\n".join(body) + "\n</svg>\n"


def portrait():
    body = [
        '<rect x="0.5" y="0.5" width="399" height="499" fill="#1c1a17" stroke="#2e2c27"/>',
        label(200, 244, "your photo", MUTED, "middle", 16),
        label(200, 270, "images/portrait.jpg", "#5f5a50", "middle", 12),
    ]
    return svg(400, 500, body)


def main():
    IMAGES.mkdir(exist_ok=True)
    (IMAGES / "noise.svg").write_text(noise_figure())
    (IMAGES / "stack.svg").write_text(stack_figure())
    (IMAGES / "dvv.svg").write_text(dvv_figure())
    (IMAGES / "helicorder.svg").write_text(helicorder())
    (IMAGES / "portrait.svg").write_text(portrait())
    print("wrote noise.svg, stack.svg, dvv.svg, helicorder.svg and portrait.svg in images/")


if __name__ == "__main__":
    main()
