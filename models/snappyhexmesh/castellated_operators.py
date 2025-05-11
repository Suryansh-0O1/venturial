import bpy
from bpy.types import Operator, PropertyGroup, UIList
from bpy.props import (
    StringProperty, FloatProperty, IntProperty, BoolProperty, 
    EnumProperty, CollectionProperty, PointerProperty
)
from bpy_extras.io_utils import ImportHelper, ExportHelper
import os

# --- DATA STRUCTURES ---

class DistanceLevelPair(PropertyGroup):
    """Distance-level pair for refinement control"""
    distance: FloatProperty(
        name="Distance",
        description="Distance from surface where refinement level changes. Measured in mesh units from the specified geometry. Smaller values create refinement closer to the surface.",
        default=1.0,
        min=0.0
    )
    
    level: IntProperty(
        name="Level",
        description="Refinement level to apply at this distance. Higher values create smaller cells. Each level doubles the resolution by splitting cells in each direction.",
        default=1,
        min=0
    )

class CastellatedFeature(PropertyGroup):
    """Feature edge specification for castellated mesh"""
    file: StringProperty(
        name="File",
        description="Path to eMesh file containing feature edges. This file defines explicit edges requiring special refinement, typically sharp edges exported from CAD or extracted using surfaceFeatureExtract utility.",
        default=""
    )
    
    refinement_mode: EnumProperty(
        name="Mode",
        description="Method for specifying feature refinement:\n• Uniform Level: Apply same refinement level everywhere along feature\n• Single Distance: Define one distance-level pair for gradual refinement\n• Multiple Distances: Define multiple distance-level pairs for fine control over refinement gradient",
        items=[
            ('uniform', "Uniform Level", "Single level for entire feature"),
            ('single_distance', "Single Distance", "One distance-level pair"),
            ('multi_distance', "Multiple Distances", "Multiple distance-level pairs")
        ],
        default='uniform'
    )
    
    level: IntProperty(
        name="Level",
        description="Refinement level for uniform mode. Higher values create finer cells along feature edges. Each level doubles the resolution. Values 2-4 are common for most applications.",
        default=2,
        min=0
    )
    
    distance: FloatProperty(
        name="Distance",
        description="Distance from feature edge where refinement begins. Measured in mesh units. Controls how far from the edge the refinement extends. Use small values (0.1-1.0) for accurate feature capture.",
        default=0.0,
        min=0.0
    )
    
    level_at_distance: IntProperty(
        name="Level",
        description="Refinement level to apply at the specified distance. For transitions, use higher levels near the feature (distance=0) and lower levels farther away. Each level doubles the resolution.",
        default=2,
        min=0
    )
    
    # Collection property added during registration

class PatchInfo(PropertyGroup):
    """Patch information for boundary regions"""
    patch_type: EnumProperty(
        name="Type",
        description="Type of boundary condition to apply to this surface region:\n• Patch: Standard boundary with value specification\n• Wall: Solid wall boundary (no-slip typically)\n• Symmetry: Mirror symmetry plane (no flow across)\n• Empty: Empty patch for 2D simulations\n• Wedge: For axisymmetric simulations",
        items=[
            ('patch', "Patch", "Standard boundary patch"),
            ('wall', "Wall", "Wall boundary"),
            ('symmetry', "Symmetry", "Symmetry plane"),
            ('empty', "Empty", "Empty patch (2D simulation)"),
            ('wedge', "Wedge", "Axisymmetric wedge boundary")
        ],
        default='patch'
    )
    
    in_group: StringProperty(
        name="Group",
        description="Optional patch group name to organize related patches together. Common groups include 'walls', 'inlets', etc. Helps organize boundaries in paraview and simplifies boundary condition application.",
        default="meshedPatches"
    )

class RefinementSurfaceRegion(PropertyGroup):
    """Region within a refinement surface with specific settings"""
    name: StringProperty(
        name="Name",
        description="Name identifying this region in the mesh. Region names should be descriptive (e.g., 'inlet', 'outlet', 'wing_surface') and match those defined in the STL file if applicable.",
        default="region"
    )
    
    min_level: IntProperty(
        name="Min",
        description="Minimum refinement level guaranteed across this surface region. Higher values create smaller cells. Each level doubles the resolution. Values 1-3 are typical for basic refinement.",
        default=2,
        min=0
    )
    
    max_level: IntProperty(
        name="Max",
        description="Maximum refinement level applied at surface curvature, features and regions of interest. Each level doubles resolution. The difference between min and max controls adaptation to features.",
        default=2,
        min=0
    )
    
    use_patch_info: BoolProperty(
        name="Use Patch Info",
        description="Enable to specify this region as a boundary patch with specific boundary condition type. Required for defining inlets, outlets, walls and other boundary conditions.",
        default=False
    )
    
    patch_info: PointerProperty(
        type=PatchInfo
    )

class RefinementSurface(PropertyGroup):
    """Surface for mesh refinement (STL or geometry object)"""
    name: StringProperty(
        name="Name",
        description="Name identifying this surface in the mesh and dictionary. Should be unique and descriptive of the geometry (e.g., 'car_body', 'propeller', 'building').",
        default="surface"
    )
    
    source_type: EnumProperty(
        name="Source",
        description="Type of geometry source to use for refinement:\n• Geometry Object: Use a mesh from the current Blender scene\n• STL File: Use an external STL file typically exported from CAD software",
        items=[
            ('geometry', "Geometry Object", "Blender mesh object"),
            ('stl', "STL File", "Imported STL file")
        ],
        default='geometry'
    )
    
    geometry_object: StringProperty(
        name="Object",
        description="Name of the Blender object to use as geometry source. The object must exist in the current scene and have a valid mesh that will be exported to STL when generating the mesh.",
        default=""
    )
    
    min_level: IntProperty(
        name="Min",
        description="Minimum refinement level guaranteed throughout this surface. Higher values (1-3) create smaller cells. Each level doubles the resolution. Start with low values and increase as needed.",
        default=2,
        min=0
    )
    
    max_level: IntProperty(
        name="Max",
        description="Maximum refinement level applied at surface curvature and features. Values 2-4 are common. The difference between min and max determines how adaptive the mesh is to geometric features.",
        default=2,
        min=0
    )
    
    # Collections and references
    regions: CollectionProperty(
        type=RefinementSurfaceRegion,
        name="Regions"
    )
    
    regions_index: IntProperty(default=0)
    
    # Zone properties
    face_zone: StringProperty(
        name="Face Zone",
        description="Optional name for face zone identification. Face zones allow boundary conditions to be applied to interior surfaces (e.g., for baffles, porous media interfaces, or fan boundaries).",
        default=""
    )
    
    cell_zone: StringProperty(
        name="Cell Zone",
        description="Optional name for cell zone identification. Cell zones define regions with different material properties or physics models (e.g., porous zones, MRF regions for rotating machinery).",
        default=""
    )
    
    cell_zone_inside: EnumProperty(
        name="Inside",
        description="For enclosed surfaces with cell zones, specifies which side is considered 'inside'. This determines whether cells inside or outside the closed surface are included in the cell zone.",
        items=[
            ('inside', "Inside", "Inside the surface"),
            ('outside', "Outside", "Outside the surface")
        ],
        default='inside'
    )

class RefinementRegion(PropertyGroup):
    """Volume region for refinement"""
    name: StringProperty(
        name="Name",
        description="Name identifying this volumetric refinement region. Use descriptive names that indicate purpose (e.g., 'wake_region', 'boundary_layer_box', 'mixing_zone').",
        default="region"
    )
    
    source_type: EnumProperty(
        name="Source",
        description="Type of geometry source defining the region's shape:\n• Geometry Object: Use a mesh object from the current Blender scene (must be watertight for 'inside' mode)\n• STL File: Use an external STL file typically from CAD software",
        items=[
            ('geometry', "Geometry Object", "Blender mesh object"),
            ('stl', "STL File", "Imported STL file")
        ],
        default='geometry'
    )
    
    geometry_object: StringProperty(
        name="Object",
        description="Name of the Blender object that defines this refinement region. For 'inside' mode, this should be a closed watertight mesh. For 'distance' mode, it can be any mesh surface.",
        default=""
    )
    
    mode: EnumProperty(
        name="Mode",
        description="Refinement method for this region:\n• Inside: Refine all cells inside the volume (requires closed geometry)\n• Distance: Refine cells within specified distance from the surface (allows gradual refinement based on distance)",
        items=[
            ('inside', "Inside", "Refine inside region"),
            ('distance', "Distance", "Distance-based refinement")
        ],
        default='inside'
    )
    
    # Settings for 'inside' mode
    level: IntProperty(
        name="Level",
        description="Refinement level to apply inside the region. Higher values create smaller cells throughout the volume. Each level doubles the resolution in each direction, so increases cell count by 8x.",
        default=1,
        min=0
    )
    
    # Settings for 'distance' mode
    use_advanced_distance: BoolProperty(
        name="Multiple Levels",
        description="Enable to specify multiple distance-level pairs for more gradual transitions. This creates smoother refinement changes as distance from the surface increases.",
        default=False
    )
    
    distance: FloatProperty(
        name="Distance",
        description="Distance from surface where refinement is applied. Measured in mesh units. Larger values create a wider refined region around the geometry. Use appropriate values based on your domain scale.",
        default=1.0,
        min=0.0
    )
    
    level_at_distance: IntProperty(
        name="Level",
        description="Refinement level to apply at specified distance. For wake regions, typically use 1-2 for large volumes. Higher values significantly increase cell count. Balance refinement against computational cost.",
        default=1,
        min=0
    )

# --- OPERATORS ---

class VNT_OT_add_feature(Operator, ImportHelper):
    """Add a feature edge file for refinement"""
    bl_idname = "vnt.add_feature"
    bl_label = "Add Feature"
    
    filename_ext = ".eMesh"
    filter_glob: StringProperty(default="*.eMesh", options={'HIDDEN'})
    
    def execute(self, context):
        feature = context.scene.cast_features.add()
        if self.filepath:
            feature.file = self.filepath
            feature.name = os.path.basename(self.filepath)
        return {'FINISHED'}

class VNT_OT_browse_feature_file(Operator, ImportHelper):
    """Select a feature edge mesh file"""
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
    """Remove selected feature edge"""
    bl_idname = "vnt.remove_feature"
    bl_label = "Remove Feature"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_features) > 0 and cs.cast_features_index >= 0:
            cs.cast_features.remove(cs.cast_features_index)
            if cs.cast_features_index > 0:
                cs.cast_features_index -= 1
        return {'FINISHED'}

class VNT_OT_add_feature_distance_level_pair(Operator):
    """Add distance-level pair to feature refinement"""
    bl_idname = "vnt.add_feature_distance_level_pair"
    bl_label = "Add Distance-Level Pair"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_features) > 0 and cs.cast_features_index >= 0:
            feature = cs.cast_features[cs.cast_features_index]
            pair = feature.distance_level_pairs.add()
            if len(feature.distance_level_pairs) > 1:
                # Set reasonable default based on previous pair
                last_pair = feature.distance_level_pairs[len(feature.distance_level_pairs)-2]
                pair.distance = last_pair.distance + 1.0
                pair.level = last_pair.level + 1
            else:
                # First pair usually starts at distance 0.0
                pair.distance = 0.0
                pair.level = feature.level or 2
        return {'FINISHED'}

class VNT_OT_remove_feature_distance_level_pair(Operator):
    """Remove distance-level pair from feature refinement"""
    bl_idname = "vnt.remove_feature_distance_level_pair"
    bl_label = "Remove Distance-Level Pair"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_features) > 0 and cs.cast_features_index >= 0:
            feature = cs.cast_features[cs.cast_features_index]
            if len(feature.distance_level_pairs) > 0 and feature.distance_level_pairs_index >= 0:
                feature.distance_level_pairs.remove(feature.distance_level_pairs_index)
                if feature.distance_level_pairs_index > 0:
                    feature.distance_level_pairs_index -= 1
        return {'FINISHED'}

class VNT_OT_add_refinement_surface(Operator):
    """Add surface for mesh refinement"""
    bl_idname = "vnt.add_refinement_surface"
    bl_label = "Add Refinement Surface"
    
    def execute(self, context):
        surface = context.scene.cast_refinement_surfaces.add()
        
        # Set defaults from existing geometry if available
        if len(context.scene.geometry_items) > 0:
            surface.geometry_object = context.scene.geometry_items[0].name
            
        return {'FINISHED'}

class VNT_OT_browse_surface_file(Operator, ImportHelper):
    """Select STL file for surface refinement"""
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
    """Remove surface refinement"""
    bl_idname = "vnt.remove_refinement_surface"
    bl_label = "Remove Surface"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_refinement_surfaces) > 0 and cs.cast_refinement_surfaces_index >= 0:
            cs.cast_refinement_surfaces.remove(cs.cast_refinement_surfaces_index)
            if cs.cast_refinement_surfaces_index > 0:
                cs.cast_refinement_surfaces_index -= 1
        return {'FINISHED'}

class VNT_OT_add_surface_region(Operator):
    """Add region to surface for local refinement"""
    bl_idname = "vnt.add_surface_region"
    bl_label = "Add Region"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_refinement_surfaces) > 0 and cs.cast_refinement_surfaces_index >= 0:
            surface = cs.cast_refinement_surfaces[cs.cast_refinement_surfaces_index]
            region = surface.regions.add()
            
            # Set default name
            region.name = f"region_{len(surface.regions)}"
            
            # Copy refinement levels from parent surface
            region.min_level = surface.min_level
            region.max_level = surface.max_level
        return {'FINISHED'}

class VNT_OT_remove_surface_region(Operator):
    """Remove region from surface"""
    bl_idname = "vnt.remove_surface_region"
    bl_label = "Remove Region"
    
    index: IntProperty(default=-1, options={'HIDDEN'})
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_refinement_surfaces) > 0 and cs.cast_refinement_surfaces_index >= 0:
            surface = cs.cast_refinement_surfaces[cs.cast_refinement_surfaces_index]
            
            # Remove by direct index if provided, otherwise use the selected index
            if self.index >= 0 and self.index < len(surface.regions):
                surface.regions.remove(self.index)
            elif surface.regions_index >= 0 and surface.regions_index < len(surface.regions):
                surface.regions.remove(surface.regions_index)
            
            # Adjust the index if needed
            if surface.regions_index >= len(surface.regions) and len(surface.regions) > 0:
                surface.regions_index = len(surface.regions) - 1
        
        return {'FINISHED'}

class VNT_OT_add_refinement_region(Operator):
    """Add volumetric refinement region"""
    bl_idname = "vnt.add_refinement_region"
    bl_label = "Add Refinement Region"
    
    region_name: StringProperty(
        name="Name",
        description="Region name",
        default="region"
    )
    
    mode: EnumProperty(
        name="Mode",
        description="Refinement mode",
        items=[
            ('inside', "Inside", "Refine inside region"),
            ('distance', "Distance", "Distance-based refinement")
        ],
        default='inside'
    )
    
    def execute(self, context):
        region = context.scene.cast_refinement_regions.add()
        region.name = self.region_name
        region.mode = self.mode
        
        # Set default geometry if available
        if len(context.scene.geometry_items) > 0:
            region.geometry_object = context.scene.geometry_items[0].name
            
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class VNT_OT_remove_refinement_region(Operator):
    """Remove volumetric refinement region"""
    bl_idname = "vnt.remove_refinement_region"
    bl_label = "Remove Region"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_refinement_regions) > 0 and cs.cast_refinement_regions_index >= 0:
            cs.cast_refinement_regions.remove(cs.cast_refinement_regions_index)
            if cs.cast_refinement_regions_index > 0:
                cs.cast_refinement_regions_index -= 1
        return {'FINISHED'}

class VNT_OT_add_distance_level_pair(Operator):
    """Add distance-level pair to region refinement"""
    bl_idname = "vnt.add_distance_level_pair"
    bl_label = "Add Distance-Level Pair"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_refinement_regions) > 0 and cs.cast_refinement_regions_index >= 0:
            region = cs.cast_refinement_regions[cs.cast_refinement_regions_index]
            pair = region.distance_level_pairs.add()
            
            if len(region.distance_level_pairs) > 1:
                # Set sensible defaults based on previous pair
                last_pair = region.distance_level_pairs[len(region.distance_level_pairs)-2]
                pair.distance = last_pair.distance * 1.5  # Increase distance
                pair.level = max(1, last_pair.level - 1)  # Decrease refinement
            else:
                # First pair defaults
                pair.distance = 1.0
                pair.level = 3
        return {'FINISHED'}

class VNT_OT_remove_distance_level_pair(Operator):
    """Remove distance-level pair from region refinement"""
    bl_idname = "vnt.remove_distance_level_pair"
    bl_label = "Remove Distance-Level Pair"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.cast_refinement_regions) > 0 and cs.cast_refinement_regions_index >= 0:
            region = cs.cast_refinement_regions[cs.cast_refinement_regions_index]
            if len(region.distance_level_pairs) > 0 and region.distance_level_pairs_index >= 0:
                region.distance_level_pairs.remove(region.distance_level_pairs_index)
                if region.distance_level_pairs_index > 0:
                    region.distance_level_pairs_index -= 1
        return {'FINISHED'}

# --- UI LIST CLASSES ---

class CAST_UL_features_list(UIList):
    """Display list of feature edges for refinement"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            
            # Show file path or just filename
            if item.file:
                filename = os.path.basename(item.file)
                row.prop(item, "file", text=filename, emboss=False, icon="FILE")
            else:
                row.prop(item, "file", text="", emboss=False, icon="FILE")
            
            # Show refinement info based on mode
            if item.refinement_mode == 'uniform':
                row.label(text=f"Level: {item.level}")
            elif item.refinement_mode == 'single_distance':
                row.label(text=f"Dist: {item.distance} → Lvl: {item.level_at_distance}")
            elif item.refinement_mode == 'multi_distance':
                if len(item.distance_level_pairs) > 0:
                    row.label(text=f"{len(item.distance_level_pairs)} distance pairs")
                else:
                    row.label(text="No distance pairs")

class CAST_UL_refinement_surfaces(UIList):
    """Display list of refinement surfaces"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            
            if item.source_type == 'geometry':
                if item.geometry_object:
                    row.prop(item, "geometry_object", text="", emboss=False, icon="MESH_DATA")
                else:
                    row.prop(item, "name", text="", emboss=False, icon="MESH_DATA")
            else:
                row.prop(item, "name", text="", emboss=False, icon="SURFACE_DATA")
                
            row.label(text=f"Levels: {item.min_level}-{item.max_level}")

class CAST_UL_refinement_regions(UIList):
    """Display list of refinement regions"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.7)
            
            # Icon based on mode
            icon_val = 'CUBE' if item.mode == 'inside' else 'FULLSCREEN_ENTER'
            split.prop(item, "name", text="", emboss=False, icon=icon_val)
            
            # Show refinement info
            if item.mode == 'distance':
                if item.use_advanced_distance and len(item.distance_level_pairs) > 0:
                    split.label(text=f"Distance: {len(item.distance_level_pairs)} pairs")
                else:
                    split.label(text=f"Dist: {item.distance} → Lvl: {item.level_at_distance}")
            else:
                split.label(text=f"Level: {item.level}")

class CAST_UL_distance_level_pairs(UIList):
    """Display list of distance-level pairs"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "distance", text="Distance")
            row.prop(item, "level", text="Level")

class CAST_UL_feature_distance_level_pairs(UIList):
    """Display list of distance-level pairs for features"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "distance", text="Distance")
            row.prop(item, "level", text="Level")

class CAST_UL_surface_regions(UIList):
    """Display list of surface regions"""
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.7)
            
            # Name with icon
            split.prop(item, "name", text="", emboss=False, icon='SURFACE_DATA')
            
            # Show the refinement levels
            split.label(text=f"Level: {item.min_level}-{item.max_level}")
            
            # Visual indicator for patch info
            if item.use_patch_info:
                layout.label(icon="MATERIAL")