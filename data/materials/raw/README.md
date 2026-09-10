# Raw material data drop folder

Put new optical-property source files here without editing them.

Accepted formats:

- `.csv`
- `.xlsx`
- `.xls`

Recommended filename examples:

- `ZrO2.csv`
- `HfO2.xlsx`
- `Si3N4_ALD_300C.xlsx`

The first three numeric columns should represent:

1. wavelength in micrometers (um)
2. refractive index `n`
3. extinction coefficient `k`

Header rows and a `Source:` note are allowed. After adding files, run:

```bash
python scripts/standardize_materials.py
```

The script writes cleaned simulation-ready CSV files into `../processed/` and refreshes `../manifest.json`.

Keep distinct datasets as distinct files when deposition process, porosity, phase, temperature, film thickness, or other material conditions differ. Do not overwrite one physical material condition with another just because the chemical formula is the same.
