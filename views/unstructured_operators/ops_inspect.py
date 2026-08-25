import bpy
import os
from .ops_utils import set_ui_error, clear_ui_status
from venturial.models.unstructured_properties import global_state


class CFMESH_OT_SetInspectBBox(bpy.types.Operator):
    bl_idname = "cfmesh.set_inspect_bbox"
    bl_label = "Set BBox from Selected Object"
    bl_description = "Auto-fills the inspection bounding box from the currently selected object(s)"

    def execute(self, context):
        selected = [o for o in context.selected_objects if o.type == 'MESH']
        if not selected:
            self.report({'ERROR'}, "No mesh object selected.")
            set_ui_error("Select a mesh object first.")
            return {'CANCELLED'}

        import mathutils
        # Accumulate world-space corners across all selected objects
        all_corners = []
        for obj in selected:
            bb = obj.bound_box           # 8 local corners
            mat = obj.matrix_world
            for corner in bb:
                all_corners.append(mat @ mathutils.Vector(corner))

        xs = [v.x for v in all_corners]
        ys = [v.y for v in all_corners]
        zs = [v.z for v in all_corners]

        props = context.scene.cfmesh_props
        props.inspect_bbox_min = (min(xs), min(ys), min(zs))
        props.inspect_bbox_max = (max(xs), max(ys), max(zs))

        self.report({'INFO'},
            f"BBox set: ({min(xs):.3f}, {min(ys):.3f}, {min(zs):.3f}) → "
            f"({max(xs):.3f}, {max(ys):.3f}, {max(zs):.3f})")
        return {'FINISHED'}


class CFMESH_OT_InspectRegion(bpy.types.Operator):
    bl_idname = "cfmesh.inspect_region"
    bl_label = "Inspect Region Quality"
    bl_description = (
        "Reads internal.vtu and reports mesh quality stats "
        "for cells inside the bounding box"
    )

    def execute(self, context):
        import xml.etree.ElementTree as ET
        props = context.scene.cfmesh_props
        case_dir = bpy.path.abspath(props.export_dir)

        # Ensure mesh exists
        if not os.path.isdir(os.path.join(case_dir, "constant", "polyMesh")):
            self.report({'ERROR'}, "No mesh found. Run 'Generate cfMesh' first.")
            set_ui_error("No mesh found. Generate mesh first.")
            return {'CANCELLED'}

        # ── 1. Find internal.vtu ────────────────────────────────────────────
        vtk_dir = os.path.join(case_dir, "VTK")
        vtu_path = None

        def find_vtu():
            if os.path.isdir(vtk_dir):
                # Walk through time dirs and grab the one at t=0 (quality fields)
                for d in sorted(os.listdir(vtk_dir)):
                    candidate = os.path.join(vtk_dir, d, "internal.vtu")
                    if os.path.isfile(candidate):
                        last = d.rsplit("_", 1)[-1]
                        try:
                            if float(last) == 0.0:
                                return candidate
                        except ValueError:
                            pass
                # Fall back to any internal.vtu if t=0 not found
                for d in sorted(os.listdir(vtk_dir)):
                    candidate = os.path.join(vtk_dir, d, "internal.vtu")
                    if os.path.isfile(candidate):
                        return candidate
            return None

        vtu_path = find_vtu()

        if not vtu_path:
            self.report({'INFO'}, "internal.vtu not found. Auto-generating quality VTK fields...")
            global_state.status_message = "Generating quality VTK files..."
            
            from .. import utils_system
            source_cmd = "source /usr/lib/openfoam/openfoam2412/etc/bashrc"
            cmd = f"{source_cmd} && checkMesh -writeAllFields -time 0 && foamToVTK -ascii -time 0"
            
            success, output = utils_system.run_cfmesh_command(cmd, case_dir)
            if success:
                vtu_path = find_vtu()

        if not vtu_path:
            self.report({'ERROR'},
                "Could not generate internal.vtu. Make sure OpenFOAM checkMesh/foamToVTK are working.")
            set_ui_error("No internal.vtu. Check solver log.")
            return {'CANCELLED'}

        clear_ui_status()
        global_state.status_message = "Inspecting region..."

        # ── 2. Parse VTU ────────────────────────────────────────────────────
        try:
            tree = ET.parse(vtu_path)
            root = tree.getroot()
            ugrid = root.find('UnstructuredGrid')
            piece = ugrid.find('Piece') if ugrid is not None else None
            if piece is None:
                raise Exception("Missing Piece in VTU.")

            # Points
            pts_elem = piece.find('Points/DataArray')
            if pts_elem is None or not pts_elem.text:
                raise Exception("No points in VTU.")
            raw_pts = [float(x) for x in pts_elem.text.split()]
            vertices = [(raw_pts[i], raw_pts[i+1], raw_pts[i+2])
                        for i in range(0, len(raw_pts), 3)]

            # Cell connectivity & offsets (to compute centroids)
            conn_elem    = piece.find('Cells/DataArray[@Name="connectivity"]')
            offsets_elem = piece.find('Cells/DataArray[@Name="offsets"]')
            if conn_elem is None or offsets_elem is None:
                raise Exception("No cell connectivity in VTU.")
            conn    = [int(x) for x in conn_elem.text.split()]
            offsets = [int(x) for x in offsets_elem.text.split()]

            # Build cell vertex lists and centroids
            centroids = []
            start = 0
            for off in offsets:
                cell_verts = conn[start:off]
                cx = sum(vertices[v][0] for v in cell_verts) / len(cell_verts)
                cy = sum(vertices[v][1] for v in cell_verts) / len(cell_verts)
                cz = sum(vertices[v][2] for v in cell_verts) / len(cell_verts)
                centroids.append((cx, cy, cz))
                start = off

            n_cells = len(centroids)

            # Read quality fields (all are CellData scalars)
            def read_cell_field(name):
                elem = piece.find(f'CellData/DataArray[@Name="{name}"]')
                if elem is None or not elem.text:
                    return None
                raw = [float(x) for x in elem.text.split()]
                nc = int(elem.get('NumberOfComponents', '1'))
                if nc == 3:
                    import math
                    return [math.sqrt(raw[i]**2 + raw[i+1]**2 + raw[i+2]**2)
                            for i in range(0, len(raw), 3)]
                return raw

            non_ortho_vals  = read_cell_field('nonOrthoAngle')
            skewness_vals   = read_cell_field('skewness')
            aspect_vals     = read_cell_field('cellAspectRatio')

        except Exception as e:
            self.report({'ERROR'}, f"Failed to read mesh file. Did you run the mesher first? Detail: {str(e)[:50]}")
            set_ui_error("Failed to read mesh result data.")
            return {'CANCELLED'}

        # ── 3. Spatial filter ────────────────────────────────────────────────
        bmin = props.inspect_bbox_min
        bmax = props.inspect_bbox_max

        # Check if BBox is default / empty
        if abs(bmin[0]-bmax[0]) < 1e-5 and abs(bmin[1]-bmax[1]) < 1e-5 and abs(bmin[2]-bmax[2]) < 1e-5:
            self.report({'ERROR'}, "Inspection bounding box is empty. Please select a mesh and click 'Set BBox from Selected Object' first.")
            set_ui_error("BBox is empty. Click 'Set BBox' first.")
            return {'CANCELLED'}

        in_region = []
        for i, (cx, cy, cz) in enumerate(centroids):
            if (bmin[0] <= cx <= bmax[0] and
                bmin[1] <= cy <= bmax[1] and
                bmin[2] <= cz <= bmax[2]):
                in_region.append(i)

        props.inspect_cells_count = len(in_region)

        if not in_region:
            # Calculate actual bounds of centroids for a helpful message
            all_cx = [c[0] for c in centroids]
            all_cy = [c[1] for c in centroids]
            all_cz = [c[2] for c in centroids]
            mesh_min = (min(all_cx), min(all_cy), min(all_cz))
            mesh_max = (max(all_cx), max(all_cy), max(all_cz))
            
            msg = (
                f"0 cells in BBox ({bmin[0]:.1f}, {bmin[1]:.1f}, {bmin[2]:.1f}) → "
                f"({bmax[0]:.1f}, {bmax[1]:.1f}, {bmax[2]:.1f}). "
                f"Mesh centroids are at ({mesh_min[0]:.1f}, {mesh_min[1]:.1f}, {mesh_min[2]:.1f}) → "
                f"({mesh_max[0]:.1f}, {mesh_max[1]:.1f}, {mesh_max[2]:.1f})."
            )
            self.report({'WARNING'}, msg)
            set_ui_error("0 cells found. Check box location!")
            global_state.status_message = "Inspect failed: 0 cells in BBox."
            return {'CANCELLED'}

        # ── 4. Compute stats ─────────────────────────────────────────────────
        def region_max(field_vals):
            if field_vals is None:
                return 0.0
            vals = [field_vals[i] for i in in_region if i < len(field_vals)]
            return max(vals) if vals else 0.0

        def region_mean(field_vals):
            if field_vals is None:
                return 0.0
            vals = [field_vals[i] for i in in_region if i < len(field_vals)]
            return sum(vals) / len(vals) if vals else 0.0

        props.inspect_max_nonortho  = region_max(non_ortho_vals)
        props.inspect_mean_nonortho = region_mean(non_ortho_vals)
        props.inspect_max_skewness  = region_max(skewness_vals)
        props.inspect_mean_skewness = region_mean(skewness_vals)
        props.inspect_max_aspect    = region_max(aspect_vals)

        global_state.status_message = (
            f"Inspect: {len(in_region)} cells | "
            f"MaxNonOrtho={props.inspect_max_nonortho:.1f}° "
            f"MaxSkew={props.inspect_max_skewness:.3f}"
        )
        self.report({'INFO'},
            f"Inspected {len(in_region)} of {n_cells} cells. "
            f"Max non-ortho: {props.inspect_max_nonortho:.1f}°, "
            f"Max skewness: {props.inspect_max_skewness:.3f}")
        return {'FINISHED'}
