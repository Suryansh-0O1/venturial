"""
Unit tests for classy_blocks utility math (winding normalization, revolve vectors, degenerate checks).
Runs in pure Python (no Blender dependency).
"""

import pytest
from utils.classy import utils


def test_normalize_winding_correct():
    """Verify normalize_winding leaves properly wound face untouched."""
    # A counter-clockwise face on the XY plane pointing in +Z
    face_pts = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0]
    ]
    sweep_vec = [0.0, 0.0, 1.0]  # Extrude along +Z

    orig_pts = [list(p) for p in face_pts]
    utils.normalize_winding(face_pts, sweep_vec)
    assert face_pts == orig_pts


def test_normalize_winding_inverted():
    """Verify normalize_winding reverses inverted points to prevent inside-out hexes."""
    # A clockwise face on the XY plane pointing in -Z
    face_pts = [
        [0.0, 1.0, 0.0],
        [1.0, 1.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0]
    ]
    sweep_vec = [0.0, 0.0, 1.0]  # Extrude along +Z (opposite to face normal)

    utils.normalize_winding(face_pts, sweep_vec)
    # The list should have been reversed in place
    assert face_pts[0] == [0.0, 0.0, 0.0]
    assert face_pts[1] == [1.0, 0.0, 0.0]
    assert face_pts[2] == [1.0, 1.0, 0.0]
    assert face_pts[3] == [0.0, 1.0, 0.0]


def test_normalize_winding_zero_sweep_degenerate():
    """Verify RuntimeError is raised when the sweep vector magnitude is near zero."""
    face_pts = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0]
    ]
    zero_sweep = [0.0, 0.0, 0.0]

    with pytest.raises(RuntimeError, match="Degenerate geometry: The sweep vector is zero"):
        utils.normalize_winding(face_pts, zero_sweep)


def test_normalize_winding_orthogonal_degenerate():
    """Verify RuntimeError is raised when face normal is orthogonal to sweep (0-volume block)."""
    # Face normal is +Z
    face_pts = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0]
    ]
    # Sweep along +X (coplanar to face, orthogonal to normal)
    orthogonal_sweep = [1.0, 0.0, 0.0]

    with pytest.raises(RuntimeError, match="Degenerate geometry detected"):
        utils.normalize_winding(face_pts, orthogonal_sweep)


def test_compute_revolve_sweep():
    """Verify revolve sweep vector computation."""
    # Face centered at (1, 0, 0)
    face_pts = [
        [0.5, -0.5, 0.0],
        [1.5, -0.5, 0.0],
        [1.5,  0.5, 0.0],
        [0.5,  0.5, 0.0]
    ]
    origin = [0.0, 0.0, 0.0]
    axis = [0.0, 0.0, 1.0]  # Z-axis
    angle_deg = 90.0

    # Cross product of axis (0, 0, 1) and (center - origin) (1, 0, 0):
    # axis x d = (0*0 - 1*0, 1*1 - 0*0, 0*0 - 0*1) = (0, 1, 0) -> +Y direction
    sweep = utils.compute_revolve_sweep(face_pts, origin, axis, angle_deg)
    assert sweep[0] == pytest.approx(0.0)
    assert sweep[1] == pytest.approx(1.0)
    assert sweep[2] == pytest.approx(0.0)

    # Inverted angle should invert sweep
    sweep_neg = utils.compute_revolve_sweep(face_pts, origin, axis, -90.0)
    assert sweep_neg[1] == pytest.approx(-1.0)

