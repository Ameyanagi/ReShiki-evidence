"""Render the before/after size table and bar chart from sizes.json."""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

data = json.loads(Path(sys.argv[1]).read_text())
out = Path(sys.argv[2])
MB = 1_000_000

INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
BEFORE, AFTER = "#a8a7a1", "#2a78d6"
GOOD = "#006300"
plt.rcParams.update({"font.family": "Helvetica", "font.size": 11})


def mb(value):
    return "—" if value is None else f"{value / MB:,.2f} MB"


def change(before, after):
    if before is None or after is None or before == 0:
        return ""
    pct = (after - before) / before * 100
    return f"{pct:+.2f}%" if abs(pct) < 0.1 else f"{pct:+.1f}%"


# Table
rows = data["table"]
fig_h = 0.85 + 0.36 * len(rows)
fig, ax = plt.subplots(figsize=(12.5, fig_h), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.axis("off")
cols = ["Platform", "What users get", "Before (main)", "After (branch)", "Change", "Source"]
xs = [0.0, 0.13, 0.43, 0.56, 0.69, 0.78]
top = 1 - 0.55 / fig_h
step = 0.36 / fig_h
ax.text(0, 1 - 0.12 / fig_h, data["table_title"], fontsize=13, weight="bold", color=INK, va="top",
        transform=ax.transAxes)
for x, c in zip(xs, cols):
    ax.text(x, top, c, weight="bold", color=MUTED, fontsize=10, va="center", transform=ax.transAxes)
ax.plot([0, 1.07], [top - step / 2] * 2, color=INK, lw=0.8, transform=ax.transAxes, clip_on=False)
for i, r in enumerate(rows):
    y = top - step * (i + 1)
    if i % 2 == 0:
        ax.add_patch(plt.Rectangle((0, y - step / 2), 1.07, step, color="#f1f0ec",
                                   transform=ax.transAxes, zorder=0, clip_on=False))
    ch = change(r["before"], r["after"])
    vals = [r["platform"], r["item"], mb(r["before"]), mb(r["after"]), ch, r["source"]]
    for j, (x, v) in enumerate(zip(xs, vals)):
        color = INK
        weight = "normal"
        if j == 4 and ch.startswith("-") and ch != "-0.05%":
            color, weight = GOOD, "bold"
        if j == 5:
            color = MUTED
        ax.text(x, y, v, fontsize=9.5 if j == 5 else 10.5, color=color, weight=weight,
                va="center", transform=ax.transAxes)
fig.savefig(out / "size_table.png", bbox_inches="tight", facecolor=SURFACE, pad_inches=0.25)
plt.close(fig)

# Bar chart: measured downloads only
bars = data["chart"]
fig, ax = plt.subplots(figsize=(10.5, 0.62 * len(bars) + 1.6), dpi=200)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)
h = 0.36
labels = [b["label"] for b in bars]
for i, b in enumerate(bars):
    y = len(bars) - 1 - i
    if b["before"] is not None:
        ax.barh(y + h / 2 + 0.01, b["before"] / MB, height=h, color=BEFORE, edgecolor=SURFACE, linewidth=1)
        ax.text(b["before"] / MB + 0.3, y + h / 2, f"{b['before'] / MB:.1f}", va="center", fontsize=9.5,
                color=MUTED)
    if b["after"] is not None:
        ax.barh(y - h / 2 - 0.01, b["after"] / MB, height=h, color=AFTER, edgecolor=SURFACE, linewidth=1)
        ch = change(b["before"], b["after"])
        ax.text(b["after"] / MB + 0.3, y - h / 2, f"{b['after'] / MB:.1f}  {ch}".rstrip(), va="center",
                fontsize=9.5, color=INK, weight="bold")
ax.set_yticks(range(len(bars)))
ax.set_yticklabels(labels[::-1], color=INK)
ax.set_xlabel("Download size (MB, 1 MB = 1,000,000 bytes)", color=MUTED)
ax.xaxis.grid(True, color=GRID, lw=0.8)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.tick_params(axis="y", length=0)
ax.tick_params(axis="x", colors=MUTED)
ax.set_xlim(0, max(max(b["before"] or 0, b["after"] or 0) for b in bars) / MB * 1.22)
from matplotlib.patches import Patch

ax.legend(handles=[Patch(color=BEFORE, label="Before: main"), Patch(color=AFTER, label="After: this branch")],
          loc="lower right", frameon=False)
ax.set_title(data["chart_title"], loc="left", fontsize=13, weight="bold", color=INK, pad=12)
fig.savefig(out / "size_chart.png", bbox_inches="tight", facecolor=SURFACE, pad_inches=0.25)
