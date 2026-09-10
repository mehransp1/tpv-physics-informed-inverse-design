# Processed simulation tables

Files in this folder use the canonical schema:

```text
wavelength_um,n,k
```

They are the tables loaded by the TMM simulation at runtime.

The initial eight GitHub tables are compact, error-controlled subsets of the uploaded full-resolution datasets. Every stored row is an actual source-data point; intermediate values are reconstructed by the same linear interpolation used by the simulator. The compact representation was selected to keep the repository lightweight while preserving wavelength dependence and absorption features.

Target compression tolerances for the initial library were approximately:

- maximum absolute interpolation error in `n`: 0.002
- maximum interpolation error in `log10(k + 1e-12)`: 0.1 decade

When you add a new source file to `../raw/` and run `python scripts/standardize_materials.py`, the local standardizer writes the full cleaned dataset here unless a later compression step is explicitly requested.

Never silently extrapolate these data beyond their tabulated wavelength ranges. The Python material loader raises an error outside the valid range by default.
