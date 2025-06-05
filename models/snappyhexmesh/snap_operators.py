"""
Snap controls module for snappyHexMesh functionality.

This module provides classes for defining snappyHexMesh snap controls properties
and operators to manipulate them within the Blender interface.
"""

import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import (StringProperty, FloatProperty, IntProperty, 
                       BoolProperty, EnumProperty, CollectionProperty, 
                       PointerProperty, FloatVectorProperty)


class SnapControlsProperties(PropertyGroup):
    """
    Properties for snappyHexMesh snap controls.
    
    This property group stores all settings related to the snapping phase
    of snappyHexMesh, including basic snapping parameters and feature
    snapping options.
    """
    
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


class VNT_OT_select_unselect_allsnap(Operator):
    """
    Operator to toggle selection of all snap features.
    
    This operator provides a convenient way to enable or disable
    feature snapping in the snappyHexMesh setup.
    """
    bl_idname = "vnt.select_unselect_allsnap"
    bl_label = "Select/Unselect all snap features"
    bl_description = "Select/Unselect all snap features from the list"
    bl_options = {'INTERNAL'}
    
    select_all: BoolProperty(
        default=False,
        name="Select all Items of List",
        options={'SKIP_SAVE'}
    )
        
    @classmethod
    def poll(cls, context):
        """
        Check if the operator can be executed.
        
        Args:
            context: Blender context
            
        Returns:
            bool: Always True for this operator
        """
        return True

    def execute(self, context):
        """
        Execute the operator to select or unselect all snap features.
        
        Args:
            context: Blender context
            
        Returns:
            dict: Operator result
        """
        cs = context.scene
        
        # Enable or disable feature snapping based on selection
        cs.useFeatureSnap = self.select_all
              
        return{'FINISHED'}
