import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import (StringProperty, FloatProperty, IntProperty, 
                       BoolProperty, EnumProperty, CollectionProperty, 
                       PointerProperty, FloatVectorProperty)

# Property group for patch-specific layer settings
class LayerPatchSettings(PropertyGroup):
    """Layer settings for individual patches"""
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

# Property group for main layer addition controls
class LayerAdditionProperties(PropertyGroup):
    """Main properties for snappyHexMesh layer addition controls"""
    
    # Basic layer settings
    relativeSizes: BoolProperty(
        name="Relative Sizes",
        description="Are thickness parameters relative to cell size or absolute",
        default=True
    )
    
    # Layer thickness specification options
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
    
    # Advanced settings - Feature angle control
    featureAngle: FloatProperty(
        name="Feature Angle",
        description="Angle at which to not extrude surface",
        default=130.0,
        min=0.0,
        max=180.0
    )
    
    # Growth control
    nGrow: IntProperty(
        name="Grow Layers",
        description="Number of layers of connected faces to grow",
        default=0,
        min=0
    )
    
    # Patch displacement settings
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
    
    # Cell ratio controls
    maxFaceThicknessRatio: FloatProperty(
        name="Max Face Thickness Ratio",
        description="Stop layer growth on highly warped cells",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    # Medial axis settings
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
    
    # Mesh shrinking
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

# Operator to add a new layer patch setting
class VNT_OT_add_layer_patch(Operator):
    """Add a new patch for layer settings"""
    bl_idname = "vnt.add_layer_patch"
    bl_label = "Add Layer Patch"
    
    patch_name: StringProperty(
        name="Patch Name",
        description="Name of the patch",
        default=""
    )
    
    def execute(self, context):
        item = context.scene.layer_patches.add()
        item.name = self.patch_name
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "patch_name")

# Operator to remove a layer patch setting
class VNT_OT_remove_layer_patch(Operator):
    """Remove the selected layer patch"""
    bl_idname = "vnt.remove_layer_patch"
    bl_label = "Remove Layer Patch"
    
    def execute(self, context):
        cs = context.scene
        if len(cs.layer_patches) > 0 and cs.layer_patches_index >= 0:
            cs.layer_patches.remove(cs.layer_patches_index)
            if cs.layer_patches_index > 0:
                cs.layer_patches_index -= 1
        return {'FINISHED'}

# UI List for layer patches
class LAYER_UL_patches_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, "name", text="", emboss=False, icon="SURFACE_DATA")
            row.label(text=f"Layers: {item.nSurfaceLayers}")
            
            if item.custom_expansion:
                icon = "CHECKMARK"
            else:
                icon = "BLANK1"
            row.label(text="", icon=icon)
