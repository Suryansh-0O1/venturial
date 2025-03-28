import bpy
from bpy.types import Operator
from bpy.app.handlers import persistent

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
        layout.row().label(text="Name")
        layout.row().prop(self, "geometry_name", text="")
        row = layout.row()
        row.label(text="Type")
        row.prop(self, "geometry_type", text="")
        if self.geometry_type == "searchableBox":
            layout.label(text="Box Settings:")
            row = layout.row()
            row.prop(self, "min_x", text="Min X")
            row.prop(self, "max_x", text="Max X")
            row = layout.row()
            row.prop(self, "min_y", text="Min Y")
            row.prop(self, "max_y", text="Max Y")
            row = layout.row()
            row.prop(self, "min_z", text="Min Z")
            row.prop(self, "max_z", text="Max Z")
        elif self.geometry_type == "searchableSphere":
            layout.label(text="Sphere Settings:")
            row = layout.row()
            row.prop(self, "centre_x", text="Centre X")
            row.prop(self, "centre_y", text="Centre Y")
            row.prop(self, "centre_z", text="Centre Z")
            layout.prop(self, "radius", text="Radius")

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
        col = bpy.data.collections.get("User Defined Geometry")
        if not col:
            col = bpy.data.collections.new("User Defined Geometry")
            context.scene.collection.children.link(col)
        if obj.name not in col.objects:
            col.objects.link(obj)
        if obj.name in context.scene.collection.objects:
            context.scene.collection.objects.unlink(obj)
        new_item = cs.geometry_items.add()
        new_item.name = obj.name
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
        self.report({'INFO'}, f"Deleted geometry: {geom_name}")
        return {'FINISHED'}

@persistent
def clean_geometry_items(dummy):
    scene = bpy.context.scene
    items = scene.geometry_items
    for i in range(len(items) - 1, -1, -1):
        if not bpy.data.objects.get(items[i].name):
            items.remove(i)

def register():
    if clean_geometry_items not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(clean_geometry_items)

def unregister():
    if clean_geometry_items in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(clean_geometry_items)
