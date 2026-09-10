"""Standardize every optical-constant file in data/materials/raw."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tpv_design.materials import standardize_material_library


def main() -> None:
    manifest = standardize_material_library(ROOT / "data" / "materials")
    print(f"Standardized {len(manifest)} materials:")
    for item in manifest:
        print(
            f"- {item['name']}: {item['rows']} rows, "
            f"{item['wavelength_min_um']:.4g}-{item['wavelength_max_um']:.4g} um"
        )


if __name__ == "__main__":
    main()
