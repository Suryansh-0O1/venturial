import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import FloatVectorProperty, IntProperty, StringProperty, CollectionProperty
import bmesh, time
import numpy as np
import bgl
import gpu
from gpu_extras.batch import batch_for_shader
from bpy_extras import object_utils
from bpy.props import CollectionProperty, IntProperty, FloatVectorProperty

from venturial.models.edge_gen_algorithms import *

def update_selected_edge(self, context):
    """
    Automatically select the edge corresponding to the current ecustom_index
    """
    try:
        # Call the select edge operator
        bpy.ops.vnt.select_edge()
    except Exception as e:
        print(f"Error updating selected edge: {e}")

a = [None, ]
verts = [[]]

def sync(self):
    try:
        cs = bpy.context.scene
        # Append empty list to match length of cs.ecustom
        while len(verts) < len(cs.ecustom):
            verts.append([])

        # Append None to match length of cs.ecustom
        while len(a) < len(cs.ecustom):
            a.append(None)

        for i in range(len(bpy.context.scene.ecustom)):
            if len(cs.ecustom[cs.ecustom_index].vert_collection)==0:
                continue
            for j in range(100):
                bpy.context.scene.ecustom[i].vertex_col[j].vert_loc = verts[i][j]
    except Exception as e:
        print(f"exception in sync ------> {e}")
        return

class VNT_ecustom_edge_obj(PropertyGroup):
    source_object: bpy.props.StringProperty()
    edge_index: bpy.props.IntProperty(default=-1)

class OBJECT_OT_add_single_vertex(Operator):
    bl_idname = "mesh.add_single_vertex"
    bl_label = "Add Single Vertex"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mesh = bpy.data.meshes.new("Vert")
        mesh.vertices.add(1)

        object_utils.object_data_add(context, mesh, operator=None)
        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}

class VNT_OT_new_edge(Operator):
    '''
    Generate custom edge type for the selected edge
    '''

    bl_idname = "vnt.new_edge"
    bl_label = "Generate Edge"

    def execute(self, context):
        a.append(None)
        verts.append([])

        cs = context.scene
        edg = cs.ecustom.add()
        index = len(cs.ecustom) - 1
        a[index] = None
        verts[index] = []

        edg.name = str(time.time())
        edg.edge_type = cs.curve_type

        for i in range(100):
            edg.vertex_col.add()

        #test to store object edge 
        bpy.ops.object.mode_set( mode = 'EDIT' )
        selectedEdges = []

        selectedEdges = [i for i in bmesh.from_edit_mesh(context.active_object.data).edges if i.select]

        if len(selectedEdges) > 1:
            self.report({'ERROR', 'Please select only one edge'})
            return
        if len(selectedEdges) < 1:
            self.report({'ERROR', 'Please select an edge'})
            return
        
        
        link = cs.ecustom_edge_obj.add()
        link.source_object = context.active_object.name
        link.edge_index = selectedEdges[0].index

        return{'FINISHED'}

class VNT_OT_select_edge(Operator):
    bl_idname = "vnt.select_edge"
    bl_label = "Select Edge"

    def execute(self, context):
        sc = context.scene
        index = sc.ecustom_index

        if index < 0 or index >= len(sc.ecustom_edge_obj):
            self.report({'ERROR'}, "Invalid edge index")
            return {'CANCELLED'}

        custom_edge = sc.ecustom_edge_obj[index]
        obj = bpy.data.objects.get(custom_edge.source_object)

        if not obj:
            self.report({'ERROR'}, "Source object not found")
            return {'CANCELLED'}

        context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')

        # Get BMesh data
        bm = bmesh.from_edit_mesh(obj.data)
        bm.edges.ensure_lookup_table()

        # Deselect all edges
        for edge in bm.edges:
            edge.select = False

        # Select the target edge
        if 0 <= custom_edge.edge_index < len(bm.edges):
            bm.edges[custom_edge.edge_index].select = True
        else:
            self.report({'ERROR'}, "Edge index out of range")
            return {'CANCELLED'}

        bmesh.update_edit_mesh(obj.data)
        # context.area.tag_redraw()
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'window': context.window, 'screen': context.screen, 'area': area, 'region': region}
                        bpy.ops.view3d.view_selected(override)
                        break
        # bpy.ops.view3d.view_selected()

        return {'FINISHED'}

class VNT_OT_new_vert(Operator):
    '''
    Generate new vertex for the selected edge
    '''

    bl_idname = "vnt.new_vert"
    bl_label = "Generate new Vertex"

    @classmethod
    def poll(cls, context):
        cs = context.scene
        if len(cs.ecustom) == 0:
            return True
        else:
            curr_edge = cs.ecustom[cs.ecustom_index]
            return curr_edge.edge_type != 'ARC' or len(curr_edge.vert_collection) == 0

    def execute(self, context):
        cs = context.scene
        try:
            self.index = cs.ecustom_index
            self.curr_edge = cs.ecustom[int(self.index)]
        
        except Exception as e:
            print(e)
            self.report({'ERROR'}, 'No spline selected to add vertex')
            return {'CANCELLED'}
        
        if(len(self.curr_edge.vert_collection) == 0):
            self.first(context)
        else:
            self.n_first(context)
        
        draw_p(self, context)
        sync(self)
        return {'FINISHED'}
    
    def first(self, context):
        cs = context.scene
        print("Executing first")
        try:
            bpy.ops.object.mode_set( mode = 'EDIT' )
            selectedEdges = []

            selectedEdges = [i for i in bmesh.from_edit_mesh(context.active_object.data).edges if i.select]

            if len(selectedEdges) > 1:
                self.report({'ERROR', 'Please select only one edge'})
                return
            if len(selectedEdges) < 1:
                self.report({'ERROR', 'Please select an edge'})
                return
            
            context.space_data.show_gizmo_object_translate = True 
            g = context.active_object.matrix_world

            x = g @ selectedEdges[0].verts[0].co
            y = g @ selectedEdges[0].verts[1].co
        except Exception:
            return
        
        for i in range(3):
            self.curr_edge.vc.add()
        
        self.curr_edge.vc[0].vert_loc=x
        self.curr_edge.vc[2].vert_loc=y
        coord = [None, None, None]

        for i in range(3):
            coord[i] = (x[i] + y[i])/1.5
        
        self.curr_edge.vert_collection.add()
        self.curr_edge.vert_collection[0].vert_loc=coord
        self.curr_edge.vc[1].vert_loc=coord
        print(coord)

        bpy.ops.object.mode_set(mode='OBJECT')
        # bpy.ops.mesh.primitive_vert_add() # to be changed
        bpy.ops.mesh.add_single_vertex()
        bpy.ops.object.mode_set(mode='OBJECT')

        vertex = context.selected_objects[0]
        vertex.location = coord
        vertex.name = f"{self.curr_edge.name}01"
        vertex=0
    
    def n_first(self, context):
        print("Executing n_first")
        context.space_data.show_gizmo_object_translate = True
        len1 = len(self.curr_edge.vertex_col)

        self.curr_edge.vert_collection.add()
        length = len(self.curr_edge.vert_collection)

        for i in range(length):
            self.curr_edge.vert_collection[i].vert_loc = (self.curr_edge.vertex_col[(i+1)*len1//(length+1)].vert_loc) 
        
        bpy.ops.object.mode_set( mode='OBJECT' )
        # bpy.ops.mesh.primitive_vert_add() # to be changed
        bpy.ops.mesh.add_single_vertex()
        bpy.ops.object.mode_set( mode='OBJECT' )

        vertex = bpy.context.selected_objects[0]
        vertex.name = f"{self.curr_edge.name}0{length}"

        for i in range(length):
            _a_ = bpy.data.objects[f"{self.curr_edge.name}0{i+1}"]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
            _a_.location = self.curr_edge.vert_collection[i].vert_loc

class VNT_OT_remove_edge(Operator):
    '''
    Remove the selected edge
    '''

    bl_idname = "vnt.remove_edge"
    bl_label = "Remove Edge"

    def execute(self, context):
        cs = context.scene
        try:
            index = cs.ecustom_index
            if index < 0 or index >= len(cs.ecustom):
                self.report({'ERROR'}, 'No spline selected to remove')
                return {'CANCELLED'}

            cur_spline = cs.ecustom[index]

        except Exception as e:
            self.report({'ERROR'}, 'No spline selected to remove')
            return {'CANCELLED'}
        
        for i in range(len(cur_spline.vert_collection)-1, -1, -1):
            bpy.data.objects.remove(bpy.data.objects[f"{cur_spline.name}0{i+1}"], do_unlink=True)
            cur_spline.vert_collection.remove(i)
        
        cs.ecustom.remove(int(index))
        cs.ecustom_edge_obj.remove(int(index))
        try:
            if a[index] is not None:
                bpy.types.SpaceView3D.draw_handler_remove(a[index], 'WINDOW')
        except Exception as e:
            pass
            
        a[index] = None
        verts[index] = []
        verts.pop(index)
        a.pop(index)
        cs.ecustom_index = max(0, index - 1)
        
        draw_p(self, context)
        return {'FINISHED'}

class VNT_OT_remove_vert(Operator):
    '''
    Remove the selected Vertex
    '''

    bl_idname = "vnt.remove_vert"
    bl_label = "Remove Vertex"

    def execute(self, context):
        cs = context.scene
        try: 
            index = cs.ecustom_index
            if index < 0 or index >= len(cs.ecustom):
                self.report({'ERROR'}, 'No spline selected to remove vertex from')
                return {'CANCELLED'}

            r_index = len(cs.ecustom[index].vert_collection) - 1
            if r_index < 0:
                self.report({'ERROR'}, 'No vertex to remove')
                return {'CANCELLED'}

            cs.ecustom[int(index)].vert_collection.remove(int(r_index))
            self.index = cs.ecustom_index
            self.curr_edge = cs.ecustom[int(self.index)]
        except Exception as e:
            self.report({'ERROR'}, 'No spline selected to remove vertex from')
            return {'CANCELLED'}
        
        bpy.data.objects.remove(bpy.data.objects[f"{self.curr_edge.name}0{r_index+1}"], do_unlink=True)
        len1 = len(self.curr_edge.vertex_col)
        length = len(self.curr_edge.vert_collection)
        for i in range(length):
            self.curr_edge.vert_collection[i].vert_loc = self.curr_edge.vertex_col[(i+1)*len1//(length+1)].vert_loc
        for i in range(length):
            _a_ = bpy.data.objects[f"{self.curr_edge.name}0{i+1}"]
            _a_.location = self.curr_edge.vert_collection[i].vert_loc
        
        # Warns the user that All verts are removed 
        if len(cs.ecustom[int(index)].vert_collection) == 0:
            self.report({'WARNING'}, 'All vertices removed. Edge still exists. Use "Remove Edge" to delete the edge.')

        # cs.ecustom_index = index

        # Remove the draw handler if no vertices are left
        if len(cs.ecustom[int(index)].vert_collection) == 0:
            try:
                if a[index] is not None:
                    bpy.types.SpaceView3D.draw_handler_remove(a[index], 'WINDOW')
                    a[index] = None
            except Exception as e:
                pass

        verts[index] = []
        draw_p(self, context)
        return {'FINISHED'}

# def tag_redraw():
#     for area in bpy.context.screen.areas:
#         if area.type == 'VIEW_3D':
#             area.tag_redraw()

def draw_p(self, context):
    '''
    Draws spline using cubic spline interpolation
    Algorithm to be changed 
    '''
    cs = context.scene

    for i in range(len(cs.ecustom)):
        if a[i] is not None:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(a[i], 'WINDOW')
            except Exception as e:
                pass
        
        if len(cs.ecustom[i].vert_collection) == 0:
            continue

        verts[i] = []
        for j in range(len(cs.ecustom[i].vert_collection)):
            ax = bpy.data.objects[f"{cs.ecustom[i].name}0{j+1}"]
            verts[i].append(ax.location)
        lin1 = []

        _a = cs.ecustom[i].vc[0].vert_loc[:]
        verts[i].insert(0, _a)
        _a = cs.ecustom[i].vc[2].vert_loc[:]
        verts[i].append(_a)

        _temp = len(verts[i])
        for k in range(_temp):
            lin1.append(int(k*100/(_temp -1 )))
        
        curve_p = []

        # This Piece of code is to be implemented when there is point generating algorithms for each edge type
        if cs.ecustom[i].edge_type == 'SPL':
            print("Using Spline Gen")
            curve_p = generate_catmull_rom_curve(100, verts[i])
        elif cs.ecustom[i].edge_type == 'ARC':
            print("Using ARC Gen")
            curve_p = generate_arc_curve(100, verts[i])
        elif cs.ecustom[i].edge_type == 'PLY':
            curve_p = verts[i]
        elif cs.ecustom[i].edge_type == 'BSPL':
            curve_p = generate_bspline_curve(100, verts[i])
        
        verts[i] = curve_p
        a[i] = bpy.types.SpaceView3D.draw_handler_add(draw_edge_viewport, (i,), 'WINDOW', 'POST_VIEW')

def draw_edge_viewport(index):
    verts_t=verts[index]
    if not verts_t:
        return
    
    try:
        curr_spline = bpy.context.scene.ecustom[index]
    except Exception as e:
        return
    
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    # bgl.glLineWidth(curr_spline.size)
    col = (curr_spline.color[0], curr_spline.color[1], curr_spline.color[2], curr_spline.color[3])

    batch = batch_for_shader(shader, 'LINE_STRIP', {'pos': verts_t})

    gpu.state.depth_test_set("LESS_EQUAL")

    gpu.state.blend_set("ALPHA")
    gpu.state.face_culling_set("BACK")

    shader.bind()
    
    shader.uniform_float('color', col)

    batch.draw(shader)

    gpu.state.blend_set("NONE")
    gpu.state.face_culling_set("NONE")
    gpu.state.depth_test_set("NONE")