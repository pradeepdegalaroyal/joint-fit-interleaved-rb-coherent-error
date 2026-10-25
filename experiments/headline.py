"""Headline numbers (results/headline.json) derived from results/*.csv."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def write(out: Path) -> dict:
    g = pd.read_csv(out / "ratio_grid.csv")
    s = pd.read_csv(out / "summary.csv")
    raw = pd.read_csv(out / "raw_results.csv")
    r = g["ratio_joint_over_irb"]
    h = {
        "ratio_mean_over_grid": round(float(r.mean()), 3),
        "ratio_min": round(float(r.min()), 3),
        "ratio_max": round(float(r.max()), 3),
        "cells_ratio_below_1": int((r < 1).sum()),
        "cells_total": int(len(r)),
    }
    base = [c for c in g.columns if c.startswith("IRB")][0]
    for sh, co in [(100, 0.4), (100, 0.6), (1000, 1.0), (25, 1.0)]:
        sel = g[(g.shots == sh) & (g.coh == co)]
        if sel.empty:
            continue
        row = sel.iloc[0]
        h[f"irb_rmse_s{sh}_c{co}"] = float(row[base])
        h[f"ratio_s{sh}_c{co}"] = round(float(row["ratio_joint_over_irb"]), 3)
    # shots dependence at coherent share 0 for IRB vs joint
    for m, key in [(base, "irb"), ("joint fit + shot weights", "joint")]:
        for sh in (25, 1000):
            sel = g[(g.shots == sh) & (g.coh == 0.0)]
            if not sel.empty:
                h[f"{key}_rmse_s{sh}_c0"] = float(sel.iloc[0][m])
    # seed-level win rate
    p = raw[raw.sweep == "grid"].pivot_table(index=["shots", "coh", "seed"], columns="method",
                                             values="rmse")
    h["seed_cells_joint_better"] = int((p["joint fit + shot weights"] < p[base]).sum())
    h["seed_cells_total"] = int(len(p))
    for ro in (0.0, 0.1):
        if s[(s.sweep == "readout") & (s.ro == ro)].empty:
            continue
        d = s[(s.sweep == "readout") & (s.ro == ro)].set_index("method")
        for m in d.index:
            h[f"readout{ro}|{m}|rmse"] = [float(d.loc[m, "rmse_mean"]), float(d.loc[m, "rmse_std"])]
    (out / "headline.json").write_text(json.dumps(h, indent=1))
    return h


if __name__ == "__main__":
    print(write(Path(__file__).resolve().parents[1] / "results"))
