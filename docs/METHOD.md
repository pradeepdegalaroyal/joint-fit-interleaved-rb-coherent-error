# Method

**Simulator.** Single-qubit channels are 4x4 Pauli transfer matrices (`src/irbfit/clifford.py`, `noise.py`).
Every Clifford is followed by a gate-independent reference noise (infidelity 3e-3, coherent part a Z
rotation, incoherent part T1/T2 decay with T2 = 1.5 T1). The interleaved gate (a fixed Clifford) carries
extra noise of infidelity 4e-3 (coherent part an X rotation). The **coherent share** splits both between
over-rotation and decay at fixed total infidelity. Survival probabilities are exact; counts are binomial
with a symmetric readout flip.

**Protocol.** Lengths m = 1, 10, 25, 50, 100, 150, 200, 300; 12 random sequences per length; S shots per
sequence; reference and interleaved curves on the same sequences.

**Baseline (standard quantum).** Interleaved RB: two independent 3-parameter fits `A p^m + B`, then
`r = (d-1)/d (1 - p_int / p_ref)`.

**Classical-statistics comparator.** Independent fits with binomial weights.

**Proposed.** Joint fit of both curves with shared `A, B` and binomial weights (4 parameters).

**Metric.** RMSE and bias of `r_est - r_true`, where `r_true` is the exact average infidelity of the interleaved
channel. Each cell is run 8 times per seed, 5 seeds; mean ± std over seeds.

**Ablation.** Baseline → add weights → add shared (A, B) (waterfall).

**Noise sweep.** Readout flip probability 0, 0.02, 0.05, 0.1 at 100 shots, coherent share 0.5.

**Scaling.** Shots {25, 50, 100, 200, 500, 1000} × coherent share {0, 0.2, ..., 1}.
