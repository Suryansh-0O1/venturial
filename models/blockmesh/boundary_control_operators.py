from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty
import bpy
import bmesh
import random
from mathutils.bvhtree import BVHTree

# Converts a face from string to list of integers,
# example: print(face_strtolist("(9 0 8 7)")) = [9, 0, 8, 7]


def face_strtolist(string):
    # Add error handling to avoid errors during parsing
    return [int(s) for s in string[1: -1].split() if s.isdigit()]

class VNT_OT_New_Boundary(Operator):
    bl_idname = "vnt.new_boundary"
    bl_label = "New Boundary"
    bl_description = "Add a new boundary to the list"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        cs = context.scene
        data = cs.face_name

        r1 = layout.row(align=True)
        r1.label(text="Boundary Name:")
        r1.prop(data, "facename")

        r2 = layout.row(align=True)
        r2.label(text="Boundary Condition:")
        r2.prop(cs, "bdclist")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def execute(self, context):   
        """
        Executes the operator to process selected faces in the active object in Blender.
        This function performs the following tasks:
        1. Checks if the active object is in Edit Mode and if faces are selected.
        2. Validates that selected faces have 3 or 4 vertices (triangles or quads).
        3. Processes triangular faces to handle duplicate vertices and block names.
        4. Adds selected face information to a custom list in the scene, including:
           - Face name
           - Face description
           - Face color
           - Face type
           - Object name
        5. Assigns a material to the selected faces.
        Args:
            context (bpy.types.Context): The context in which the operator is executed.
        Returns:
            set: A set containing {'FINISHED'} if the operation completes successfully.
        Notes:
            - `sel_v` is a list of lists, where each inner list contains the vertex indices
              of a selected face in the active object.
            - If a face has more than 4 vertices, an informational message is reported.
            - If no face name is provided, an informational message is reported.
        """
        scn = context.scene 
        obj = context.object

        if obj:
            if obj.mode == 'EDIT':
                face_check = True
                bm = bmesh.from_edit_mesh(obj.data)
                vertices = bm.verts
                sel_v = [[v.index for v in f.verts]
                         for f in bm.faces if f.select]
                for i in sel_v:
                    if len(i) > 4:
                        face_check = False
                        break
                    elif len(i) == 3:
                        # i.append(i[-1])
                        BN = []  # Block Names
                        for w in scn.simblk:
                            BN.append(w.name)
                        seen = set()
                        result = []
                        for item in BN:
                            if item not in seen:
                                seen.add(item)
                                result.append(item)
                        BV = []  # Block Vertices
                        for j in result:
                            m = []
                            for q in range(0, len(scn.simblk)):
                                if scn.simblk[q].name == j:
                                    m.append(scn.simblk[q].index)
                            BV.append(m)
                        brep_verts = []
                        for rv in BV:
                            s = [item for item, count in collections.Counter(
                                rv).items() if count > 1]
                            if len(s) > 0:
                                brep_verts.append(s)
                        rep_v = []
                        for j in brep_verts:
                            for c in j:
                                rep_v.append(c)
                        for v in range(0, len(i)):
                            if i[v] in list(set(rep_v)):
                                i.insert(v, i[v])
                                break
                    else:
                        pass
                if face_check == False:
                    self.report(
                        {'INFO'}, "A selected Face has more than 4 vertices.")
                else:
                    str_fac = []
                    sel_fac_list = []
                    for fac in sel_v:
                        str_fac = []
                        for i in fac:
                            str_fac.append(str(i))
                        M = "("
                        for j in str_fac:
                            if j == str_fac[0]:
                                M = M + "" + j
                            else:
                                M = M + " " + j
                        M = M + ")"
                        sel_fac_list.append(M)
                    if not scn.face_name.facename.strip():
                        self.report(
                            {'INFO'}, "Name the Face to add to list")
                    else:
                        clr = self.get_random_color()
                        for i in sel_fac_list:
                            item = scn.fcustom.add()
                            item.name = i
                            item.face_des = scn.face_name.facename
                            item.face_clr = clr
                            item.face_type = scn.bdclist
                            item.face=bm.faces[sel_fac_list.index(i)]
                            # bpy.ops.object.material_slot_add()
                            mat_clr = bpy.data.materials.new("clr")
                            mat_clr.diffuse_color = clr
                            scn.fcustom_index = len(scn.fcustom)-1
                            info = '"%s" added to list' % (item.name)
                            self.report({'INFO'}, info)
                        cfl = [f for f in bm.faces if f.select]
                        for i in cfl:
                            i.material_index = 1
            else:
                self.report(
                    {'INFO'}, "Enter Face Select option in Edit Mode")

        return {'FINISHED'}
    
    def get_random_color(self):
        r, g, b = [random.random() for i in range(3)]
        return r, g, b, 1


class VNT_OT_faceactions(Operator):
    bl_idname = "custom.face_action"
    bl_label = ""
    bl_description = "Remove Selected"
    bl_options = {'REGISTER'}

    action: EnumProperty(items=(('REMOVE', "Remove", ""),
                                ('ADD', "Add", "")))

    def get_random_color(self):
        r, g, b = [random.random() for i in range(3)]
        return r, g, b, 1

    def invoke(self, context, event):
        scn = context.scene
        print(type(context.scene))
        idx = scn.fcustom_index

        try:
            item = scn.fcustom[idx]
        except IndexError:
            pass

        if self.action == 'REMOVE':
            for i in range(len(scn.fcustom) - 1, -1, -1):  # Iterate in reverse
                if scn.fcustom[i].enabled:
                    scn.fcustom.remove(i)
            self.report({'INFO'}, "Selected Faces removed from list")

        if self.action == 'ADD':

            obj = bpy.context.object

            if obj:

                if obj.mode == 'EDIT':

                    face_check = True

                    bm = bmesh.from_edit_mesh(obj.data)
                    vertices = bm.verts
                    sel_v = [[v.index for v in f.verts]
                             for f in bm.faces if f.select]
                    for i in sel_v:
                        if len(i) > 4:
                            face_check = False
                            break

                        elif len(i) == 3:
                            # i.append(i[-1])
                            BN = []  # Block Names
                            for w in scn.simblk:
                                BN.append(w.name)

                            seen = set()
                            result = []
                            for item in BN:
                                if item not in seen:
                                    seen.add(item)
                                    result.append(item)

                            BV = []  # Block Vertices
                            for j in result:
                                m = []
                                for q in range(0, len(scn.simblk)):
                                    if scn.simblk[q].name == j:
                                        m.append(scn.simblk[q].index)

                                BV.append(m)

                            brep_verts = []
                            for rv in BV:
                                s = [item for item, count in collections.Counter(
                                    rv).items() if count > 1]
                                if len(s) > 0:
                                    brep_verts.append(s)

                            rep_v = []
                            for j in brep_verts:
                                for c in j:
                                    rep_v.append(c)

                            for v in range(0, len(i)):
                                if i[v] in list(set(rep_v)):
                                    i.insert(v, i[v])
                                    break
                        else:
                            pass

                    if face_check == False:
                        self.report(
                            {'INFO'}, "A selected Face has more than 4 vertices.")

                    else:
                        str_fac = []
                        sel_fac_list = []

                        for fac in sel_v:
                            str_fac = []
                            for i in fac:
                                str_fac.append(str(i))

                            M = "("
                            for j in str_fac:
                                if j == str_fac[0]:
                                    M = M + "" + j
                                else:
                                    M = M + " " + j

                            M = M + ")"
                            sel_fac_list.append(M)

                        if not scn.face_name.facename.strip():
                            self.report(
                                {'INFO'}, "Name the Face to add to list")

                        else:
                            clr = self.get_random_color()

                            for i in sel_fac_list:
                                item = scn.fcustom.add()
                                item.name = i
                                item.face_des = scn.face_name.facename
                                item.face_clr = clr
                                item.face_type = scn.bdclist
                                # bpy.ops.object.material_slot_add()

                                mat_clr = bpy.data.materials.new("clr")
                                mat_clr.diffuse_color = clr

                                scn.fcustom_index = len(scn.fcustom)-1
                                info = '"%s" added to list' % (item.name)
                                self.report({'INFO'}, info)

                            cfl = [f for f in bm.faces if f.select]

                            for i in cfl:
                                i.material_index = 1

                else:
                    self.report(
                        {'INFO'}, "Enter Face Select option in Edit Mode")

            else:
                self.report({'INFO'}, "Select Block/Geometry")

        return {"FINISHED"}


class VNT_OT_set_face_name(Operator):
    bl_label = "Set Face Name"
    bl_idname = "set.facename"
    bl_description = "Set Name of Face to be edited"

    def execute(self, context):
        scn = context.scene

        if len(scn.fcustom) == 0:
            self.report({'INFO'}, "No Faces available \ Face not Selected.")

        else:
            k = 0
            for i in range(0, len(scn.fcustom)):
                if scn.fcustom[i].enabled:
                    scn.fcustom[i].face_des = scn.face_name.facename
                    k += 1

            self.report({'INFO'}, "Name: " + scn.face_name.facename +
                        " assigned to " + str(k) + " selected faces.")

        return {"FINISHED"}


class VNT_OT_set_type_face(Operator):
    bl_label = "Set Type to Faces"
    bl_idname = "set.facetype"
    bl_description = "Choose Face type from drop-down menu.\nClick this button to change to selected Face Type"

    def execute(self, context):
        scn = context.scene

        if len(scn.fcustom) == 0:
            self.report({'INFO'}, "No Faces available \ Face not Selected.")

        else:
            k = 0
            for i in range(0, len(scn.fcustom)):
                if scn.fcustom[i].enabled:
                    scn.fcustom[i].face_type = scn.bdclist
                    k += 1

            self.report({'INFO'}, "Name: " + scn.bdclist +
                        " assigned to " + str(k) + " selected faces.")

        return {'FINISHED'}


class VNT_OT_selectfaces(Operator):
    bl_idname = "custom.select_faces"
    bl_label = "Select Item(s) in Viewport"
    bl_description = "Show Selected Face(s) in the Viewport"
    bl_options = {'REGISTER', 'UNDO'}

    select_all: BoolProperty(
        default=False,
        name="Select all Items of List",
        options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return bool(context.scene.fcustom)

    def execute(self, context):
        scn = context.scene
        idx = scn.fcustom_index
        print("____")
        if bpy.context.object.mode == "EDIT":
            pass
        else:
            bpy.ops.object.mode_set(mode='EDIT')

        # Select all faces in the List
        if self.select_all:
            obj = bpy.context.object
            bm = bmesh.from_edit_mesh(obj.data)
            sel_face_list = []

            sel_face_list = [face_strtolist(
                scn.fcustom[i].name) for i in range(0, len(scn.fcustom))]

            for f in bm.faces:
                face = []
                for v in f.verts:
                    face.append(v.index)

                for i in sel_face_list:
                    if i == face:
                        f.select = True
                        bmesh.update_edit_mesh(obj.data, destructive=True)

        else:
            obj = bpy.context.object
            bm = bmesh.from_edit_mesh(obj.data)
            sel_face_list = []

            sel_face_list = [face_strtolist(scn.fcustom[i].name) for i in range(
                0, len(scn.fcustom)) if scn.fcustom[i].enabled]

            for f in bm.faces:
                face = []
                for v in f.verts:
                    face.append(v.index)

                for i in sel_face_list:
                    if i == face:
                        f.select = True
                        bmesh.update_edit_mesh(obj.data, destructive=True)

        return{'FINISHED'}


class VNT_OT_clearfaces(Operator):
    bl_idname = "custom.clear_faces"
    bl_label = "Clear All Faces"
    bl_description = "Clear all Faces from the List"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.fcustom)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if bool(context.scene.fcustom):
            context.scene.fcustom.clear()
            self.report({'INFO'}, "All items removed")
        else:
            self.report({'INFO'}, "Nothing to remove")
        return{'FINISHED'}

def project_point_onto_plane(point, plane_point, plane_normal):
        """Project a point onto a plane defined by a point and a normal."""
        vec = point - plane_point
        distance = vec.dot(plane_normal)
        projection = point - distance * plane_normal
        return distance, projection


def point_in_polygon_2d(pt, poly):
    """
    Determine if a 2D point is inside a polygon using the ray-casting algorithm.

    :param pt: tuple (x, y) of the point
    :param poly: list of tuples [(x1, y1), (x2, y2), ...] defining the polygon vertices
    :return: True if inside or on edge, False otherwise
    """
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[(i + 1) % n]
        if (yi > y) != (yj > y):
            x_intersect = (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi
            if x < x_intersect:
                inside = not inside
    return inside

def faces_intersect(faces, tol=1e-6):
    """
    Check if one face is entirely contained within the other.

    :param faces: list of two bmesh Face elements
    :param tol: tolerance for projection errors
    :return: True if one face lies completely within the other, False otherwise
    """
    if len(faces) != 2:
        raise ValueError("Exactly two faces are required.")

    f1, f2 = faces

    def face_completely_inside(inner, outer):
        # Build 2D basis for the outer face
        u = (outer.verts[1].co - outer.verts[0].co).normalized()
        v = outer.normal.cross(u).normalized()

        poly2d = [
            (
                (vtx.co - outer.verts[0].co).dot(u),
                (vtx.co - outer.verts[0].co).dot(v)
            ) for vtx in outer.verts
        ]

        for vtx in inner.verts:
            dist, proj = project_point_onto_plane(vtx.co, outer.verts[0].co, outer.normal)
            if abs(dist) > tol:
                return False
            pt2d = (
                (proj - outer.verts[0].co).dot(u),
                (proj - outer.verts[0].co).dot(v)
            )
            if not point_in_polygon_2d(pt2d, poly2d):
                return False

        return True

    return face_completely_inside(f1, f2) or face_completely_inside(f2, f1)

# Operators for mergepatchpairs
class VNT_OT_merge_faces(Operator):
    bl_idname = "vnt.merge_faces"
    bl_label = "Merge Faces"
    bl_description = "Merge two selected overlapping faces"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        cs = context.scene
        obj = context.object

        if obj.mode != 'EDIT':
            self.report({'ERROR'}, "You must be in Edit Mode to merge faces.")
            return {'CANCELLED'}

        bm = bmesh.from_edit_mesh(obj.data)
        selected_faces = [f for f in bm.faces if f.select]

        if len(selected_faces) != 2:
            self.report({'ERROR'}, "Exactly two faces must be selected.")
            return {'CANCELLED'}
        
        # Convert selected faces to their vertex indices
        selected_face_indices = [[v.index for v in f.verts] for f in selected_faces]

        # Verify both faces exist in context.scene.fcustom
        fcustom_faces = [face_strtolist(f.name) for f in cs.fcustom]
        if not all(face in fcustom_faces for face in selected_face_indices):
            print(selected_face_indices)
            print(fcustom_faces)
            self.report({'ERROR'}, "Selected faces must exist in the face list.")
            return {'CANCELLED'}

        # Check if the two faces are overlapping
        face_areas = [f.calc_area() for f in selected_faces]
        if not faces_intersect(selected_faces):
            self.report({'ERROR'}, "Selected faces are not overlapping.")
            return {'CANCELLED'}

        fcustom_faces = [face_strtolist(f.name) for f in cs.fcustom]

        selected_face_des=[[],[]]

        # search for the master face in the fcustom list
        for i in range(len(fcustom_faces)):
            if fcustom_faces[i] == selected_face_indices[0]:
                selected_face_des[0] = cs.fcustom[i].face_des
                break
        # search for the slave face in the fcustom list
        for i in range(len(fcustom_faces)):
            if fcustom_faces[i] == selected_face_indices[1]:
                selected_face_des[1] = cs.fcustom[i].face_des
                break
        
        # determine the master and slave faces based on the area
        master_face, slave_face = (selected_face_des[0], selected_face_des[1]) if face_areas[0] > face_areas[1] else (selected_face_des[1], selected_face_des[0])

        # Add the mapping to fmcustom
        item = cs.fmcustom.add()
        item.master_face = master_face
        item.slave_face = slave_face

        self.report({'INFO'}, f"Merged {item.master_face} (master) with {item.slave_face} (slave).")
        return {'FINISHED'}

    def face_to_string(self, face):
        """Convert a face's vertex indices to a string representation."""
        return f"({', '.join(str(v.index) for v in face.verts)})"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

class VNT_OT_merge_faces_delete(Operator):
    bl_idname = "vnt.merge_faces_delete"
    bl_label = "Separate Faces"
    bl_description = "Separate selected Face pairs"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.fmcustom)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if bool(context.scene.fcustom):
            context.scene.fmcustom.clear()
            self.report({'INFO'}, "All items removed")
        else:
            self.report({'INFO'}, "Nothing to remove")
        return{'FINISHED'}



def list_current_faces(self, context):
    items = []
    for i, f in enumerate(context.scene.fcustom):
        items.append((str(f.face_des), f.face_des, f"{f.face_des}, {f.name}"))
    return items