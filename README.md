# Physics-Informed Inverse Design for Thermophotovoltaic Systems

A physics-first research framework for modeling, optimizing, and eventually performing physics-informed inverse design of multilayer spectral filters for thermophotovoltaic (TPV) systems.

The project starts with a validated forward model before introducing machine learning. The immediate objective is a fast, traceable Python pipeline that maps multilayer design variables and real optical-property data to spectra and TPV performance metrics, then uses that model to generate training data for surrogate modeling and inverse design.

## Current status

**Phase 1: forward physics baseline — in progress.**

Implemented:

- Coherent Transfer Matrix Method (TMM) for planar multilayers
- TE (s) and TM (p) polarization
- Angle-resolved and Lambertian hemispherical averaging
- Reflectance `R(lambda)`, transmittance `T(lambda)`, absorptance `A(lambda)`
- Energy-conservation checks
- Wavelength-dependent complex refractive index `n(lambda) + i k(lambda)` per layer
- Expandable CSV/Excel optical-material library
- Strict material wavelength-range validation (no silent extrapolation)
- Planck blackbody spectral exitance
- GaSb cutoff from bandgap
- Above-bandgap photon flux and `Jsc`
- Ideal radiative-limit dark current `J0`
- `Voc`, maximum-power point, fill factor, and output power density
- Spectral efficiency, ideal cell efficiency, and no-recycling system efficiency
- Automated physics/unit tests and GitHub Actions CI

## Optical material library

The repository currently includes processed wavelength-dependent optical constants for:

| Material | Tabulated range (um) |
|---|---:|
| 30% porous SiO2 | 0.35–13.986 |
| Al2O3 | 0.21–10.0 |
| MgF2 | 0.20–10.007 |
| SiO2 | 0.05–14.5 |
| Ta2O5 | 0.5–1000 |
| TiO2 | 0.120–125.123 |
| ZnS | 0.389–12.2 |
| ZnSe | 0.5–21.739 |

Material data are organized as:

```text
data/materials/
├── raw/          # drop new original .csv/.xlsx/.xls files here
├── processed/    # simulation-ready wavelength_um,n,k tables
├── manifest.json # provenance, spectral coverage, representation metadata
└── README.md
```

To expand the simulation environment with a new optical material:

```bash
# 1. copy the source file into data/materials/raw/
# 2. standardize all raw files
python scripts/standardize_materials.py
```

The loader sorts and validates optical data, averages duplicate wavelength rows, and supports Excel as well as CSV. The solver refuses out-of-range material requests by default instead of extrapolating unknown optical constants.

See [`data/materials/README.md`](data/materials/README.md) for the data contract and provenance rules.

## Why physics first?

A neural network is only as trustworthy as the forward-physics data used to train it. For multilayer TPV filters, TMM is fast enough to explore large design spaces while retaining wave-interference physics. Using measured/tabulated `n(lambda)` and `k(lambda)` also allows the model to capture material dispersion and parasitic absorption that constant-index stacks miss.

## Examples

Install and run:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

Constant-index reference case:

```bash
python examples/quarter_wave_filter.py
```

Wavelength-dependent complex-index case using the material library:

```bash
python examples/dispersive_material_filter.py
```

The dispersive example builds a five-pair SiO2/TiO2 quarter-wave stack using the real part of each material index at the design wavelength for initial thicknesses, then evaluates the entire spectrum with wavelength-dependent complex indices.

## Model definitions

For filter transmission `T(lambda)` and blackbody hemispherical spectral exitance `M_lambda(T_e)`, the power incident on the cell is

```text
P_inc = integral T(lambda) M_lambda(T_e) d lambda
```

The current baseline reports

```text
eta_spectral = P(E >= Eg) / P_inc
```

Short-circuit current is calculated from transmitted above-bandgap photon flux. The electrical model is currently an ideal single-diode radiative-limit model, retained as a transparent baseline until validated GaSb EQE and recombination/loss data are incorporated.

Two efficiencies are reported intentionally:

- **Cell efficiency:** `Pmax / P_inc`
- **System efficiency (no recycling):** `Pmax / (sigma T_e^4)`

The second metric does not yet recover filter-reflected photons at the emitter; explicit photon recycling is a planned system-level extension.

## Repository structure

```text
.
├── README.md
├── ROADMAP.md
├── requirements.txt
├── pyproject.toml
├── data/materials/
│   ├── raw/
│   ├── processed/
│   ├── manifest.json
│   └── README.md
├── scripts/
│   └── standardize_materials.py
├── examples/
│   ├── quarter_wave_filter.py
│   └── dispersive_material_filter.py
├── src/tpv_design/
│   ├── __init__.py
│   ├── materials.py
│   ├── optics.py
│   ├── radiation.py
│   └── tpv.py
└── tests/
    ├── test_materials.py
    ├── test_optics.py
    └── test_radiation_tpv.py
```

## Next validation gates

1. Add a validated ZrO2 complex-index dataset so the original SiO2/ZrO2 TPV designs can be reproduced without constant-index assumptions.
2. Reproduce a known quarter-wave filter result from prior TPV work.
3. Reproduce graded-index and double-stack designs and quantify differences versus the earlier COMSOL model.
4. Replace the ideal GaSb electrical model with validated EQE/J-V and non-radiative loss data.
5. Freeze design-variable/material bounds and generate the first 10,000-design dataset.
6. Train baseline surrogate models before introducing physics-informed losses.
7. Perform inverse design and revalidate every candidate with the forward TMM model.

See [ROADMAP.md](ROADMAP.md) for the full plan.

## Scientific scope and limitations

This repository is a research baseline, not a device-performance claim. The current TMM assumes coherent, planar, isotropic, non-magnetic layers. Tabulated optical constants are treated as properties of the specific datasets supplied; they are not assumed to be universal for every deposition process or temperature. The TPV electrical model remains idealized. The next major milestone is quantitative reproduction of independently known TPV filter results before machine-learning training begins.
