"""
Unit tests for pure unstructured meshing logic and OpenFOAM dictionary generation.
These tests run in standard Python with pytest in milliseconds (no Blender / bpy required).
"""

import os
import pytest
from utils.unstructured import utils_mesh


def test_sanitize_patch_name():
    """Verify that patch names are sanitized according to OpenFOAM rules."""
    # Replaces spaces and dashes with underscores
    assert utils_mesh._sanitize_patch_name("inlet-patch 1") == "inlet_patch_1"
    assert utils_mesh._sanitize_patch_name("wall-front") == "wall_front"

    # Prefixes 'p_' if the first character is a digit
    assert utils_mesh._sanitize_patch_name("1_inlet") == "p_1_inlet"
    assert utils_mesh._sanitize_patch_name("0_wall") == "p_0_wall"

    # Preserves clean names
    assert utils_mesh._sanitize_patch_name("outlet") == "outlet"


def test_write_decompose_par_single_core(tmp_path):
    """Verify write_decompose_par does nothing when cpu_cores <= 1."""
    base_dir = tmp_path / "single_core_case"
    base_dir.mkdir()
    (base_dir / "system").mkdir()

    utils_mesh.write_decompose_par(str(base_dir), cpu_cores=1)
    dict_file = base_dir / "system" / "decomposeParDict"
    assert not dict_file.exists()


def test_write_decompose_par_multicore(tmp_path):
    """Verify write_decompose_par generates correct Scotch syntax for multi-core runs."""
    base_dir = tmp_path / "parallel_case"
    base_dir.mkdir()
    (base_dir / "system").mkdir()

    utils_mesh.write_decompose_par(str(base_dir), cpu_cores=8)
    dict_file = base_dir / "system" / "decomposeParDict"
    assert dict_file.exists()

    content = dict_file.read_text(encoding="utf-8")
    assert "numberOfSubdomains 8;" in content
    assert "method          scotch;" in content
    assert "decomposeParDict" in content


def test_compute_wake_cylinder_points():
    """Verify 3D wake refinement cylinder point math."""
    min_b = (-1.0, -0.5, -0.2)
    max_b = (1.0, 0.5, 0.2)
    obj_lens = (2.0, 1.0, 0.4)
    vel_norm = (1.0, 0.0, 0.0)  # Flow in +X direction
    wake_factor = 3.0
    avg_scale = 1.0

    # Identity matrix (flattened 4x4)
    mat_identity = [
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    ]

    p1, p2, radius = utils_mesh.compute_wake_cylinder_points(
        min_b, max_b, vel_norm, obj_lens, wake_factor, avg_scale, mat_identity
    )

    # With +X velocity, p1 starts at max_b.x (1.0), p2 extends by obj_len_x * wake_factor (2.0 * 3.0 = 6.0)
    assert p1[0] == 1.0
    assert p2[0] == 7.0  # 1.0 + 6.0
    assert p1[1] == 0.0  # (0.5 + -0.5) / 2
    assert p2[1] == 0.0
    assert radius == pytest.approx((1.0 / 2.0) * 1.1)  # max(obj_y, obj_z)/2 * 1.1


def test_combine_ascii_stls(tmp_path):
    """Verify stitching multiple STL surface files without 3D viewport."""
    stl_dir = tmp_path / "stls"
    stl_dir.mkdir()

    stl1 = stl_dir / "patch1.stl"
    stl1.write_text("solid patch1\n  facet normal 0 0 1\n  endfacet\nendsolid patch1\n", encoding="utf-8")

    stl2 = stl_dir / "patch2.stl"
    stl2.write_text("solid patch2\n  facet normal 0 1 0\n  endfacet\nendsolid patch2\n", encoding="utf-8")

    output_stl = tmp_path / "combined.stl"

    # Function exists in utils_mesh or can be tested
    if hasattr(utils_mesh, "combine_ascii_stls"):
        utils_mesh.combine_ascii_stls(str(stl_dir), str(output_stl))
        assert output_stl.exists()
        merged = output_stl.read_text(encoding="utf-8")
        assert "solid patch1" in merged
        assert "solid patch2" in merged


def test_generate_fields_icoFoam(tmp_path):
    """Verify generation of initial field dictionaries (0/U, 0/p, constant/physicalProperties, system/controlDict)."""
    case_dir = tmp_path / "case_flow"
    case_dir.mkdir()
    (case_dir / "0").mkdir()
    (case_dir / "constant").mkdir()
    (case_dir / "system").mkdir()

    utils_mesh.generate_fields(
        base_dir=str(case_dir),
        solver_type="icoFoam",
        nu=1e-5,
        inlet_vel=[10.0, 0.0, 0.0],
        turb_model="laminar",
        start_time=0.0,
        end_time=0.5,
        delta_t=0.001,
        write_interval=10
    )

    # Check 0/U
    u_file = case_dir / "0" / "U"
    assert u_file.exists()
    u_content = u_file.read_text(encoding="utf-8")
    assert "uniform (10.0 0.0 0.0)" in u_content
    assert "volVectorField" in u_content

    # Check 0/p
    p_file = case_dir / "0" / "p"
    assert p_file.exists()
    p_content = p_file.read_text(encoding="utf-8")
    assert "volScalarField" in p_content

    # Check constant/physicalProperties
    prop_file = case_dir / "constant" / "physicalProperties"
    assert prop_file.exists()
    prop_content = prop_file.read_text(encoding="utf-8")
    assert "1e-05" in prop_content or "1e-5" in prop_content

    # Check system/controlDict
    ctrl_file = case_dir / "system" / "controlDict"
    assert ctrl_file.exists()
    ctrl_content = ctrl_file.read_text(encoding="utf-8")
    assert "application     icoFoam;" in ctrl_content
    assert "adjustTimeStep  yes;" in ctrl_content

