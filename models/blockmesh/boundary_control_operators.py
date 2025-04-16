from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty
import bpy
import bmesh
import random

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
                            item.object_name = obj.name
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
    bl_description = "Add/Remove Faces or Move Faces Up/Down"
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
            self.report({'INFO'}, "Feature in development. Use delete all for now.")

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

# Operators for mergepatchpairs
class VNT_OT_merge_faces(Operator):
    bl_idname = "vnt.merge_faces"
    bl_label = "Merge Faces"
    bl_description = "Merge selected Faces"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        cs = context.scene

        r1 = layout.row(align=True)
        r1.label(text="Master Face:")
        r1.prop(cs, "faceList_master")

        r2 = layout.row(align=True)
        r2.label(text="Slave:")
        r2.prop(cs, "faceList_slave")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def execute(self, context):  
        cs = context.scene
        
        if cs.faceList_master == cs.faceList_slave:
            self.report({'ERROR'}, "Master and Slave faces cannot be same")
            return {'CANCELLED'}
        
        master_item = next((f for f in cs.fcustom if f.face_des == cs.faceList_master), None)
        slave_item = next((f for f in cs.fcustom if f.face_des == cs.faceList_slave), None)

        if not master_item or not slave_item:
            self.report({'ERROR'}, "Boundary not found.")
            return {'CANCELLED'}

        # Parse the vertex index strings
        def parse_indices(vstring):
            return [int(v) for v in vstring.strip("()").split()]

        master_verts = parse_indices(master_item.name)
        slave_verts = parse_indices(slave_item.name)

        master_obj = bpy.data.objects.get(master_item.object_name)
        slave_obj = bpy.data.objects.get(slave_item.object_name)

        if not master_obj or not slave_obj:
            self.report({'ERROR'}, "One or both objects not found.")
            return {'CANCELLED'}

        # Duplicate master and slave face regions into separate objects
        def extract_face_region(obj, verts, name):
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj

            bpy.ops.object.duplicate()
            dup = context.active_object
            dup.name = name

            bpy.ops.object.mode_set(mode='EDIT')
            bm = bmesh.from_edit_mesh(dup.data)
            for f in bm.faces:
                if not all(v.index in verts for v in f.verts):
                    f.select = False
                else:
                    f.select = True
            bmesh.update_edit_mesh(dup.data)
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.delete(type='FACE')
            bpy.ops.object.mode_set(mode='OBJECT')
            return dup

        master_region = extract_face_region(master_obj, master_verts, "MasterRegion")
        slave_region = extract_face_region(slave_obj, slave_verts, "SlaveRegion")

        # Perform boolean on full object
        context.view_layer.objects.active = master_obj
        master_obj.select_set(True)
        slave_region.select_set(True)

        bool_mod = master_obj.modifiers.new(name="MergeFaces", type='BOOLEAN')
        bool_mod.operation = 'UNION'
        bool_mod.object = slave_region
        bool_mod.solver = 'EXACT'

        bpy.ops.object.modifier_apply(modifier=bool_mod.name)

        # Cleanup
        bpy.data.objects.remove(slave_region, do_unlink=True)
        bpy.data.objects.remove(master_region, do_unlink=True)

        # Save mapping
        item = cs.fmcustom.add()
        item.master_face = cs.faceList_master
        item.slave_face = cs.faceList_slave

        self.report({'INFO'}, f"Merged {cs.faceList_master} with {cs.faceList_slave} using Boolean")
        return {'FINISHED'}

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