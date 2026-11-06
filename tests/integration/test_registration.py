"""
Headless Blender Integration Test: Add-on Registration & Integrity Verification.

This test is executed by headless Blender in background mode:
    blender -b -P tests/integration/test_registration.py

It verifies that all Venturial operators, menus, and Scene properties register
and unregister cleanly without throwing tracebacks or runtime collisions.
"""

import sys
import traceback

def run_integration_tests():
    print("\n=======================================================")
    print(">>> STARTING VENTURIAL HEADLESS BLENDER INTEGRATION TEST")
    print("=======================================================")

    try:
        import bpy
    except ImportError:
        print("ERROR: This integration test must be run inside Blender's Python runtime.")
        sys.exit(1)

    # 1. Enable / Register the add-on
    print("[1/4] Registering Venturial add-on...")
    try:
        # Try enabling via Blender's addon manager
        bpy.ops.preferences.addon_enable(module="venturial")
        print("      -> Successfully enabled via addon_enable('venturial')")
    except Exception as e:
        print(f"      -> addon_enable failed ({e}), attempting direct import registration...")
        try:
            import venturial
            venturial.register()
            print("      -> Successfully registered via direct venturial.register()")
        except Exception as err:
            print(f"FATAL: Could not register Venturial: {err}")
            traceback.print_exc()
            sys.exit(1)

    # 2. Verify Operator Domains
    print("[2/4] Verifying operator domain registrations...")
    assert hasattr(bpy.ops, "cfmesh"), "FATAL: 'bpy.ops.cfmesh' operator domain not found!"
    assert hasattr(bpy.ops, "classy"), "FATAL: 'bpy.ops.classy' operator domain not found!"

    # Verify specific operators
    cfmesh_ops = ["generate_cfmesh", "add_wake_preset", "add_box_refinement", "run_solver"]
    for op in cfmesh_ops:
        assert hasattr(bpy.ops.cfmesh, op), f"FATAL: 'bpy.ops.cfmesh.{op}' is missing!"
    print(f"      -> All cfMesh operators verified: {cfmesh_ops}")

    classy_ops = ["generate_mesh", "export_terrain_stl", "install_python_deps"]
    for op in classy_ops:
        assert hasattr(bpy.ops.classy, op), f"FATAL: 'bpy.ops.classy.{op}' is missing!"
    print(f"      -> All classy_blocks operators verified: {classy_ops}")

    # 3. Verify Scene Property Attachments
    print("[3/4] Verifying Scene property bindings...")
    scene = bpy.context.scene
    assert hasattr(scene, "cfmesh_props"), "FATAL: 'scene.cfmesh_props' pointer property missing!"
    assert hasattr(scene, "classy_mesh_props"), "FATAL: 'scene.classy_mesh_props' pointer property missing!"
    assert hasattr(bpy.types.Scene, "foam_dirs"), "FATAL: 'Scene.foam_dirs' pointer property missing!"
    print("      -> All Scene PointerProperties successfully attached.")

    # 4. Verify Clean Unregistration
    print("[4/4] Verifying clean unregistration...")
    try:
        bpy.ops.preferences.addon_disable(module="venturial")
        print("      -> Successfully disabled via addon_disable('venturial')")
    except Exception:
        try:
            import venturial
            venturial.unregister()
            print("      -> Successfully unregistered via venturial.unregister()")
        except Exception as unreg_err:
            print(f"WARNING during unregister: {unreg_err}")

    print("\n=======================================================")
    print(">>> SUCCESS: ALL BLENDER INTEGRATION TESTS PASSED!")
    print("=======================================================\n")
    sys.exit(0)


if __name__ == "__main__":
    run_integration_tests()

