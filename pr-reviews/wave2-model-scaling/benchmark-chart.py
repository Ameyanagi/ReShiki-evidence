import sys, statistics, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src, out_png, out_md = sys.argv[1:4]
runs = collections.defaultdict(list)  # (side, workload) -> [median]
side = None
for line in open(src):
    p = line.strip().split(",")
    if p[0] == "RUN":
        side = p[1]
    elif p[0] == "PERF":
        runs[(side, p[1])].append(float(p[3]))
med = {k: statistics.median(v) for k, v in runs.items()}
nrounds = {k: len(v) for k, v in runs.items()}

def ms(v):
    return f"{v:,.0f}" if v >= 100 else (f"{v:.1f}" if v >= 1 else f"{v:.2f}")

BLUE, ORANGE, GRID, INK, MUTED = "#2a78d6", "#eb6834", "#e4e3df", "#0b0b0b", "#52514e"
panels = [
    ("Scene build (gallery)", "scene_primitives_{}", ["1x", "4x", "16x"], [483, 1932, 7728], "atoms"),
    ("Selection bounds (gallery)", "selection_bounds_{}", ["1x", "4x", "16x"], [483, 1932, 7728], "atoms"),
    ("Align left (gallery)", "align_left_{}", ["1x", "4x", "16x"], [483, 1932, 7728], "atoms"),
    ("Crossing gaps (gallery)", "crossing_gaps_{}", ["1x", "4x", "16x"], [483, 1932, 7728], "atoms"),
    ("Repeat render copy\n(two-attachment group)", "render_copy_shared_{}", ["1x", "4x", "16x"], [483, 1932, 7728], "atoms"),
    ("Ammonia column, scene", "ammonia_column_scene_{}", ["256", "1024", "4096"], [256, 1024, 4096], "labels"),
    ("Bond column, crossing gaps", "bond_column_crossing_gaps_{}", ["256", "1024", "4096"], [256, 1024, 4096], "bonds"),
    ("NMe column, scene", "condensed_column_scene_{}", ["256", "1024", "4096"], [256, 1024, 4096], "labels"),
    ("Captioned arrows, Align left", "labelled_arrows_align_left_{}", ["256", "1024", "4096"], [256, 1024, 4096], "arrows"),
    ("One collapsed group, Align left", "large_group_align_left_{}", ["256", "1024", "4096"], [256, 1024, 4096], "atoms in group"),
]
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK})
fig, axes = plt.subplots(2, 5, figsize=(15, 6.6), dpi=150)
fig.patch.set_facecolor("#fcfcfb")
for ax, (title, key, sizes, xs, unit) in zip(axes.flat, panels):
    ax.set_facecolor("#fcfcfb")
    b = [med[("base", key.format(s))] for s in sizes]
    h = [med[("head", key.format(s))] for s in sizes]
    # Proportional growth from the branch's smallest size.
    ax.plot(xs, [h[0] * x / xs[0] for x in xs], color="#a9a8a2", lw=1, ls=(0, (2, 2)), zorder=1)
    ax.plot(xs, b, color=ORANGE, lw=2, marker="o", ms=5, zorder=3, label="base 1d94f392")
    ax.plot(xs, h, color=BLUE, lw=2, marker="o", ms=5, zorder=3, label="branch 7154c93b")
    close = max(b[-1], h[-1]) / min(b[-1], h[-1]) < 1.8
    up, down = (5, -5) if close else (0, 0)
    hi_b = b[-1] >= h[-1]
    ax.annotate(ms(b[-1]), (xs[-1], b[-1]), textcoords="offset points", xytext=(7, up if hi_b else down), ha="left", va="center", color=MUTED, fontsize=8)
    ax.annotate(ms(h[-1]), (xs[-1], h[-1]), textcoords="offset points", xytext=(7, down if hi_b else up), ha="left", va="center", color=MUTED, fontsize=8)
    ax.set_xlim(xs[0] / 1.5, xs[-1] * 2.6)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xticks(xs); ax.set_xticklabels([f"{x:,}" for x in xs])
    ax.minorticks_off()
    ax.set_xlabel(unit, fontsize=8)
    ax.set_title(title, fontsize=9.5, color=INK, loc="left")
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
axes[0][0].set_ylabel("median ms (log)")
axes[1][0].set_ylabel("median ms (log)")
handles, labels = axes[0][0].get_legend_handles_labels()
handles.append(plt.Line2D([], [], color="#a9a8a2", lw=1, ls=(0, (2, 2))))
labels.append("grows in step with the drawing")
fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0))
fig.suptitle("reshiki-model release benchmarks, macOS arm64: median of interleaved runs, load average about 3 (lower is better)", y=0.95, fontsize=10, color=MUTED)
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(out_png, facecolor=fig.get_facecolor())

order = [k for k in dict.fromkeys(w for (_, w) in runs)]
with open(out_md, "w") as f:
    f.write("| Workload | Base ms | Branch ms | Base / branch |\n|---|---:|---:|---:|\n")
    for w in order:
        if ("base", w) in med and ("head", w) in med:
            b, h = med[("base", w)], med[("head", w)]
            f.write(f"| `{w}` | {ms(b)} | {ms(h)} | {b / h:.1f}× |\n")
print("rounds:", sorted(set(nrounds.values())))
