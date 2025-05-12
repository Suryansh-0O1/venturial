"""
Mesh Quality control for SnappyHexMesh

This module defines the property groups and operators for the mesh quality settings
in SnappyHexMesh. It includes:
- Standard mesh quality constraints
- Advanced mesh quality settings
- Relaxed mesh quality parameters (used later in the meshing process)
- File selection operator for external mesh quality dictionaries
"""

import bpy
from bpy.props import (
    FloatProperty,
    BoolProperty,
    StringProperty,
    IntProperty,
    PointerProperty,
)

class MeshQualityProperties(bpy.types.PropertyGroup):
    """
    Property group for standard and advanced mesh quality settings.
    
    These settings control mesh quality checks during the SnappyHexMesh process.
    Standard settings affect the basic mesh quality constraints, while advanced
    settings provide finer control over specialized quality metrics.
    """
    
    #------------------------------------------------------
    # Standard Mesh Quality Constraints
    #------------------------------------------------------
    maxNonOrtho: FloatProperty(
        name="Max Non-Orthogonality",
        description="Maximum non-orthogonality allowed (angle in degrees)",
        default=65.0,
        min=0.0,
        max=180.0
    )
    
    maxBoundarySkewness: FloatProperty(
        name="Max Boundary Skewness",
        description="Maximum skewness allowed for boundary faces",
        default=20.0,
        min=0.0
    )
    
    maxInternalSkewness: FloatProperty(
        name="Max Internal Skewness",
        description="Maximum skewness allowed for internal faces",
        default=4.0,
        min=0.0
    )
    
    maxConcave: FloatProperty(
        name="Max Concaveness",
        description="Maximum concaveness allowed (angle in degrees)",
        default=80.0,
        min=0.0,
        max=180.0
    )
    
    minFlatness: FloatProperty(
        name="Min Flatness",
        description="Minimum flatness of faces (ratio of projected area to actual area)",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    minVol: FloatProperty(
        name="Min Volume",
        description="Minimum cell volume threshold",
        default=1e-13,
        precision=15
    )
    
    minTetQuality: FloatProperty(
        name="Min Tet Quality",
        description="Minimum quality of tetrahedral cells (0-1)",
        default=1e-30,
        min=0.0,
        max=1.0
    )
    
    #------------------------------------------------------
    # Advanced Mesh Quality Settings
    #------------------------------------------------------
    minVolCollapseRatio: FloatProperty(
        name="Min Volume Collapse Ratio",
        description="Only collapse cells with volume ratio larger than this value",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    minArea: FloatProperty(
        name="Min Area",
        description="Minimum face area (negative value disables this check)",
        default=-1.0
    )
    
    minTwist: FloatProperty(
        name="Min Twist",
        description="Minimum face twist measure (0-1)",
        default=0.02,
        min=0.0,
        max=1.0
    )
    
    minDeterminant: FloatProperty(
        name="Min Determinant",
        description="Minimum normalized cell determinant (measure of cell quality)",
        default=0.001,
        min=0.0,
        max=1.0
    )
    
    minFaceWeight: FloatProperty(
        name="Min Face Weight",
        description="Minimum weight factor for face interpolation",
        default=0.05,
        min=0.0,
        max=1.0
    )
    
    minVolRatio: FloatProperty(
        name="Min Volume Ratio", 
        description="Minimum ratio of neighboring cell volumes",
        default=0.01,
        min=0.0,
        max=1.0
    )
    
    minTriangleTwist: FloatProperty(
        name="Min Triangle Twist",
        description="Minimum triangle twist (negative value disables this check)",
        default=-1.0
    )
    
    #------------------------------------------------------
    # Error Distribution Settings
    #------------------------------------------------------
    nSmoothScale: IntProperty(
        name="Smooth Scale Iterations",
        description="Number of error distribution iterations",
        default=4,
        min=0
    )
    
    errorReduction: FloatProperty(
        name="Error Reduction",
        description="Amount to scale back displacement at error points",
        default=0.75,
        min=0.0,
        max=1.0
    )
    
    #------------------------------------------------------
    # External Dictionary Settings
    #------------------------------------------------------
    includeMeshQualityDict: BoolProperty(
        name="Include External Dictionary",
        description="Include external mesh quality dictionary file (overrides settings)",
        default=False
    )
    
    meshQualityDictPath: StringProperty(
        name="Dictionary Path",
        description="Path to external mesh quality dictionary file",
        default="meshQualityDict"
    )
    
    #------------------------------------------------------
    # UI Controls
    #------------------------------------------------------
    show_advanced_quality: BoolProperty(
        name="Show Advanced Settings",
        description="Show additional advanced mesh quality settings",
        default=False
    )


class RelaxedMeshQualityProperties(bpy.types.PropertyGroup):
    """
    Property group for relaxed mesh quality settings.
    
    These less stringent quality settings are used after reaching
    a specified number of iterations (nRelaxedIter) to allow the
    mesh generation process to complete when strict settings might
    cause it to fail.
    """
    
    maxNonOrtho: FloatProperty(
        name="Relaxed Max Non-Orthogonality",
        description="Maximum non-orthogonality allowed in relaxed mode",
        default=75.0,
        min=0.0,
        max=180.0
    )
    
    maxBoundarySkewness: FloatProperty(
        name="Relaxed Max Boundary Skewness",
        description="Maximum boundary face skewness allowed in relaxed mode",
        default=30.0,
        min=0.0
    )
    
    maxInternalSkewness: FloatProperty(
        name="Relaxed Max Internal Skewness",
        description="Maximum internal face skewness allowed in relaxed mode",
        default=8.0,
        min=0.0
    )
    
    maxConcave: FloatProperty(
        name="Relaxed Max Concaveness",
        description="Maximum concaveness allowed in relaxed mode",
        default=90.0,
        min=0.0,
        max=180.0
    )
    

class VNT_OT_select_mesh_quality_dict(bpy.types.Operator):
    """
    Operator to select an external mesh quality dictionary file.
    
    Opens a file browser to select a dictionary file containing
    mesh quality settings that will override the UI settings.
    """
    
    bl_idname = "vnt.select_mesh_quality_dict"
    bl_label = "Select Mesh Quality Dict"
    bl_description = "Browse for an external mesh quality dictionary file"
    
    filepath: StringProperty(
        name="File Path",
        description="Path to mesh quality dictionary file",
        default=""
    )
    
    def execute(self, context):
        context.scene.mesh_quality.meshQualityDictPath = self.filepath
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
