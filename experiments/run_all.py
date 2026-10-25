"""Reproduce every result and figure: python experiments/run_all.py [--quick]."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from irbfit.estimators import METHODS  # noqa: E402
from irbfit.study import run_cell, summarize  # noqa: E402
import headline  # noqa: E402
import plots  # noqa: E402

SEEDS = [0, 1, 2, 3, 4]


def sweep(configs, seeds, n_rep, tag):
    """Evaluate every config on every seed; one row per (config, seed, method)."""
    rows = []
    for cfg in configs:
        for s in seeds:
            errs = run_cell(1000 * s + cfg["shots"] + int(100 * cfg["coh"]), n_rep,
                            cfg["shots"], cfg["coh"], cfg.get("ro", 0.0))
            for m, e in errs.items():
                rmse, bias = summarize(e)
                rows.append({"sweep": tag, **cfg, "seed": s, "method": m,
                             "rmse": rmse, "bias": bias})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replot", action="store_true", help="redraw figures from results/")
    ap.add_argument("--quick", action="store_true", help="< 1 min smoke run")
    a = ap.parse_args()
    t0 = time.time()
    seeds = SEEDS[:2] if a.quick else SEEDS
    n_rep = 2 if a.quick else 8
    cohs = [0.0, 0.5, 1.0] if a.quick else [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    shots = [50, 500] if a.quick else [25, 50, 100, 200, 500, 1000]
    out = ROOT / ("results_quick" if a.quick else "results")
    fig = ROOT / ("figures_quick" if a.quick else "figures")
    out.mkdir(exist_ok=True)
    fig.mkdir(exist_ok=True)

    if a.replot:
        summ = pd.read_csv(out / "summary.csv")
        g = pd.read_csv(out / "ratio_grid.csv")
        plots.make_all(summ, g, fig, list(METHODS)[0], list(METHODS)[-1], shots, cohs)
        return
    grid = [{"shots": s, "coh": c} for s in shots for c in cohs]
    df_grid = pd.DataFrame(sweep(grid, seeds, n_rep, "grid"))
    ro = [0.0, 0.02, 0.05, 0.1] if not a.quick else [0.0, 0.05]
    noise = [{"shots": 100, "coh": 0.5, "ro": r} for r in ro]
    df_noise = pd.DataFrame(sweep(noise, seeds, n_rep, "readout"))
    df = pd.concat([df_grid, df_noise], ignore_index=True)
    df.to_csv(out / "raw_results.csv", index=False)

    summ = (df.groupby(["sweep", "shots", "coh", "ro", "method"], dropna=False)
              .agg(rmse_mean=("rmse", "mean"), rmse_std=("rmse", "std"),
                   bias_mean=("bias", "mean"), bias_std=("bias", "std"))
              .reset_index())
    summ.to_csv(out / "summary.csv", index=False)
    base, best = list(METHODS)[0], list(METHODS)[-1]
    g = summ[summ.sweep == "grid"].pivot_table(index=["shots", "coh"], columns="method",
                                               values="rmse_mean").reset_index()
    g["ratio_joint_over_irb"] = g[best] / g[base]
    g.to_csv(out / "ratio_grid.csv", index=False)
    plots.make_all(summ, g, fig, base, best, shots, cohs)
    headline.write(out)
    (out / "runtime.json").write_text(
        f'{{"seconds": {time.time() - t0:.1f}, "quick": {str(a.quick).lower()}}}')
    print(f"done in {time.time() - t0:.1f}s -> {out}")


if __name__ == "__main__":
    main()
