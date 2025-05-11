import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import (StringProperty, FloatProperty, IntProperty, 
                       BoolProperty, EnumProperty, CollectionProperty, 
                       PointerProperty, FloatVectorProperty)

# Property group to store snap controls settings
class SnapControlsProperties(PropertyGroup):
    """Properties for snappyHexMesh snap controls"""
    
    # Base snap settings
    nSmoothPatch: IntProperty(
        name="Smooth Patch Iterations",
        description="Number of patch smoothing iterations before finding correspondence to surface",
        default=3,
        min=0
    )
    
    tolerance: FloatProperty(
        name="Tolerance",
        description="Maximum relative distance for points to be attracted by surface",
        default=2.0,
        min=0.0
    )
    
    nSolveIter: IntProperty(
        name="Solve Iterations",
        description="Number of mesh displacement relaxation iterations",
        default=30,
        min=0
    )
    
    nRelaxIter: IntProperty(
        name="Relax Iterations",
        description="Maximum number of snapping relaxation iterations",
        default=5,
        min=0
    )
    
    # Feature snapping settings
    useFeatureSnap: BoolProperty(
        name="Use Feature Snapping",
        description="Enable feature edge snapping",
        default=True
    )
    
    nFeatureSnapIter: IntProperty(
        name="Feature Snap Iterations",
        description="Number of feature edge snapping iterations",
        default=10,
        min=0
    )
    
    implicitFeatureSnap: BoolProperty(
        name="Implicit Feature Snap",
        description="Detect features by sampling the surface",
        default=False
    )
    
    explicitFeatureSnap: BoolProperty(
        name="Explicit Feature Snap",
        description="Use castellatedMeshControls features",
        default=True
    )
    
    multiRegionFeatureSnap: BoolProperty(
        name="Multi-region Feature Snap",
        description="Detect features between multiple surfaces",
        default=False
    )

# Select/unselect operator for snap controls
class VNT_OT_select_unselect_allsnap(Operator):
    """Select/Unselect all snap features"""
    bl_idname = "vnt.select_unselect_allsnap"
    bl_label = "Select/Unselect all snap features"
    bl_description = "Select/Unselect all snap features from the list"
    bl_options = {'INTERNAL'}
    
    select_all: BoolProperty(
        default=False,
        name="Select all Items of List",
        options={'SKIP_SAVE'})
        
    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        cs = context.scene
        
        # Enable or disable feature snapping based on selection
        if self.select_all:
            cs.useFeatureSnap = True
        else:
            cs.useFeatureSnap = False
              
        return{'FINISHED'}
