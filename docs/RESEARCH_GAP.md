# Research gap

## State of the art (from the supplied literature)

Superconducting, atom-array and ion platforms now report error-corrected or below-threshold operation
(Acharya et al., 2023, 10.1038/s41586-022-05434-1; Zobrist et al., 2025, 10.1038/s41586-024-08449-y;
Bluvstein et al., 2024, 10.1038/s41586-023-06927-3; Sivak et al., 2023, 10.1038/s41586-023-05782-6;
Moses et al., 2023, 10.1103/PhysRevX.13.041052). These results rest on physical gate errors that are measured
with randomized-benchmarking-type protocols, and on noise characterisation that is cheap enough to repeat
during calibration (Kim et al., 2023, 10.1038/s41586-023-06096-3). The randomized-measurement toolbox
(Elben et al., 2023, 10.1038/s42254-022-00535-2) and the random-circuit review
(Fisher et al., 2023, 10.1146/annurev-conmatphys-031720-030658) describe the statistics of such
randomised experiments. Newer work shows that fidelity maps are increasingly used as inputs for
compilation (Du et al., 2027, 10.1016/j.future.2026.108830) and measurement reduction
(Matsumoto, 2027, 10.1007/s40314-026-03881-4), so a gate-error number with a calibrated uncertainty is
a design input, not just a report.

Note: the supplied brief tags every paper with the single role "other"; the roles in the table below are
assigned by citation count and date (landmark: highly cited, recent: 2027 issue, review: survey).

## Related work

| Paper | Year | Role | What it does | What it does NOT cover |
|---|---|---|---|---|
| Acharya et al., 10.1038/s41586-022-05434-1 | 2023 | landmark | Scales a surface-code logical qubit | How the underlying physical gate errors were estimated at a given shot budget |
| Zobrist et al., 10.1038/s41586-024-08449-y | 2025 | landmark | quantum error correction (QEC) below threshold | Statistical cost of calibrating the input gate errors |
| Sivak et al., 10.1038/s41586-023-05782-6 | 2023 | landmark | Real-time QEC beyond break-even | Estimator choice for gate error versus coherent error |
| Bluvstein et al., 10.1038/s41586-023-06927-3 | 2024 | landmark | Logical processor on atom arrays | Benchmark-estimator variance |
| Kim et al., 10.1038/s41586-023-06096-3 | 2023 | landmark | Utility before fault tolerance, noise characterisation at scale | Single-gate estimator efficiency |
| Moses et al., 10.1103/PhysRevX.13.041052 | 2023 | landmark | Trapped-ion processor benchmark | Fit-model sharing across benchmark curves |
| Elben et al., 10.1038/s42254-022-00535-2 | 2023 | review | Randomized-measurement toolbox | Interleaved gate-error fitting under coherent error |
| Fisher et al., 10.1146/annurev-conmatphys-031720-030658 | 2023 | review | Random-circuit physics | Parameter-estimation statistics |
| Wang et al., 10.15302/frontphys.2027.023301 | 2027 | recent review | variational quantum algorithms (VQAs) towards fault tolerance | Noise-characterisation budget |
| Du et al., 10.1016/j.future.2026.108830 | 2027 | recent | Compilation weighted by gate fidelity asymmetry | Uncertainty of the fidelity inputs |
| Matsumoto, 10.1007/s40314-026-03881-4 | 2027 | recent | Fewer measurements in erasure correction | Benchmarking-shot cost |
| Bravyi et al., 10.1038/s41586-024-07107-7 | 2024 | landmark | Low-overhead fault-tolerant memory | Physical-error estimation |

## The gap

Interleaved randomized benchmarking (IRB) is the standard way to get a single-gate error, and it is normally
analysed with two independent exponential fits. Two things are left open by the papers above: (i) with a
fixed, small shot budget, the independent fits waste information because the reference and interleaved curves
share the same state-preparation and measurement (SPAM) offsets, and (ii) the papers
treat the resulting number as given, without asking how large its error is when part of the gate error is
coherent. We test whether a **joint fit with shared SPAM parameters and binomial shot weights** lowers the
estimator error at equal shots, and where the coherent-error bias makes the estimator choice irrelevant.

**Hypothesis (falsifiable).** At 100 shots per sequence and a coherent share of 0.5, the joint weighted fit has
an root-mean-square error (RMSE) at least 20 % below independent unweighted IRB; at the largest shot count and a coherent share of
1.0 the RMSE of both is dominated by bias and the ratio is above 0.8.
**Metric:** RMSE of the estimated gate infidelity against the exact infidelity of the simulated channel,
mean ± std over 5 seeds.

**Scale.** Single-qubit Pauli-transfer-matrix simulation (exact), 24 Cliffords, no hardware data.

**Novelty (one sentence).** A paired, equal-shot comparison of independent and joint shot-weighted IRB fits across the
coherent-share / shot-budget plane, with the region where fitting cannot help mapped explicitly.
