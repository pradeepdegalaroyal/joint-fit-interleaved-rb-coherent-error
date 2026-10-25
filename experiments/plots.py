"""Black/grey figures: phase contour, waterfall ablation, hatched grouped bars."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

plt.rcParams.update({"font.size": 10, "axes.grid": False})
HATCH = ["", "//", "xx", ".."]
GREYS = ["#ffffff", "#cccccc", "#888888", "#444444"]


def make_all(summ, g, fig, base, best, shots, cohs) -> None:
    # 1. phase diagram: where joint+weights beats independent IRB (RMSE ratio < 1)
    p = g.pivot(index="coh", columns="shots", values="ratio_joint_over_irb")
    fig1, ax = plt.subplots(figsize=(6.2, 4.6))
    X, Y = np.meshgrid(range(len(p.columns)), p.index.values)
    lv = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.2]
    cs = ax.contourf(X, Y, p.values, levels=lv, cmap="Greys", alpha=0.85)
    ax.contour(X, Y, p.values, levels=[0.5], colors="k", linestyles="--", linewidths=1.5)
    ax.plot(X.ravel(), Y.ravel(), "k+", ms=5)
    ax.set_xticks(range(len(p.columns)), [str(s) for s in p.columns])
    ax.set_xlabel("shots per sequence")
    ax.set_ylabel("coherent share of gate error")
    ax.set_title("RMSE ratio, joint+weights / IRB (dashed: 0.5; +: grid points)")
    fig1.colorbar(cs, label="RMSE ratio (below 1: joint fit wins)")
    fig1.tight_layout()
    fig1.savefig(fig / "fig1_phase_diagram.png", dpi=200)

    # 2. waterfall ablation at shots=100, coh=0.5 (nearest grid point)
    sh = min(shots, key=lambda s: abs(s - 100))
    co = min(cohs, key=lambda c: abs(c - 0.5))
    sub = summ[(summ.sweep == "grid") & (summ.shots == sh) & (summ.coh == co)]
    r = dict(zip(sub.method, sub.rmse_mean))
    names = list(r)
    steps = [("IRB baseline", r[names[0]], None),
             ("+ shot weights", r[names[1]] - r[names[0]], None),
             ("+ shared A,B (joint)", r[names[3]] - r[names[1]], None),
             ("joint + weights", r[names[3]], None)]
    fig2, ax = plt.subplots(figsize=(6.2, 4.2))
    cum = 0.0
    for i, (lab, v, _) in enumerate(steps):
        if i in (0, 3):
            ax.bar(i, v, color="#444444" if i == 0 else "#888888", edgecolor="k")
            cum = v
        else:
            ax.bar(i, v, bottom=cum, color="white", edgecolor="k", hatch="//")
            cum += v
        ax.text(i, max(cum, v) + 0.02 * r[names[0]], f"{v:+.2e}" if i in (1, 2) else f"{v:.2e}",
                ha="center", fontsize=8)
    ax.set_ylim(0, 1.2 * r[names[0]])
    ax.set_xticks(range(4), [s[0] for s in steps], fontsize=8)
    ax.set_ylabel("RMSE of gate-error estimate")
    ax.set_title(f"Ablation waterfall ({sh} shots, coherent share {co})")
    fig2.tight_layout()
    fig2.savefig(fig / "fig2_ablation_waterfall.png", dpi=200)

    # 3. grouped bars: readout-error sweep
    nz = summ[summ.sweep == "readout"]
    ros = sorted(nz.ro.unique())
    meths = list(r)
    fig3, ax = plt.subplots(figsize=(6.6, 4.2))
    w = 0.2
    for j, m in enumerate(meths):
        d = nz[nz.method == m].sort_values("ro")
        ax.bar(np.arange(len(ros)) + (j - 1.5) * w, d.rmse_mean, w, yerr=d.rmse_std,
               color=GREYS[j], edgecolor="k", hatch=HATCH[j], capsize=2, label=m)
    ax.set_xticks(range(len(ros)), [f"{x:.2f}" for x in ros])
    ax.set_xlabel("readout bit-flip probability")
    ax.set_ylabel("RMSE of gate-error estimate")
    ax.set_title("Readout-error robustness (100 shots, coherent share 0.5)")
    ax.legend(fontsize=7)
    fig3.tight_layout()
    fig3.savefig(fig / "fig3_readout_robustness.png", dpi=200)

    # 4. bias vs coherent share (markers/linestyles)
    fig4, ax = plt.subplots(figsize=(6.2, 4.2))
    big = max(shots)
    d0 = summ[(summ.sweep == "grid") & (summ.shots == big)]
    for m, mk, ls in zip(meths, "osv^", ["-", "--", ":", "-."]):
        d = d0[d0.method == m].sort_values("coh")
        ax.errorbar(d.coh, d.bias_mean * 1e3, d.bias_std * 1e3, color="k", marker=mk,
                    linestyle=ls, mfc="white", capsize=2, label=m)
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_xlabel("coherent share of gate error")
    ax.set_ylabel("mean estimate error (x 1e-3)")
    ax.set_title(f"Systematic bias of IRB-type estimates ({big} shots)")
    ax.legend(fontsize=7)
    fig4.tight_layout()
    fig4.savefig(fig / "fig4_bias_vs_coherence.png", dpi=200)
    plt.close("all")
