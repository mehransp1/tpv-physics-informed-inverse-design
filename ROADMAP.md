# Research Roadmap

## Phase 1 — Forward physics baseline
- [x] Coherent multilayer Transfer Matrix Method (TMM)
- [x] TE/TM polarization support
- [x] Angle-resolved and Lambertian hemispherical averaging
- [x] Energy-conservation checks
- [x] Planck blackbody spectrum
- [x] Ideal radiative-limit TPV cell metrics
- [x] Wavelength-dependent complex optical constants `n(lambda) + i k(lambda)`
- [x] Expandable CSV/Excel material-property library
- [x] Initial material set: porous SiO2, Al2O3, MgF2, SiO2, Ta2O5, TiO2, ZnS, ZnSe
- [ ] Add validated ZrO2 optical constants for thesis-design reproduction
- [ ] Reproduce one validated thesis filter case
- [ ] Add real GaSb EQE / cell loss model

## Phase 2 — Dataset generation
- [ ] Define permitted material families and design variables
- [ ] Define common wavelength window from material-coverage constraints
- [ ] Latin-hypercube / Sobol design sampling
- [ ] Generate 10k pilot samples
- [ ] Add invalid-design / numerical-quality filters
- [ ] Scale to 50k–200k validated simulations
- [ ] Save design metadata, spectra, scalar metrics, and material provenance

## Phase 3 — Baseline optimization and validation
- [ ] Quarter-wave reference
- [ ] Graded-index reference
- [ ] Double-stack reference
- [ ] Compare against thesis / published targets
- [ ] Establish numerical error budget and acceptance criteria
- [ ] Compare constant-index vs dispersive/absorbing-material predictions

## Phase 4 — Surrogate modeling
- [ ] Random Forest baseline
- [ ] XGBoost baseline
- [ ] Fully connected neural-network surrogate
- [ ] Train/validation/test split by design family
- [ ] Calibrate uncertainty / out-of-distribution checks

## Phase 5 — Physics-informed learning
- [ ] Energy-conservation penalty
- [ ] Spectral smoothness / physical bounds
- [ ] TPV metric consistency loss
- [ ] Material/wavelength-domain validity constraints
- [ ] Compare data-only vs physics-informed surrogate

## Phase 6 — Inverse design
- [ ] Define target-performance vector
- [ ] Gradient-free inverse search on surrogate
- [ ] Physics re-validation with TMM
- [ ] Multi-objective Pareto front: efficiency vs power density vs manufacturability
- [ ] Reject candidates outside validated optical-property domains

## Phase 7 — Research-grade extensions
- [x] Dispersion and absorption from tabulated optical constants
- [ ] Finite emitter emissivity and view factor
- [ ] Photon recycling / spectral-filter feedback
- [ ] Temperature-dependent material properties
- [ ] Process-specific optical-constant variants and uncertainty
- [ ] Robust design under thickness and refractive-index tolerances
- [ ] Compare TMM-selected designs against a higher-fidelity solver
