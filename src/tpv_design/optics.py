"""Transfer-matrix optics for planar multilayer spectral filters.

The implementation uses the characteristic-matrix formulation for coherent,
isotropic, non-magnetic layers. Thicknesses correspond only to the internal
finite layers; the incident and substrate media are semi-infinite.
"""
from __future__ import annotations

from typing import Iterable, Literal
import numpy as np

Polarization = Literal["s", "p"]


def _cos_theta(n0: complex, theta0_rad: float, n: complex) -> complex:
    """Return cos(theta) from Snell's law with a forward-propagating branch."""
    sin_theta = n0 * np.sin(theta0_rad) / n
    cos_theta = np.sqrt(1 - sin_theta**2 + 0j)
    # Choose branch corresponding to forward propagation / decay.
    if np.real(cos_theta) < 0:
        cos_theta = -cos_theta
    if np.real(cos_theta) == 0 and np.imag(cos_theta) < 0:
        cos_theta = -cos_theta
    return cos_theta


def _admittance(n: complex, cos_theta: complex, pol: Polarization) -> complex:
    if pol == "s":
        return n * cos_theta
    if pol == "p":
        return n / cos_theta
    raise ValueError("pol must be 's' (TE) or 'p' (TM)")


def multilayer_rt(
    wavelength_m: Iterable[float] | np.ndarray,
    n_layers: Iterable[complex],
    d_layers_m: Iterable[float],
    *,
    n_incident: complex = 1.0,
    n_substrate: complex = 1.0,
    angle_deg: float = 0.0,
    pol: Polarization = "s",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute R, T, A spectra for a coherent multilayer.

    Parameters
    ----------
    wavelength_m:
        Vacuum wavelengths in meters.
    n_layers:
        Refractive index of each finite layer. Values may be complex but are
        assumed wavelength independent in this baseline model.
    d_layers_m:
        Physical thickness of each finite layer in meters.
    n_incident, n_substrate:
        Semi-infinite incident and substrate refractive indices.
    angle_deg:
        Incidence angle in degrees in the incident medium.
    pol:
        's' for TE, 'p' for TM.

    Returns
    -------
    R, T, A : np.ndarray
        Power reflectance, transmittance, and absorptance.
    """
    wavelength_m = np.asarray(wavelength_m, dtype=float)
    n_layers = np.asarray(list(n_layers), dtype=complex)
    d_layers_m = np.asarray(list(d_layers_m), dtype=float)

    if wavelength_m.ndim != 1 or np.any(wavelength_m <= 0):
        raise ValueError("wavelength_m must be a 1D array of positive values")
    if len(n_layers) != len(d_layers_m):
        raise ValueError("n_layers and d_layers_m must have the same length")
    if np.any(d_layers_m <= 0):
        raise ValueError("all finite layer thicknesses must be positive")
    if not 0 <= angle_deg < 90:
        raise ValueError("angle_deg must satisfy 0 <= angle_deg < 90")

    theta0 = np.deg2rad(angle_deg)
    cos0 = _cos_theta(n_incident, theta0, n_incident)
    coss = _cos_theta(n_incident, theta0, n_substrate)
    eta0 = _admittance(n_incident, cos0, pol)
    etas = _admittance(n_substrate, coss, pol)

    cos_layers = np.array([_cos_theta(n_incident, theta0, n) for n in n_layers])
    eta_layers = np.array([
        _admittance(n, ct, pol) for n, ct in zip(n_layers, cos_layers)
    ])

    R = np.empty_like(wavelength_m)
    T = np.empty_like(wavelength_m)

    for idx, lam in enumerate(wavelength_m):
        M = np.eye(2, dtype=complex)
        for n, d, ct, eta in zip(n_layers, d_layers_m, cos_layers, eta_layers):
            delta = 2 * np.pi * n * d * ct / lam
            c = np.cos(delta)
            s = np.sin(delta)
            layer_M = np.array(
                [[c, -1j * s / eta], [-1j * eta * s, c]], dtype=complex
            )
            M = M @ layer_M

        B = M[0, 0] + M[0, 1] * etas
        C = M[1, 0] + M[1, 1] * etas
        denom = eta0 * B + C

        r = (eta0 * B - C) / denom
        t = 2 * eta0 / denom

        R[idx] = float(np.real_if_close(abs(r) ** 2))
        # Power-flux correction for dissimilar incident/substrate media.
        T[idx] = float(np.real(np.real(etas) / np.real(eta0) * abs(t) ** 2))

    A = 1.0 - R - T
    # Remove harmless floating-point noise for lossless stacks.
    A[np.abs(A) < 1e-12] = 0.0
    return R, T, A


def unpolarized_rt(
    wavelength_m: Iterable[float] | np.ndarray,
    n_layers: Iterable[complex],
    d_layers_m: Iterable[float],
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Average TE and TM power spectra for unpolarized light."""
    Rs, Ts, As = multilayer_rt(
        wavelength_m, n_layers, d_layers_m, pol="s", **kwargs
    )
    Rp, Tp, Ap = multilayer_rt(
        wavelength_m, n_layers, d_layers_m, pol="p", **kwargs
    )
    return 0.5 * (Rs + Rp), 0.5 * (Ts + Tp), 0.5 * (As + Ap)


def hemispherical_rt(
    wavelength_m: Iterable[float] | np.ndarray,
    n_layers: Iterable[complex],
    d_layers_m: Iterable[float],
    *,
    angles_deg: Iterable[float] | np.ndarray | None = None,
    n_incident: complex = 1.0,
    n_substrate: complex = 1.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Lambertian, unpolarized hemispherical average of R, T, A.

    The angular weighting is proportional to sin(theta) cos(theta), appropriate
    for integrating radiance over a hemisphere. The grid excludes 90 degrees
    to avoid the grazing-incidence singularity.
    """
    if angles_deg is None:
        angles_deg = np.linspace(0.0, 85.0, 36)
    angles_deg = np.asarray(list(angles_deg), dtype=float)
    if angles_deg.ndim != 1 or len(angles_deg) < 2:
        raise ValueError("angles_deg must contain at least two angles")
    if np.any((angles_deg < 0) | (angles_deg >= 90)):
        raise ValueError("angles must satisfy 0 <= angle < 90 degrees")

    theta = np.deg2rad(angles_deg)
    weights = np.sin(theta) * np.cos(theta)

    R_by_angle, T_by_angle, A_by_angle = [], [], []
    for angle in angles_deg:
        R, T, A = unpolarized_rt(
            wavelength_m,
            n_layers,
            d_layers_m,
            n_incident=n_incident,
            n_substrate=n_substrate,
            angle_deg=float(angle),
        )
        R_by_angle.append(R)
        T_by_angle.append(T)
        A_by_angle.append(A)

    R_by_angle = np.asarray(R_by_angle)
    T_by_angle = np.asarray(T_by_angle)
    A_by_angle = np.asarray(A_by_angle)

    norm = np.trapezoid(weights, theta)
    R_h = np.trapezoid(R_by_angle * weights[:, None], theta, axis=0) / norm
    T_h = np.trapezoid(T_by_angle * weights[:, None], theta, axis=0) / norm
    A_h = np.trapezoid(A_by_angle * weights[:, None], theta, axis=0) / norm
    return R_h, T_h, A_h
