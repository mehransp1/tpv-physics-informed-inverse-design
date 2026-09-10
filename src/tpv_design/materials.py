"""Wavelength-dependent optical-constant material library.

Material CSV files use three columns:
    wavelength_um, n, k

The complex refractive-index convention is n_complex = n + i*k, with k >= 0
representing absorption in the TMM implementation used by this project.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import numpy as np

BoundsMode = Literal["raise", "clip"]

_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "materials"

_ALIASES = {
    "sio2": "SiO2",
    "silica": "SiO2",
    "porous_sio2_30": "porous_SiO2_30",
    "30poroussio2": "porous_SiO2_30",
    "tio2": "TiO2",
    "al2o3": "Al2O3",
    "mgf2": "MgF2",
    "ta2o5": "Ta2O5",
    "zns": "ZnS",
    "znse": "ZnSe",
}


@dataclass(frozen=True)
class OpticalMaterial:
    name: str
    wavelength_um: np.ndarray
    n: np.ndarray
    k: np.ndarray

    @property
    def wavelength_range_um(self) -> tuple[float, float]:
        return float(self.wavelength_um[0]), float(self.wavelength_um[-1])

    def complex_index(
        self,
        wavelength_m: np.ndarray | list[float] | float,
        *,
        bounds: BoundsMode = "raise",
    ) -> np.ndarray:
        """Interpolate n(lambda)+i*k(lambda) onto wavelengths in meters.

        Linear interpolation is used between tabulated measurements. By
        default, requesting wavelengths outside the measured data range raises
        an error rather than silently extrapolating nonphysical values.
        """
        wavelength_m = np.asarray(wavelength_m, dtype=float)
        wavelength_um = wavelength_m * 1e6
        lo, hi = self.wavelength_range_um

        if bounds == "raise":
            if np.any(wavelength_um < lo) or np.any(wavelength_um > hi):
                requested_lo = float(np.min(wavelength_um))
                requested_hi = float(np.max(wavelength_um))
                raise ValueError(
                    f"{self.name} optical constants cover {lo:g}-{hi:g} um, "
                    f"but {requested_lo:g}-{requested_hi:g} um was requested"
                )
            query = wavelength_um
        elif bounds == "clip":
            query = np.clip(wavelength_um, lo, hi)
        else:
            raise ValueError("bounds must be 'raise' or 'clip'")

        n_interp = np.interp(query, self.wavelength_um, self.n)
        k_interp = np.interp(query, self.wavelength_um, self.k)
        return n_interp + 1j * k_interp


def available_materials(data_dir: str | Path | None = None) -> list[str]:
    directory = Path(data_dir) if data_dir is not None else _DEFAULT_DATA_DIR
    return sorted(path.stem for path in directory.glob("*.csv"))


def load_material(
    name: str,
    *,
    data_dir: str | Path | None = None,
) -> OpticalMaterial:
    """Load one standardized optical-constant CSV by material name."""
    directory = Path(data_dir) if data_dir is not None else _DEFAULT_DATA_DIR
    canonical = _ALIASES.get(name.lower(), name)
    path = directory / f"{canonical}.csv"
    if not path.exists():
        choices = ", ".join(available_materials(directory))
        raise FileNotFoundError(
            f"Unknown material {name!r}. Available materials: {choices}"
        )

    table = np.genfromtxt(path, delimiter=",", names=True)
    wavelength_um = np.atleast_1d(table["wavelength_um"]).astype(float)
    n = np.atleast_1d(table["n"]).astype(float)
    k = np.atleast_1d(table["k"]).astype(float)

    if not (
        len(wavelength_um) == len(n) == len(k)
        and len(wavelength_um) >= 2
        and np.all(np.diff(wavelength_um) > 0)
    ):
        raise ValueError(f"Invalid optical-constant table: {path}")
    if np.any(k < 0):
        raise ValueError(f"Extinction coefficient k must be nonnegative: {path}")

    return OpticalMaterial(canonical, wavelength_um, n, k)
