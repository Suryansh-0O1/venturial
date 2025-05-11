import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import StringProperty, FloatProperty, IntProperty, BoolProperty, EnumProperty, CollectionProperty, PointerProperty, FloatVectorProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
import os

# Property Groups for the different castellated mesh components
class CastellatedFeature(PropertyGroup):
    """Represents a feature edge for castellated mesh refinement"""
    file: StringProperty(
        name="File",
        description="Path to the eMesh file",
        default=""
    )
    
    use_levels: BoolProperty(
        name="Use Levels",
        description="Use distance-based levels instead of a single level",
        default=False
    )
    
    level: IntProperty(
        name="Level",
        description="Refinement level for this feature",
        default=2,
        min=0
    )
    
    distance: FloatProperty(
        name="Distance",
        description="Distance value for level pair",
        default=0.0,
        min=0.0
    )
    
    level_at_distance: IntProperty(
        name="Level at Distance",
        description="Refinement level at the specified distance",
        default=2,
        min=0
    )

class RefinementRegion(PropertyGroup):
    """Represents a refinement region for castellated mesh"""
    name: StringProperty(
        name="Name",
        description="Name of the refinement region",
        default="region"
    )
    
    source_type: EnumProperty(
        name="Source Type",
        description="Type of geometry source",
        items=[
            ('geometry', "Geometry Object", "Use a geometry object from the scene"),
            ('stl', "STL File", "Use an STL file")
        ],
        default='geometry'
    )
    
    geometry_object: StringProperty(
        name="Geometry Object",
        description="Name of the geometry object to use for refinement",
        default=""
    )
    
    mode: EnumProperty(
        name="Mode",
        description="Refinement mode",
        items=[
            ('distance', "Distance", "Distance-based refinement"),
            ('inside', "Inside", "Refine cells inside the surface"),
            ('outside', "Outside", "Refine cells outside the surface")
        ],
        default='inside'
    )
    
    level: IntProperty(
        name="Level",
        description="Refinement level for inside/outside mode",
        default=1,
        min=0
    )
    
    distance: FloatProperty(
        name="Distance",
        description="Distance value for distance mode",
        default=1.0,
        min=0.0
    )
    
    level_at_distance: IntProperty(
        name="Level at Distance",
        description="Refinement level at the specified distance",
        default=4,
        min=0
    )
    
    use_multi_levels: BoolProperty(
        name="Use Multiple Levels",
        description="Use multiple distance-level pairs",
        default=False
    )
    
    distance2: FloatProperty(
        name="Distance 2",
        description="Second distance value for multi-level distance refinement",
        default=2.0,
        min=0.0
    )
    
    level_at_distance2: IntProperty(
        name="Level at Distance 2",
        description="Refinement level at the second distance",
        default=3,
        min=0
    )

class PatchInfo(PropertyGroup):
    """Represents patch information for a refinement surface"""
    patch_type: EnumProperty(
        name="Type",
        description="Type of patch",
        items=[
            ('patch', "Patch", "Regular patch"),
            ('wall', "Wall", "Wall patch"),
            ('symmetry', "Symmetry", "Symmetry patch"),
            ('empty', "Empty", "Empty patch"),
            ('wedge', "Wedge", "Wedge patch")
        ],
        default='patch'
    )
    
    in_group: StringProperty(
        name="In Group",
        description="Group this patch belongs to",
        default="meshedPatches"
    )

class RefinementSurfaceRegion(PropertyGroup):
    """Represents a region in a refinement surface"""
    name: StringProperty(
        name="Name",
        description="Name of the region",
        default="region"
    )
    
    min_level: IntProperty(
        name="Min Level",
        description="Minimum refinement level",
        default=2,
        min=0
    )
    
    max_level: IntProperty(
        name="Max Level",
        description="Maximum refinement level",
        default=2,
        min=0
    )
    
    use_patch_info: BoolProperty(
        name="Use Patch Info",
        description="Specify patch information for this region",
        default=False
    )
    
    patch_info: PointerProperty(
        type=PatchInfo
    )

class RefinementSurface(PropertyGroup):
    """Represents a refinement surface for castellated mesh"""
    name: StringProperty(
        name="Name",
        description="Name of the refinement surface",
        default="surface.stl"
    )
    
    source_type: EnumProperty(
        name="Source Type",
        description="Type of geometry source",
        items=[
            ('geometry', "Geometry Object", "Use a geometry object from the scene"),
            ('stl', "STL File", "Use an STL file")
        ],
        default='geometry'
    )
    
    geometry_object: StringProperty(
        name="Geometry Object",
        description="Name of the geometry object to use for refinement",
        default=""
    )
    
    min_level: IntProperty(
        name="Min Level",
        description="Minimum refinement level",
        default=2,
        min=0
    )
    
    max_level: IntProperty(
        name="Max Level",
        description="Maximum refinement level",
        default=2,
        min=0
    )
    
    regions: CollectionProperty(
        type=RefinementSurfaceRegion,
        name="Regions"
    )
    
    regions_index: IntProperty(default=0)
    
    use_patch_info: BoolProperty(
        name="Use Patch Info",
        description="Specify patch information",
        default=False
    )
    
    patch_info: PointerProperty(
        type=PatchInfo
    )
    
    use_zones: BoolProperty(
        name="Use Zones",
        description="Specify face and cell zones",
        default=False
    )
    
    face_zone: StringProperty(
        name="Face Zone",
        description="Name of the face zone",
        default=""
    )
    
    cell_zone: StringProperty(
        name="Cell Zone",
        description="Name of the cell zone",
        default=""
    )
    
    cell_zone_inside: EnumProperty(
        name="Cell Zone Inside",
        description="Cell zone inside option",
        items=[
            ('inside', "Inside", "Inside the surface"),
            ('outside', "Outside", "Outside the surface")
        ],
        default='inside'
    )
    
    gap_level_increment: IntProperty(
        name="Gap Level Increment",
        description="Increment on top of max level in small gaps",
        default=2,
        min=0
    )
    
    use_gap_level: BoolProperty(
        name="Use Gap Level",
        description="Enable gap level increment",
        default=False
    )
    
    perpendicular_angle: FloatProperty(
        name="Perpendicular Angle",
        description="Angle to detect small-large cell situation",
        default=10.0,
        min=-1.0,
        max=90.0
    )
    
    use_perpendicular_angle: BoolProperty(
        name="Use Perpendicular Angle",
        description="Enable perpendicular angle",
        default=False
    )

# Enhanced operators with file browsing capabilities
class VNT_OT_add_feature(Operator, ImportHelper):
    """Add a new feature edge for refinement"""
    bl_idname = "vnt.add_feature"
    bl_label = "Add Feature"
    
    filename_ext = ".eMesh"
    filter_glob: StringProperty(default="*.eMesh", options={'HIDDEN'})
    
    def execute(self, context):
        item = context.scene.cast_features.add()
        if self.filepath:
            item.file = self.filepath
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class VNT_OT_browse_feature_file(Operator, ImportHelper):
    """Browse for feature edge mesh file"""
    bl_idname = "vnt.browse_feature_file"
    bl_label = "Browse Feature File"
    
    filename_ext = ".eMesh"
    filter_glob: StringProperty(default="*.eMesh", options={'HIDDEN'})
    
    feature_index: IntProperty(options={'HIDDEN'})
    
    def execute(self, context):
        if self.filepath and self.feature_index >= 0 and self.feature_index < len(context.scene.cast_features):
            context.scene.cast_features[self.feature_index].file = self.filepath
        return {'FINISHED'}

class VNT_OT_remove_feature(Operator):
    """Remove the selected feature edge"""
    bl_idname = "vnt.remove_feature"
    bl_label = "Remove Feature"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_features) > 0 and cs.cast_features_index >= 0:
            cs.cast_features.remove(cs.cast_features_index)
            if cs.cast_features_index > 0:
                cs.cast_features_index -= 1
        return {'FINISHED'}

class VNT_OT_add_refinement_surface(Operator):
    """Add a new refinement surface"""
    bl_idname = "vnt.add_refinement_surface"
    bl_label = "Add Refinement Surface"
    
    def execute(self, context):
        item = context.scene.cast_refinement_surfaces.add()
        
        if len(context.scene.geometry_items) > 0:
            item.geometry_object = context.scene.geometry_items[0].name
            
        return {'FINISHED'}

class VNT_OT_browse_surface_file(Operator, ImportHelper):
    """Browse for refinement surface file"""
    bl_idname = "vnt.browse_surface_file"
    bl_label = "Browse Surface File"
    
    filename_ext = ".stl"
    filter_glob: StringProperty(default="*.stl", options={'HIDDEN'})
    
    surface_index: IntProperty(options={'HIDDEN'})
    
    def execute(self, context):
        if self.filepath and self.surface_index >= 0 and self.surface_index < len(context.scene.cast_refinement_surfaces):
            surface = context.scene.cast_refinement_surfaces[self.surface_index]
            surface.name = os.path.basename(self.filepath)
            surface.source_type = 'stl'
        return {'FINISHED'}

class VNT_OT_remove_refinement_surface(Operator):
    """Remove the selected refinement surface"""
    bl_idname = "vnt.remove_refinement_surface"
    bl_label = "Remove Refinement Surface"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_refinement_surfaces) > 0 and cs.cast_refinement_surfaces_index >= 0:
            cs.cast_refinement_surfaces.remove(cs.cast_refinement_surfaces_index)
            if cs.cast_refinement_surfaces_index > 0:
                cs.cast_refinement_surfaces_index -= 1
        return {'FINISHED'}

class VNT_OT_add_surface_region(Operator):
    """Add a new region to the selected refinement surface"""
    bl_idname = "vnt.add_surface_region"
    bl_label = "Add Surface Region"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_refinement_surfaces) > 0 and cs.cast_refinement_surfaces_index >= 0:
            surface = cs.cast_refinement_surfaces[cs.cast_refinement_surfaces_index]
            surface.regions.add()
        return {'FINISHED'}

class VNT_OT_remove_surface_region(Operator):
    """Remove the selected region from the refinement surface"""
    bl_idname = "vnt.remove_surface_region"
    bl_label = "Remove Surface Region"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_refinement_surfaces) > 0 and cs.cast_refinement_surfaces_index >= 0:
            surface = cs.cast_refinement_surfaces[cs.cast_refinement_surfaces_index]
            if len(surface.regions) > 0 and surface.regions_index >= 0:
                surface.regions.remove(surface.regions_index)
                if surface.regions_index > 0:
                    surface.regions_index -= 1
        return {'FINISHED'}

class VNT_OT_add_refinement_region(Operator):
    """Add a new refinement region"""
    bl_idname = "vnt.add_refinement_region"
    bl_label = "Add Refinement Region"
    
    region_name: StringProperty(
        name="Region Name",
        description="Name of the refinement region",
        default="region"
    )
    
    mode: EnumProperty(
        name="Mode",
        description="Refinement mode",
        items=[
            ('distance', "Distance", "Distance-based refinement"),
            ('inside', "Inside", "Refine cells inside the surface"),
            ('outside', "Outside", "Refine cells outside the surface")
        ],
        default='inside'
    )
    
    def execute(self, context):
        item = context.scene.cast_refinement_regions.add()
        item.name = self.region_name
        item.mode = self.mode
        
        if len(context.scene.geometry_items) > 0:
            item.geometry_object = context.scene.geometry_items[0].name
            
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "region_name")
        layout.prop(self, "mode")

class VNT_OT_remove_refinement_region(Operator):
    """Remove the selected refinement region"""
    bl_idname = "vnt.remove_refinement_region"
    bl_label = "Remove Refinement Region"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_refinement_regions) > 0 and cs.cast_refinement_regions_index >= 0:
            cs.cast_refinement_regions.remove(cs.cast_refinement_regions_index)
            if cs.cast_refinement_regions_index > 0:
                cs.cast_refinement_regions_index -= 1
        return {'FINISHED'}

# UI Lists for castellated mesh components
class CAST_UL_features_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "file", text="", emboss=False, icon="FILE")
            
            if item.use_levels:
                sub = row.row(align=True)
                sub.label(text=f"Levels: {item.distance} → {item.level_at_distance}")
            else:
                row.label(text=f"Level: {item.level}")

class CAST_UL_refinement_surfaces(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False, icon="SURFACE_DATA")
            row.label(text=f"Levels: {item.min_level}-{item.max_level}")

class CAST_UL_refinement_regions(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False, icon="MESH_CUBE")
            
            if item.mode == 'distance':
                row.label(text=f"Distance: {item.distance} → {item.level_at_distance}")
            else:
                row.label(text=f"{item.mode.capitalize()}: Level {item.level}")
