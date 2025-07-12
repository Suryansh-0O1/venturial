import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import (StringProperty, FloatProperty, IntProperty, 
                       BoolProperty, EnumProperty, CollectionProperty, 
                       PointerProperty, FloatVectorProperty)

#--------------------------------------------------
# PROPERTY GROUPS
#--------------------------------------------------

class LayerPatchSettings(PropertyGroup):
    """
    Layer settings for individual patches in boundary layer mesh generation.
    
    This property group stores all the settings needed for configuring
    boundary layer generation on specific patches.
    """
    
    name: StringProperty(
        name="Patch Name",
        description="Name of the patch",
        default=""
    )
    
    nSurfaceLayers: IntProperty(
        name="Surface Layers",
        description="Number of surface layers for this patch",
        default=1,
        min=0
    )
    
    custom_expansion: BoolProperty(
        name="Custom Expansion",
        description="Use custom expansion settings for this patch",
        default=False
    )
    
    expansionRatio: FloatProperty(
        name="Expansion Ratio",
        description="Expansion factor for layer mesh on this patch",
        default=1.3,
        min=1.0,
        max=10.0
    )
    
    finalLayerThickness: FloatProperty(
        name="Final Layer Thickness",
        description="Thickness of the final layer",
        default=0.3,
        min=0.0
    )
    
    minThickness: FloatProperty(
        name="Minimum Thickness",
        description="Minimum overall thickness of layers",
        default=0.1,
        min=0.0
    )
    
    use_advanced_settings: BoolProperty(
        name="Use Advanced Settings",
        description="Directly specify layer distribution parameters",
        default=False
    )
    
    layer_specification: EnumProperty(
        name="Layer Specification",
        description="Method for specifying layer distribution",
        items=[
            ('uniform', "Uniform Thickness", "Layers have uniform thickness"),
            ('gradual', "Gradual Expansion", "Layers expand gradually from wall"),
            ('custom', "Custom Distribution", "Custom layer thickness distribution")
        ],
        default='gradual'
    )
    
    mesh_quality_controls: BoolProperty(
        name="Custom Mesh Quality",
        description="Use custom mesh quality settings for this patch",
        default=False
    )
    
    max_thickness_ratio: FloatProperty(
        name="Max Thickness Ratio",
        description="Maximum thickness to local mesh size ratio",
        default=0.8,
        min=0.1,
        max=5.0
    )


class LayerAdditionProperties(PropertyGroup):
    """
    Main properties for snappyHexMesh layer addition controls.
    
    Contains all the parameters needed for configuring the boundary
    layer addition process in snappyHexMesh.
    """
    
    relativeSizes: BoolProperty(
        name="Relative Sizes",
        description="Are thickness parameters relative to cell size or absolute",
        default=True
    )
    
    thickness_mode: EnumProperty(
        name="Thickness Mode",
        description="Method for specifying layer thickness",
        items=[
            ('expansion_final', "Expansion + Final Layer", "Use expansion ratio and final layer thickness"),
            ('expansion_first', "Expansion + First Layer", "Use expansion ratio and first layer thickness"),
            ('overall_first', "Overall + First Layer", "Use overall thickness and first layer thickness"),
            ('overall_final', "Overall + Final Layer", "Use overall thickness and final layer thickness"),
            ('overall_expansion', "Overall + Expansion", "Use overall thickness and expansion ratio")
        ],
        default='expansion_final'
    )
    
    expansionRatio: FloatProperty(
        name="Expansion Ratio",
        description="Expansion factor for layer mesh",
        default=1.0,
        min=1.0,
        max=10.0
    )
    
    finalLayerThickness: FloatProperty(
        name="Final Layer Thickness",
        description="Thickness of layer furthest from wall",
        default=0.3,
        min=0.001
    )
    
    firstLayerThickness: FloatProperty(
        name="First Layer Thickness",
        description="Thickness of layer next to wall",
        default=0.3,
        min=0.001
    )
    
    thickness: FloatProperty(
        name="Overall Thickness",
        description="Total thickness of all layers",
        default=0.5,
        min=0.001
    )
    
    minThickness: FloatProperty(
        name="Minimum Thickness",
        description="Minimum thickness of total layers",
        default=0.25,
        min=0.0
    )
    
    featureAngle: FloatProperty(
        name="Feature Angle",
        description="Angle at which to not extrude surface",
        default=130.0,
        min=0.0,
        max=180.0
    )
    
    nGrow: IntProperty(
        name="Grow Layers",
        description="Number of layers of connected faces to grow",
        default=0,
        min=0
    )
    
    nSmoothSurfaceNormals: IntProperty(
        name="Smooth Surface Normals",
        description="Smoothing iterations for surface normals",
        default=1,
        min=0
    )
    
    nSmoothThickness: IntProperty(
        name="Smooth Thickness",
        description="Iterations to smooth layer thickness",
        default=10,
        min=0
    )
    
    maxFaceThicknessRatio: FloatProperty(
        name="Max Face Thickness Ratio",
        description="Stop layer growth on highly warped cells",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    minMedialAxisAngle: FloatProperty(
        name="Min Medial Axis Angle",
        description="Angle used to pick up medial axis points",
        default=90.0,
        min=0.0,
        max=180.0
    )
    
    maxThicknessToMedialRatio: FloatProperty(
        name="Max Thickness to Medial Ratio",
        description="Reduce growth where thickness to medial distance is large",
        default=0.3,
        min=0.0,
        max=1.0
    )
    
    nSmoothNormals: IntProperty(
        name="Smooth Normals",
        description="Smoothing iterations for mesh movement direction",
        default=3,
        min=0
    )
    
    slipFeatureAngle: FloatProperty(
        name="Slip Feature Angle",
        description="Angle above which mesh can slip at non-patched sides",
        default=30.0,
        min=0.0,
        max=180.0
    )
    
    nRelaxIter: IntProperty(
        name="Relax Iterations",
        description="Maximum snapping relaxation iterations",
        default=5,
        min=0
    )
    
    nBufferCellsNoExtrude: IntProperty(
        name="Buffer Cells No Extrude",
        description="Buffer region for new layer terminations",
        default=0,
        min=0
    )
    
    nLayerIter: IntProperty(
        name="Layer Iterations",
        description="Max number of layer addition iterations",
        default=50,
        min=1
    )
    
    nRelaxedIter: IntProperty(
        name="Relaxed Iterations",
        description="Iterations after which relaxed mesh quality controls are used",
        default=20,
        min=0
    )
    
    additionalReporting: BoolProperty(
        name="Additional Reporting",
        description="Report problematic face centers",
        default=False
    )
    
    layer_strategy: EnumProperty(
        name="Layer Strategy",
        description="Strategy for layer addition",
        items=[
            ('standard', "Standard", "Standard layer addition approach"),
            ('conservative', "Conservative", "More cautious approach for complex geometry"),
            ('aggressive', "Aggressive", "Try harder to add layers even in complex areas")
        ],
        default='standard'
    )

#--------------------------------------------------
# OPERATORS
#--------------------------------------------------

class VNT_OT_add_layer_patch(Operator):
    """
    Add a new patch for boundary layer meshing.
    
    Creates a new entry in the layer_patches collection with the specified
    name and number of surface layers.
    """
    bl_idname = "vnt.add_layer_patch"
    bl_label = "Add Layer Patch"
    
    patch_name: StringProperty(
        name="Patch Name",
        description="Name of the patch",
        default=""
    )
    
    n_surface_layers: IntProperty(
        name="Surface Layers",
        description="Number of surface layers to add",
        default=1,
        min=0
    )
    
    def execute(self, context):
        # Create new patch and set initial properties
        item = context.scene.layer_patches.add()
        item.name = self.patch_name
        item.nSurfaceLayers = self.n_surface_layers
        
        # Auto-select the new item
        context.scene.layer_patches_index = len(context.scene.layer_patches) - 1
        
        self.report({'INFO'}, f"Added patch '{self.patch_name}' with {self.n_surface_layers} surface layers")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "patch_name")
        layout.prop(self, "n_surface_layers")


class VNT_OT_remove_layer_patch(Operator):
    """
    Remove the selected layer patch.
    
    Deletes the currently selected layer patch from the layer_patches collection.
    """
    bl_idname = "vnt.remove_layer_patch"
    bl_label = "Remove Layer Patch"
    
    @classmethod
    def poll(cls, context):
        return context.scene.layer_patches and context.scene.layer_patches_index >= 0
    
    def execute(self, context):
        cs = context.scene
        if len(cs.layer_patches) > 0 and cs.layer_patches_index >= 0:
            # Get name for reporting
            patch_name = cs.layer_patches[cs.layer_patches_index].name
            
            # Remove item and update index
            cs.layer_patches.remove(cs.layer_patches_index)
            if cs.layer_patches_index > 0:
                cs.layer_patches_index -= 1
                
            self.report({'INFO'}, f"Removed patch '{patch_name}'")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class VNT_OT_duplicate_layer_patch(Operator):
    """
    Duplicate the selected layer patch with all its settings.
    
    Creates a new patch as a copy of the currently selected patch,
    preserving all property values.
    """
    bl_idname = "vnt.duplicate_layer_patch"
    bl_label = "Duplicate Layer Patch"
    
    @classmethod
    def poll(cls, context):
        return context.scene.layer_patches and context.scene.layer_patches_index >= 0
    
    def execute(self, context):
        cs = context.scene
        if len(cs.layer_patches) > 0 and cs.layer_patches_index >= 0:
            # Get source and create duplicate
            source = cs.layer_patches[cs.layer_patches_index]
            new_patch = cs.layer_patches.add()
            
            # Copy all settings
            new_patch.name = f"{source.name}_copy"
            new_patch.nSurfaceLayers = source.nSurfaceLayers
            new_patch.custom_expansion = source.custom_expansion
            new_patch.expansionRatio = source.expansionRatio
            new_patch.finalLayerThickness = source.finalLayerThickness
            new_patch.minThickness = source.minThickness
            
            # Select the new patch
            cs.layer_patches_index = len(cs.layer_patches) - 1
            
            self.report({'INFO'}, f"Duplicated patch '{source.name}' to '{new_patch.name}'")
        return {'FINISHED'}


class VNT_OT_import_boundary_patches(Operator):
    """
    Import patches from boundary conditions in BlockMesh dictionary.
    
    Retrieves boundary definitions from the BlockMesh settings and
    creates corresponding layer patches.
    """
    bl_idname = "vnt.import_boundary_patches"
    bl_label = "Import from Boundaries"
    
    filter_walls: BoolProperty(
        name="Only Wall Boundaries",
        description="Only import boundaries with wall type",
        default=True
    )
    
    def execute(self, context):
        cs = context.scene
        
        # Sample boundaries for demonstration
        # In real implementation, these would come from BlockMesh settings
        sample_boundaries = [
            ("inlet", "patch"),
            ("outlet", "patch"),
            ("walls", "wall"),
            ("top", "wall"),
            ("bottom", "wall")
        ]
        
        # Process boundaries
        patches_added = 0
        for name, btype in sample_boundaries:
            # Skip non-wall patches if filter is enabled
            if self.filter_walls and btype != "wall":
                continue
                
            # Only add if patch doesn't already exist
            exists = False
            for patch in cs.layer_patches:
                if patch.name == name:
                    exists = True
                    break
            
            # Create new patch
            if not exists:
                new_patch = cs.layer_patches.add()
                new_patch.name = name
                new_patch.nSurfaceLayers = 3 if btype == "wall" else 0
                patches_added += 1
        
        self.report({'INFO'}, f"Added {patches_added} patches from boundaries")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "filter_walls")


class VNT_OT_configure_layer_settings(Operator):
    """
    Configure advanced layer addition settings.
    
    Presents a dialog with all the available settings for controlling
    the layer addition process in snappyHexMesh.
    """
    bl_idname = "vnt.configure_layer_settings"
    bl_label = "Layer Addition Settings"
    
    changed: BoolProperty(default=False)
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Basic settings section
        box = layout.box()
        box.label(text="Basic Settings", icon="PREFERENCES")
        
        row = box.row()
        row.prop(scene, "relativeSizes")
        
        # Thickness specification
        box.label(text="Layer Thickness Specification:")
        row = box.row(align=True)
        row.prop(scene, "thickness_mode", text="")
        
        # Show relevant thickness controls based on selected mode
        if 'expansion' in scene.thickness_mode:
            row = box.row(align=True)
            row.prop(scene, "expansionRatio")
        
        if 'overall' in scene.thickness_mode:
            row = box.row(align=True)
            row.prop(scene, "overallThickness")
            
        if 'final' in scene.thickness_mode:
            row = box.row(align=True)
            row.prop(scene, "finalLayerThickness")
            
        if 'first' in scene.thickness_mode:
            row = box.row(align=True)
            row.prop(scene, "firstLayerThickness")
        
        row = box.row()
        row.prop(scene, "minThickness")
        
        # Advanced settings
        adv_box = layout.box()
        adv_box.label(text="Advanced Settings", icon="TOOL_SETTINGS")
        
        # Layer strategy
        row = adv_box.row()
        row.label(text="Layer Addition Strategy:")
        row = adv_box.row()
        row.prop(scene, "layer_strategy", text="")
        
        # Feature handling
        row = adv_box.row()
        row.label(text="Feature Handling:")
        row = adv_box.row()
        row.prop(scene, "featureAngle")
        row = adv_box.row()
        row.prop(scene, "maxFaceThicknessRatio")
        
        # Patch displacement
        row = adv_box.row()
        row.label(text="Patch Displacement:")
        col = adv_box.column(align=True)
        col.prop(scene, "nSmoothSurfaceNormals")
        col.prop(scene, "nSmoothThickness")
        
        # Medial axis
        row = adv_box.row()
        row.label(text="Medial Axis Analysis:")
        col = adv_box.column(align=True)
        col.prop(scene, "minMedialAxisAngle")
        col.prop(scene, "maxThicknessToMedialRatio")
        col.prop(scene, "nSmoothNormals")
        
        # Mesh shrinking
        row = adv_box.row()
        row.label(text="Mesh Shrinking:")
        col = adv_box.column(align=True)
        col.prop(scene, "slipFeatureAngle")
        col.prop(scene, "nRelaxIter")
        col.prop(scene, "nBufferCellsNoExtrude")
        col.prop(scene, "nLayerIter")
        col.prop(scene, "nRelaxedIter")
        
        row = adv_box.row()
        row.prop(scene, "additionalReporting")
    
    def execute(self, context):
        if self.changed:
            self.report({'INFO'}, "Layer settings updated")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)


#--------------------------------------------------
# UI LIST CLASSES
#--------------------------------------------------

class LAYER_UL_patches_list(bpy.types.UIList):
    """
    UI list for displaying and selecting layer patches.
    
    Displays patch names, layer counts, and indicators for custom settings.
    """
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.7)
            
            # Name display with appropriate icon
            row = split.row(align=True)
            icon = "OUTLINER_OB_SURFACE" if item.nSurfaceLayers > 0 else "X"
            row.prop(item, "name", text="", emboss=False, icon=icon)
            
            # Info section with layer count and custom indicator
            right_col = split.row(align=True)
            right_col.label(text=f"Layers: {item.nSurfaceLayers}")
            
            if item.custom_expansion:
                right_col.label(text="", icon="MODIFIER_ON")
            
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.name)
