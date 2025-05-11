import bpy
from bpy.types import Operator, PropertyGroup, UIList
from bpy.props import (
    StringProperty, EnumProperty,
    FloatProperty, FloatVectorProperty,
    PointerProperty
)
from bpy.app.handlers import persistent

class GeometryItem(PropertyGroup):
    name: StringProperty()
    geometry_type: EnumProperty(
        name="Type", items=[
            ("searchableBox", "Box", ""),
            ("searchableSphere", "Sphere", ""),
        ])
    box_min: FloatVectorProperty(size=3)
    box_max: FloatVectorProperty(size=3)
    sphere_center: FloatVectorProperty(size=3)
    sphere_radius: FloatProperty()

class GEOMETRY_UL_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.label(text=item.name, icon='MESH_CUBE' if item.geometry_type == "searchableBox" else 'SPHERE')
            row.label(text=item.geometry_type)

class VNT_OT_create_new_geometry(Operator):
    """Create new geometry"""
    bl_idname = "vnt.create_new_geometry"
    bl_label = "Create New Geometry"

    geometry_type: bpy.props.EnumProperty(
        name="Type",
        description="Select Geometry Type",
        items=[
            ("searchableBox", "Box", ""),
            ("searchableSphere", "Sphere", ""),
        ],
        default="searchableBox"
    )
    geometry_name: bpy.props.StringProperty( 
        name="Name",
        description="Enter the geometry name",
        default=""
    )
    min_x: bpy.props.FloatProperty(name="Min X", default=0.0)
    min_y: bpy.props.FloatProperty(name="Min Y", default=0.0)
    min_z: bpy.props.FloatProperty(name="Min Z", default=0.0)
    max_x: bpy.props.FloatProperty(name="Max X", default=1.0)
    max_y: bpy.props.FloatProperty(name="Max Y", default=1.0)
    max_z: bpy.props.FloatProperty(name="Max Z", default=1.0)
    centre_x: bpy.props.FloatProperty(name="Centre X", default=0.0)
    centre_y: bpy.props.FloatProperty(name="Centre Y", default=0.0)
    centre_z: bpy.props.FloatProperty(name="Centre Z", default=0.0)
    radius: bpy.props.FloatProperty(name="Radius", default=1.0)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        
        # Name field with better labeling
        box = layout.box()
        box.label(text="Geometry Settings:", icon='OUTLINER_OB_MESH')
        row = box.row()
        row.label(text="Name:")
        row.prop(self, "geometry_name", text="")
        
        # Type selection with more visual separation
        box.separator()
        row = box.row()
        row.label(text="Type:")
        row.prop(self, "geometry_type", text="")
        
        # Parameters box
        params_box = layout.box()
        
        if self.geometry_type == "searchableBox":
            params_box.label(text="Box Parameters:", icon='MESH_CUBE')
            
            # Min/Max coordinates with better layout
            col = params_box.column(align=True)
            
            row = col.row(align=True)
            row.label(text="X Range:")
            row.prop(self, "min_x", text="Min")
            row.prop(self, "max_x", text="Max")
            
            row = col.row(align=True)
            row.label(text="Y Range:")
            row.prop(self, "min_y", text="Min")
            row.prop(self, "max_y", text="Max")
            
            row = col.row(align=True)
            row.label(text="Z Range:")
            row.prop(self, "min_z", text="Min")
            row.prop(self, "max_z", text="Max")
            
        elif self.geometry_type == "searchableSphere":
            params_box.label(text="Sphere Parameters:", icon='MESH_UVSPHERE')
            
            # Center location
            col = params_box.column(align=True)
            col.label(text="Center Location:")
            row = col.row(align=True)
            row.prop(self, "centre_x", text="X")
            row.prop(self, "centre_y", text="Y")
            row.prop(self, "centre_z", text="Z")
            
            # Radius
            col.separator()
            col.prop(self, "radius", text="Radius")

    def execute(self, context):
        cs = context.scene
        if self.geometry_type == "searchableBox":
            width  = self.max_x - self.min_x
            height = self.max_y - self.min_y
            depth  = self.max_z - self.min_z
            center = ((self.min_x + self.max_x) / 2,
                      (self.min_y + self.max_y) / 2,
                      (self.min_z + self.max_z) / 2)
            bpy.ops.mesh.primitive_cube_add(location=center)
            cube = context.active_object
            cube.scale = (width / 2, height / 2, depth / 2)
        elif self.geometry_type == "searchableSphere":
            loc = (self.centre_x, self.centre_y, self.centre_z)
            bpy.ops.mesh.primitive_uv_sphere_add(radius=self.radius, location=loc)
        
        obj = context.active_object
        if self.geometry_name:
            obj.name = self.geometry_name
        else:
            obj.name = f"{self.geometry_type}_{len(cs.geometry_items)}"
        
        # Set display type to wire + solid for better visibility
        mat_name = f"{obj.name}_material"
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(mat_name)
        
        mat.use_nodes = True
        mat.blend_method = 'BLEND'
        mat.shadow_method = 'NONE'  # Don't cast shadows
        mat.use_backface_culling = False
        
        # Set viewport display properties
        if hasattr(mat, "diffuse_color"):  # For viewport display
            if self.geometry_type == "searchableBox":
                mat.diffuse_color = (0.2, 0.6, 1.0, 0.4)  # Blue, translucent
            else:
                mat.diffuse_color = (1.0, 0.6, 0.2, 0.4)  # Orange, translucent
        
        # Clear existing material slots
        while len(obj.material_slots) > 0:
            bpy.ops.object.material_slot_remove()
            
        # Add new material slot and assign material
        obj.data.materials.append(mat)
        
        # Set material nodes for translucency
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        # Clear existing nodes
        for node in nodes:
            nodes.remove(node)
            
        # Create new nodes
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        output.location = (300, 0)
        bsdf.location = (0, 0)
        
        # Set node properties
        if self.geometry_type == "searchableBox":
            bsdf.inputs['Base Color'].default_value = (0.2, 0.6, 1.0, 1.0)  # Blue
        else:
            bsdf.inputs['Base Color'].default_value = (1.0, 0.6, 0.2, 1.0)  # Orange
            
        bsdf.inputs['Alpha'].default_value = 0.4  # 40% opacity
        bsdf.inputs['Specular'].default_value = 0.1  # Low specular
        bsdf.inputs['Roughness'].default_value = 0.9  # High roughness
        
        # Connect nodes
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        
        # Organize and hide the geometry
        col = bpy.data.collections.get("User Defined Geometry")
        if not col:
            col = bpy.data.collections.new("User Defined Geometry")
            context.scene.collection.children.link(col)
        
        # Move object to collection
        if obj.name not in col.objects:
            col.objects.link(obj)
        if obj.name in context.scene.collection.objects:
            context.scene.collection.objects.unlink(obj)
            
        # Add to items list
        new_item = cs.geometry_items.add()
        new_item.name = obj.name
        new_item.geometry_type = self.geometry_type
        if self.geometry_type == "searchableBox":
            new_item.box_min = (self.min_x, self.min_y, self.min_z)
            new_item.box_max = (self.max_x, self.max_y, self.max_z)
        else:
            new_item.sphere_center = (self.centre_x, self.centre_y, self.centre_z)
            new_item.sphere_radius = self.radius
        
        # Set this new item as the selected one
        cs.geometry_items_index = len(cs.geometry_items) - 1
        
        # Force update visibility
        obj.color = princ_color = (
            *(bsdf.inputs['Base Color'].default_value[0:3]), 
            0.4
        )
        obj.show_in_front = True      # always visible
        obj.show_wire = False         # hide wire, show solid
        obj.active_material = mat     # ensure material is bound

        for other_obj in col.objects:
            other_obj.hide_viewport = (other_obj != obj)
        
        self.report({'INFO'}, f"Created geometry of type {self.geometry_type}")
        return {'FINISHED'}

class VNT_OT_delete_geometry(Operator):
    """Delete geometry"""
    bl_idname = "vnt.delete_geometry"
    bl_label = "Delete Geometry"

    def execute(self, context):
        cs = context.scene
        index = cs.geometry_items_index
        if index < 0 or index >= len(cs.geometry_items):
            self.report({'WARNING'}, "Please select geometry to delete")
            return {'CANCELLED'}
        geom_name = cs.geometry_items[index].name
        obj = bpy.data.objects.get(geom_name)
        if not obj:
            cs.geometry_items.remove(index)
            cs.geometry_items_index = min(index, len(cs.geometry_items) - 1)
            self.report({'WARNING'}, f"Object {geom_name} not found, removed from list")
            return {'FINISHED'}
        for col in obj.users_collection:
            col.objects.unlink(obj)
        bpy.data.objects.remove(obj)
        cs.geometry_items.remove(index)
        cs.geometry_items_index = min(index, len(cs.geometry_items) - 1)
        
        # Update visibility after deletion
        update_geometry_visibility(context.scene, None)
        
        self.report({'INFO'}, f"Deleted geometry: {geom_name}")
        return {'FINISHED'}

def update_geometry_visibility(scene, context):
    """Update geometry visibility when selection changes in UI"""
    collection = bpy.data.collections.get("User Defined Geometry")
    if not collection:
        return
    
    # Hide all geometry objects
    for obj in collection.objects:
        obj.hide_viewport = True
    
    # Show only the selected geometry
    if hasattr(scene, "geometry_items") and hasattr(scene, "geometry_items_index"):
        index = scene.geometry_items_index
        if 0 <= index < len(scene.geometry_items):
            obj_name = scene.geometry_items[index].name
            obj = bpy.data.objects.get(obj_name)
            if obj:
                obj.hide_viewport = False

# Callback for index property update
def geometry_index_update(self, context):
    """Callback when the geometry_items_index changes"""
    update_geometry_visibility(self, context)

@persistent
def clean_geometry_items(dummy):
    scene = bpy.context.scene
    items = scene.geometry_items
    for i in range(len(items) - 1, -1, -1):
        if not bpy.data.objects.get(items[i].name):
            items.remove(i)

# This function should be called from the scene post handler
@persistent
def initialize_geometry_visibility(dummy):
    """Initialize visibility of geometry objects after file load"""
    if not hasattr(bpy.context.scene, "geometry_items"):
        return
    update_geometry_visibility(bpy.context.scene, bpy.context)

def register():
    bpy.utils.register_class(GeometryItem)
    bpy.utils.register_class(GEOMETRY_UL_items)
    if clean_geometry_items not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(clean_geometry_items)
    
    # Add handler for file load to initialize visibility
    if initialize_geometry_visibility not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(initialize_geometry_visibility)
    
def unregister():
    bpy.utils.unregister_class(GEOMETRY_UL_items)
    bpy.utils.unregister_class(GeometryItem)
    if clean_geometry_items in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(clean_geometry_items)
    
    if initialize_geometry_visibility in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(initialize_geometry_visibility)
