"""Material optical-constant library for TPV spectral-filter simulations.

The library is intentionally data-driven. New materials can be added by placing
CSV/XLS/XLSX files in ``data/materials/raw`` and running
``python scripts/standardize_materials.py``. Runtime simulations prefer the
standardized CSV tables in ``data/materials/processed``.

Each material table is represented as wavelength-dependent complex refractive
index n~(lambda) = n(lambda) + i k(lambda), where k >= 0 denotes absorption.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import json
import re

import numpy as np
import pandas as pd


SUPPORTED_SUFFIXES = {".csv", ".xlsx", ".xls"}


def repository_root() -> Path:
    """Return the repository root for an editable/source-tree installation."""
    return Path(__file__).resolve().parents[2]


def default_material_root() -> Path:
    return repository_root() / "data" / "materials"


def _canonical_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


@dataclass(frozen=True)
class MaterialData:
    """Tabulated wavelength-dependent optical constants for one material."""

    name: str
    wavelength_um: np.ndarray
    n: np.ndarray
    k: np.ndarray
    source_note: str | None = None
    file_path: Path | None = None

    def __post_init__(self) -> None:
        wl = np.asarray(self.wavelength_um, dtype=float)
        n = np.asarray(self.n, dtype=float)
        k = np.asarray(self.k, dtype=float)
        if wl.ndim != 1 or n.ndim != 1 or k.ndim != 1:
            raise ValueError("wavelength_um, n, and k must be one-dimensional")
        if not (len(wl) == len(n) == len(k)) or len(wl) < 2:
            raise ValueError("wavelength_um, n, and k must have equal length >= 2")
        if np.any(~np.isfinite(wl)) or np.any(~np.isfinite(n)) or np.any(~np.isfinite(k)):
            raise ValueError("material data must be finite")
        if np.any(wl <= 0):
            raise ValueError("wavelengths must be positive")
        if np.any(np.diff(wl) <= 0):
            raise ValueError("wavelengths must be strictly increasing")
        if np.any(k < 0):
            raise ValueError("extinction coefficient k must be non-negative")
        object.__setattr__(self, "wavelength_um", wl)
        object.__setattr__(self, "n", n)
        object.__setattr__(self, "k", k)

    @property
    def wavelength_range_um(self) -> tuple[float, float]:
        return float(self.wavelength_um[0]), float(self.wavelength_um[-1])

    def complex_index_um(
        self,
        wavelength_um: Iterable[float] | np.ndarray,
        *,
        extrapolate: bool = False,
    ) -> np.ndarray:
        """Interpolate n(lambda)+i*k(lambda) for wavelengths in micrometers."""
        x = np.asarray(wavelength_um, dtype=float)
        if np.any(~np.isfinite(x)) or np.any(x <= 0):
            raise ValueError("requested wavelengths must be finite and positive")
        lo, hi = self.wavelength_range_um
        if not extrapolate and (np.min(x) < lo or np.max(x) > hi):
            raise ValueError(
                f"{self.name} data cover {lo:g}-{hi:g} um, but requested range is "
                f"{np.min(x):g}-{np.max(x):g} um"
            )
        n_interp = np.interp(x, self.wavelength_um, self.n)
        k_interp = np.interp(x, self.wavelength_um, self.k)
        return n_interp + 1j * k_interp

    def complex_index(
        self,
        wavelength_m: Iterable[float] | np.ndarray,
        *,
        extrapolate: bool = False,
    ) -> np.ndarray:
        """Interpolate n(lambda)+i*k(lambda) for wavelengths in meters.

        This is the preferred interface for the TMM solver because the optics
        package uses SI units internally.
        """
        wavelength_m = np.asarray(wavelength_m, dtype=float)
        return self.complex_index_um(wavelength_m * 1e6, extrapolate=extrapolate)


OpticalMaterial = MaterialData


def _read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, header=None, dtype=str)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, header=None, dtype=str)
    raise ValueError(f"Unsupported material file type: {path.suffix}")


def parse_material_file(path: str | Path, *, name: str | None = None) -> MaterialData:
    """Parse a flexible user material file into a clean MaterialData object."""
    path = Path(path)
    frame = _read_table(path)
    if frame.shape[1] < 3:
        raise ValueError(f"{path.name} must contain at least three columns")

    first_three = frame.iloc[:, :3].copy()
    numeric = first_three.apply(pd.to_numeric, errors="coerce")
    valid = numeric.notna().all(axis=1)
    clean = numeric.loc[valid].copy()
    clean.columns = ["wavelength_um", "n", "k"]
    if len(clean) < 2:
        raise ValueError(f"{path.name} does not contain at least two numeric n,k rows")

    clean = clean.sort_values("wavelength_um")
    clean = clean.groupby("wavelength_um", as_index=False).mean(numeric_only=True)

    source_note = None
    for row in frame.astype(str).itertuples(index=False):
        text = " ".join(str(v) for v in row if str(v).lower() != "nan").strip()
        if text.lower().startswith("source:"):
            source_note = text
            break

    material_name = name or path.stem
    return MaterialData(
        name=material_name,
        wavelength_um=clean["wavelength_um"].to_numpy(float),
        n=clean["n"].to_numpy(float),
        k=clean["k"].to_numpy(float),
        source_note=source_note,
        file_path=path,
    )


def discover_material_files(
    material_root: str | Path | None = None,
    *,
    prefer_processed: bool = True,
) -> dict[str, Path]:
    """Discover material files by filename stem, case/punctuation-insensitively."""
    root = Path(material_root) if material_root is not None else default_material_root()
    search_dirs = (
        [root / "processed", root / "raw", root]
        if prefer_processed
        else [root / "raw", root / "processed", root]
    )
    found: dict[str, Path] = {}
    for directory in search_dirs:
        if not directory.exists():
            continue
        for path in sorted(directory.iterdir()):
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
                found.setdefault(_canonical_key(path.stem), path)
    return found


def list_materials(material_root: str | Path | None = None) -> list[str]:
    """List material names currently available to the simulator."""
    files = discover_material_files(material_root)
    return sorted(path.stem for path in files.values())


def load_material(
    name: str,
    *,
    material_root: str | Path | None = None,
    prefer_processed: bool = True,
) -> MaterialData:
    """Load a material by filename stem (e.g. 'SiO2', 'TiO2', 'ZnSe')."""
    files = discover_material_files(material_root, prefer_processed=prefer_processed)
    key = _canonical_key(name)
    if key not in files:
        available = ", ".join(sorted(path.stem for path in files.values())) or "none"
        raise KeyError(f"Material '{name}' not found. Available materials: {available}")
    return parse_material_file(files[key], name=files[key].stem)


def standardize_material_file(
    input_path: str | Path,
    output_path: str | Path,
    *,
    name: str | None = None,
) -> dict[str, object]:
    """Convert CSV/Excel optical constants into canonical wavelength_um,n,k CSV."""
    material = parse_material_file(input_path, name=name)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "wavelength_um": material.wavelength_um,
            "n": material.n,
            "k": material.k,
        }
    ).to_csv(output_path, index=False)
    lo, hi = material.wavelength_range_um
    return {
        "name": material.name,
        "input_file": Path(input_path).name,
        "processed_file": output_path.name,
        "rows": len(material.wavelength_um),
        "wavelength_min_um": lo,
        "wavelength_max_um": hi,
        "source_note": material.source_note,
    }


def standardize_material_library(
    material_root: str | Path | None = None,
) -> list[dict[str, object]]:
    """Standardize every raw material file and write a reproducibility manifest."""
    root = Path(material_root) if material_root is not None else default_material_root()
    raw_dir = root / "raw"
    processed_dir = root / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, object]] = []
    for input_path in sorted(raw_dir.iterdir()):
        if not input_path.is_file() or input_path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        output_path = processed_dir / f"{input_path.stem}.csv"
        manifest.append(standardize_material_file(input_path, output_path))

    with (root / "manifest.json").open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


available_materials = list_materials
