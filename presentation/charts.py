import math


def _fmt_exp(v: float) -> str:
    v = round(v, 1)
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.1f}K"
    return f"{v:,.1f}"


def curve_svg(gamma: float, base_exp: float) -> str:
    gamma = round(gamma, 2)
    W, H = 500, 300
    padL, padR, padT, padB = 64, 18, 18, 44
    plotW = W - padL - padR
    plotH = H - padT - padB

    levels = list(range(1, 51))
    costs = [base_exp * (n ** gamma) for n in levels]

    cmin = min(costs)
    cmax = max(costs)
    span = cmax - cmin

    def px(i):
        return padL + i * plotW / (len(levels) - 1)

    def py(c):
        if span < 1e-9:
            return padT + plotH * 0.5
        return padT + plotH * (1 - (c - cmin) / span)

    pts = [(px(i), py(costs[i])) for i in range(len(levels))]
    path = " ".join(
        ("M" if i == 0 else "L") + f"{p[0]:.2f} {p[1]:.2f}"
        for i, p in enumerate(pts)
    )

    # Y axis: 5 evenly-spaced ticks from cmin to cmax
    y_ticks = [cmin + (cmax - cmin) * t for t in [0, 0.25, 0.5, 0.75, 1.0]]
    grid_lines = "".join(
        f'<line x1="{padL}" y1="{py(v):.1f}" x2="{W - padR}" y2="{py(v):.1f}" '
        f'stroke="#2e2e2e" stroke-width="1"/>'
        for v in y_ticks
    )
    y_labels = "".join(
        f'<text x="{padL - 8}" y="{py(v):.1f}" dominant-baseline="middle" '
        f'text-anchor="end" fill="#7d7d7d" font-size="11" '
        f'font-family="Spline Sans Mono,ui-monospace,monospace">{_fmt_exp(v)}</text>'
        for v in y_ticks
    )

    # X axis: label every 10 levels (1, 10, 20, 30, 40, 50)
    x_label_levels = [1, 10, 20, 30, 40, 50]
    x_labels = "".join(
        f'<text x="{px(n - 1):.1f}" y="{padT + plotH + 20}" text-anchor="middle" '
        f'fill="#7d7d7d" font-size="11" font-family="Figtree,sans-serif">{n}</text>'
        for n in x_label_levels
    )

    # Highlight dots only at labeled x positions
    dots = "".join(
        f'<circle cx="{px(n - 1):.2f}" cy="{py(costs[n - 1]):.2f}" r="4" fill="#534AB7"/>'
        for n in x_label_levels
    )

    return f"""
<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto" role="img" aria-label="EXP cost per level">
  {grid_lines}
  {y_labels}
  {x_labels}
  <text x="{padL + plotW // 2}" y="{H - 4}" text-anchor="middle"
        fill="#5e5e5e" font-size="11" font-family="Figtree,sans-serif">level →</text>
  <path d="{path}" fill="none" stroke="#534AB7" stroke-width="2.5"
        stroke-linejoin="round" stroke-linecap="round"/>
  {dots}
</svg>
<div style="margin-top:10px;padding-top:10px;border-top:1px solid #2c2c2c;
            display:flex;align-items:center;gap:8px">
  <span style="width:14px;height:14px;border-radius:3px;background:#534AB7;display:inline-block"></span>
  <span style="font-size:12px;color:#aeaeae">EXP Threshold
    <span style="font-family:'Spline Sans Mono',monospace">(γ = {gamma:.2f})</span>
  </span>
</div>
"""
