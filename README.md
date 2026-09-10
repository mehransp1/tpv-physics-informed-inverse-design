# Physics-Informed Inverse Design for Thermophotovoltaic Systems

A physics-first research framework for modeling, optimizing, and eventually performing physics-informed inverse design of multilayer spectral filters for thermophotovoltaic (TPV) systems.

The project deliberately starts with a validated forward model before introducing machine learning. The immediate objective is to create a fast and trustworthy Python pipeline that maps multilayer design variables to optical spectra and TPV performance metrics, then use that model to generate a large training dataset for surrogate modeling and inverse design.

## Current status

**Phase 1: forward physics baseline — in progress.**

Implemented:

- Coherent Transfer Matrix Method (TMM) for planar multilayers
- TE (s) and TM (p) polarization
- Angle-resolved spectra
- Unpolarized averaging
- Lambertian hemispherical angular averaging
- Reflectance `R(lambda)`, transmittance `T(lambda)`, absorptance `A(lambda)`
- Energy-conservation checks, `R + T + A = 1` for lossless stacks
- Planck blackbody spectral exitance
- GaSb cutoff from bandgap
- Above-bandgap photon flux and `Jsc`
- Ideal radiative-limit dark current `J0`
- `Voc`, maximum-power point, fill factor, and output power density
- Spectral efficiency, ideal cell efficiency, and a no-recycling system efficiency

## Why physics first?

A neural network is only as trustworthy as the forward-physics data used to train it. For multilayer TPV filters, TMM is fast enough to evaluate large design spaces while retaining the essential wave-interference physics. That makes it a practical dataset generator before moving to surrogate models or physics-informed neural networks.

## Baseline example

The first example is a five-pair SiO2/ZrO2 quarter-wave stack designed around 2.4 um and evaluated for an 1800 K blackbody emitter and an idealized GaSb cell.

> **Important:** the current material refractive indices are constant placeholders and the cell model is an ideal radiative-limit baseline. Results are not yet intended to reproduce experimental GaSb performance or thesis values. Dispersion, absorption, real EQE, non-radiative recombination, view factor, emitter emissivity, and photon recycling are planned validation steps.

Run:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python examples/quarter_wave_filter.py
```

The example writes plots into `results/` and prints the main TPV metrics.

## Model definitions

For a filter transmission spectrum `T(lambda)` and blackbody hemispherical spectral exitance `M_lambda(T_e)`, the power incident on the cell is

```text
P_inc = integral T(lambda) M_lambda(T_e) d lambda
```

The spectral efficiency used in this baseline is

```text
eta_spectral = P(E >= Eg) / P_inc
```

The short-circuit current density is calculated from transmitted above-bandgap photon flux assuming a constant EQE above the bandgap. The open-circuit voltage and maximum-power point use an ideal single-diode radiative-limit model.

Two efficiencies are reported intentionally:

- **Cell efficiency:** `Pmax / P_inc`, where `P_inc` is power transmitted through the filter to the cell.
- **System efficiency (no recycling):** `Pmax / (sigma T_e^4)`, which treats reflected emitter power as unrecovered. A later model will explicitly include reflected-photon recycling.

## Repository structure

```text
.
├── README.md
├── ROADMAP.md
├── requirements.txt
├── pyproject.toml
├── examples/
│   └── quarter_wave_filter.py
├── src/tpv_design/
│   ├── __init__.py
│   ├── optics.py
│   ├── radiation.py
│   └── tpv.py
└── tests/
    ├── test_optics.py
    └── test_radiation_tpv.py
```

## Near-term research milestones

1. Add wavelength-dependent complex optical constants for SiO2, ZrO2, TiO2, and HfO2.
2. Reproduce a known quarter-wave result from prior TPV work.
3. Reproduce graded-index and double-stack designs.
4. Replace the ideal GaSb electrical model with validated cell data and loss mechanisms.
5. Define parameter bounds and generate a 10,000-design pilot dataset.
6. Train baseline surrogates before adding physics-informed losses.
7. Perform inverse design and re-validate candidate structures with the forward model.

See [ROADMAP.md](ROADMAP.md) for the full research plan.

## Scientific scope and limitations

This repository is currently a research baseline, not a device-performance claim. The present TMM solver treats each layer as coherent, isotropic, planar, and non-magnetic. The starter example uses wavelength-independent refractive indices. The TPV electrical model is intentionally idealized to establish a transparent physics pipeline before adding empirical parameters.

The next validation gate is to reproduce an independently known multilayer TPV result before any machine-learning model is trained.
