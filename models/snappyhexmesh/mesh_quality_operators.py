"""
Mesh Quality Control for SnappyHexMesh

This module provides property groups and operators for configuring mesh quality settings
in SnappyHexMesh. It implements:

- Standard mesh quality constraints with industry-standard defaults
- Advanced mesh quality parameters for fine-tuning
- Relaxed mesh quality settings for iterative refinement processes
- File selection capability for external mesh quality dictionaries
"""

import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import (
    StringProperty, FloatProperty, IntProperty, BoolProperty, 
    EnumProperty, PointerProperty
)
from bpy_extras.io_utils import ImportHelper


class MeshQualityProperties(PropertyGroup):
    """
    Standard mesh quality settings for SnappyHexMesh.
    
    This property group defines all mesh quality parameters that can be adjusted
    to control the mesh generation process, including standard and advanced constraints.
    """
    
    # External dictionary includes
    includeMeshQualityDict: BoolProperty(
        name="Use External Dictionary",
        description="Include external mesh quality dictionary file",
        default=False
    )
    
    meshQualityDictPath: StringProperty(
        name="Mesh Quality Dict Path",
        description="Path to external mesh quality dictionary file",
        default="meshQualityDict"
    )
    
    # Standard constraints
    maxNonOrtho: FloatProperty(
        name="Max Non-Orthogonality",
        description="Maximum non-orthogonality allowed. 0=orthogonal, 90=bad. Values over 70-80 may lead to robustness issues.",
        default=65.0,
        min=0.0,
        max=180.0
    )
    
    maxBoundarySkewness: FloatProperty(
        name="Max Boundary Skewness",
        description="Maximum boundary face skewness allowed. Lower is better. Values over 4-5 may affect stability.",
        default=20.0,
        min=0.0,
        soft_max=20.0
    )
    
    maxInternalSkewness: FloatProperty(
        name="Max Internal Skewness",
        description="Maximum internal face skewness allowed. Lower is better. Values over 4-5 may affect stability.",
        default=4.0,
        min=0.0,
        soft_max=10.0
    )
    
    maxConcave: FloatProperty(
        name="Max Concaveness",
        description="Maximum concaveness allowed in degrees. 0=not concave, 180=fully concave. Lower is better.",
        default=80.0,
        min=0.0,
        max=180.0
    )
    
    minFlatness: FloatProperty(
        name="Min Flatness",
        description="Minimum face flatness (1=flat, 0=degenerate). Values below 0.5 may indicate poor mesh quality.",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    minVol: FloatProperty(
        name="Min Volume",
        description="Minimum normalized cell volume. Small values can indicate poor mesh quality.",
        default=1e-13,
        min=0.0,
    )
    
    minTetQuality: FloatProperty(
        name="Min Tet Quality",
        description="Minimum quality of tetrahedral cells. Higher is better.",
        default=1e-30,
        min=0.0
    )
    
    # Advanced constraints
    minVolCollapseRatio: FloatProperty(
        name="Min Volume Collapse Ratio",
        description="Minimum volume ratio for collapsed cells. Higher values preserve more of original cell volume.",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    minArea: FloatProperty(
        name="Min Area",
        description="Minimum normalized face area (0=degenerate). Use 0 to disable check.",
        default=0.0,
        min=0.0
    )
    
    minTwist: FloatProperty(
        name="Min Twist",
        description="Minimum face twist (0=twisted, 1=not twisted). Values below 0.02 are problematic.",
        default=0.02,
        min=0.0,
        max=1.0
    )
    
    minDeterminant: FloatProperty(
        name="Min Determinant",
        description="Minimum normalized cell determinant. 1=regular, 0=degenerate. Negative values indicate invalid mesh.",
        default=0.001,
        min=0.0,
        max=1.0
    )
    
    minFaceWeight: FloatProperty(
        name="Min Face Weight",
        description="Minimum face interpolation weight (0=bad, 1=good). Low values indicate poor quality.",
        default=0.05,
        min=0.0,
        max=1.0
    )
    
    minVolRatio: FloatProperty(
        name="Min Vol Ratio",
        description="Minimum volume ratio between adjacent cells (0=big difference, 1=same size). Low values indicate poor transitions.",
        default=0.01,
        min=0.0,
        max=1.0
    )
    
    minTriangleTwist: FloatProperty(
        name="Min Triangle Twist",
        description="Minimum triangle face twist. 1=no twist, 0=completely folded. Values below 0.05 are problematic.",
        default=0.01,
        min=0.0,
        max=1.0
    )
    
    # Error reduction settings
    nSmoothScale: IntProperty(
        name="Smooth Scale Iterations",
        description="Number of error distribution iterations for mesh smoothing",
        default=4,
        min=0
    )
    
    errorReduction: FloatProperty(
        name="Error Reduction",
        description="Amount of error reduction in each iteration (0=none, 1=complete). Controls relaxation speed.",
        default=0.75,
        min=0.0,
        max=1.0
    )


class RelaxedMeshQualityProperties(PropertyGroup):
    """
    Relaxed mesh quality settings for SnappyHexMesh.
    
    These settings are applied to cells exceeding nRelaxedIter iterations in the meshing process.
    Relaxed parameters allow the mesh generator to succeed when standard constraints
    would be too restrictive, particularly in complex geometry regions.
    """
    
    # Relaxation factor for quick setup
    relaxation_factor: FloatProperty(
        name="Relaxation Factor",
        description="Factor applied to standard settings when copying (>1 for looser constraints, <1 for tighter)",
        default=1.15,
        min=0.5,
        max=2.0
    )
    
    # Standard constraints with consistent use_* prefix for all toggle properties
    use_maxNonOrtho: BoolProperty(
        name="Max Non-Orthogonality",
        description="Enable relaxed non-orthogonality constraint",
        default=True
    )
    
    maxNonOrtho: FloatProperty(
        name="Value",
        description="Relaxed maximum non-orthogonality allowed (0=orthogonal, 90=bad)",
        default=75.0,
        min=0.0,
        max=180.0
    )
    
    use_maxBoundarySkewness: BoolProperty(
        name="Max Boundary Skewness",
        description="Enable relaxed boundary skewness constraint",
        default=False
    )
    
    maxBoundarySkewness: FloatProperty(
        name="Value",
        description="Relaxed maximum boundary face skewness allowed",
        default=30.0,
        min=0.0,
        soft_max=40.0
    )
    
    use_maxInternalSkewness: BoolProperty(
        name="Max Internal Skewness",
        description="Enable relaxed internal skewness constraint",
        default=False
    )
    
    maxInternalSkewness: FloatProperty(
        name="Value",
        description="Relaxed maximum internal face skewness allowed",
        default=8.0,
        min=0.0,
        soft_max=20.0
    )
    
    use_maxConcave: BoolProperty(
        name="Max Concaveness",
        description="Enable relaxed concaveness constraint",
        default=False
    )
    
    maxConcave: FloatProperty(
        name="Value",
        description="Relaxed maximum concaveness allowed in degrees",
        default=90.0,
        min=0.0,
        max=180.0
    )
    
    use_minFlatness: BoolProperty(
        name="Min Flatness",
        description="Enable relaxed flatness constraint",
        default=False
    )
    
    minFlatness: FloatProperty(
        name="Value",
        description="Relaxed minimum face flatness",
        default=0.2,
        min=0.0,
        max=1.0
    )
    
    use_minVol: BoolProperty(
        name="Min Volume",
        description="Enable relaxed volume constraint",
        default=False
    )
    
    minVol: FloatProperty(
        name="Value",
        description="Relaxed minimum normalized cell volume",
        default=1e-14,
        min=0.0
    )
    
    use_minTetQuality: BoolProperty(
        name="Min Tet Quality",
        description="Enable relaxed tetrahedral quality constraint",
        default=False
    )
    
    minTetQuality: FloatProperty(
        name="Value",
        description="Relaxed minimum quality of tetrahedral cells",
        default=1e-40,
        min=0.0
    )
    
    # Advanced constraints
    use_minVolCollapseRatio: BoolProperty(
        name="Min Volume Collapse Ratio",
        description="Enable relaxed volume collapse ratio constraint",
        default=False
    )
    
    minVolCollapseRatio: FloatProperty(
        name="Value",
        description="Relaxed minimum volume ratio for collapsed cells",
        default=0.2,
        min=0.0,
        max=1.0
    )
    
    use_minArea: BoolProperty(
        name="Min Area",
        description="Enable relaxed area constraint",
        default=False
    )
    
    minArea: FloatProperty(
        name="Value",
        description="Relaxed minimum normalized face area",
        default=0.0,
        min=0.0
    )
    
    use_minTwist: BoolProperty(
        name="Min Twist",
        description="Enable relaxed twist constraint",
        default=False
    )
    
    minTwist: FloatProperty(
        name="Value",
        description="Relaxed minimum face twist",
        default=0.01,
        min=0.0,
        max=1.0
    )
    
    use_minDeterminant: BoolProperty(
        name="Min Determinant",
        description="Enable relaxed determinant constraint",
        default=False
    )
    
    minDeterminant: FloatProperty(
        name="Value",
        description="Relaxed minimum normalized cell determinant",
        default=0.0005,
        min=0.0,
        max=1.0
    )
    
    use_minFaceWeight: BoolProperty(
        name="Min Face Weight",
        description="Enable relaxed face weight constraint",
        default=False
    )
    
    minFaceWeight: FloatProperty(
        name="Value",
        description="Relaxed minimum face interpolation weight",
        default=0.01,
        min=0.0,
        max=1.0
    )
    
    use_minVolRatio: BoolProperty(
        name="Min Volume Ratio",
        description="Enable relaxed volume ratio constraint",
        default=False
    )
    
    minVolRatio: FloatProperty(
        name="Value",
        description="Relaxed minimum volume ratio between adjacent cells",
        default=0.001,
        min=0.0,
        max=1.0
    )
    
    use_minTriangleTwist: BoolProperty(
        name="Min Triangle Twist",
        description="Enable relaxed triangle twist constraint",
        default=False
    )
    
    minTriangleTwist: FloatProperty(
        name="Value",
        description="Relaxed minimum triangle face twist",
        default=0.001,
        min=0.0,
        max=1.0
    )


class VNT_OT_select_mesh_quality_dict(Operator, ImportHelper):
    """
    File selector operator for mesh quality dictionary files.
    
    Allows users to browse the filesystem and select an external mesh quality
    dictionary file for inclusion in the snappyHexMeshDict.
    """
    bl_idname = "vnt.select_mesh_quality_dict"
    bl_label = "Select Mesh Quality Dictionary File"
    
    filename_ext = ".dict"
    filter_glob: StringProperty(
        default="*.dict",
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        """Store the selected file path in the mesh quality settings."""
        if self.filepath:
            context.scene.mesh_quality.meshQualityDictPath = self.filepath
        return {'FINISHED'}


class VNT_OT_copy_relaxed_settings(Operator):
    """
    Copy standard mesh quality settings to relaxed settings.
    
    This operator applies the relaxation factor to the standard mesh quality settings
    and populates the relaxed settings fields. It automatically enables constraints
    that differ significantly from the standard values.
    """
    bl_idname = "vnt.copy_relaxed_settings"
    bl_label = "Copy From Standard"
    bl_description = "Copy standard mesh quality settings to relaxed settings with relaxation applied"
    
    def execute(self, context):
        """
        Copy standard settings to relaxed settings with relaxation factor applied.
        
        This method:
        1. Gets the mesh quality settings and relaxation factor
        2. Applies the factor to each setting (multiply for 'max' values, divide for 'min' values)
        3. Enables constraints where the relaxed value differs significantly from standard
        
        Returns:
            dict: Operator result
        """
        mesh_quality = context.scene.mesh_quality
        relaxed = context.scene.relaxed_mesh_quality
        factor = relaxed.relaxation_factor
        
        # For max values, multiply by factor (higher = more permissive)
        relaxed.maxNonOrtho = min(mesh_quality.maxNonOrtho * factor, 180.0)
        relaxed.maxBoundarySkewness = mesh_quality.maxBoundarySkewness * factor
        relaxed.maxInternalSkewness = mesh_quality.maxInternalSkewness * factor
        relaxed.maxConcave = min(mesh_quality.maxConcave * factor, 180.0)
        
        # For min values, divide by factor (lower = more permissive)
        relaxed.minFlatness = max(mesh_quality.minFlatness / factor, 0.0)
        relaxed.minVol = max(mesh_quality.minVol / factor, 0.0)
        relaxed.minTetQuality = max(mesh_quality.minTetQuality / factor, 0.0)
        relaxed.minVolCollapseRatio = max(mesh_quality.minVolCollapseRatio / factor, 0.0)
        relaxed.minArea = max(mesh_quality.minArea / factor, 0.0)
        relaxed.minTwist = max(mesh_quality.minTwist / factor, 0.0) 
        relaxed.minDeterminant = max(mesh_quality.minDeterminant / factor, 0.0)
        relaxed.minFaceWeight = max(mesh_quality.minFaceWeight / factor, 0.0)
        relaxed.minVolRatio = max(mesh_quality.minVolRatio / factor, 0.0)
        relaxed.minTriangleTwist = max(mesh_quality.minTriangleTwist / factor, 0.0)
        
        # Enable constraints if their values are significantly different from standard
        threshold = 0.01
        relaxed.use_maxNonOrtho = abs(relaxed.maxNonOrtho - mesh_quality.maxNonOrtho) > threshold
        relaxed.use_maxBoundarySkewness = abs(relaxed.maxBoundarySkewness - mesh_quality.maxBoundarySkewness) > threshold
        relaxed.use_maxInternalSkewness = abs(relaxed.maxInternalSkewness - mesh_quality.maxInternalSkewness) > threshold
        relaxed.use_maxConcave = abs(relaxed.maxConcave - mesh_quality.maxConcave) > threshold
        relaxed.use_minFlatness = abs(relaxed.minFlatness - mesh_quality.minFlatness) > threshold
        relaxed.use_minVol = abs(relaxed.minVol - mesh_quality.minVol) > threshold * mesh_quality.minVol
        relaxed.use_minTetQuality = abs(relaxed.minTetQuality - mesh_quality.minTetQuality) > threshold * mesh_quality.minTetQuality
        relaxed.use_minVolCollapseRatio = abs(relaxed.minVolCollapseRatio - mesh_quality.minVolCollapseRatio) > threshold
        relaxed.use_minArea = abs(relaxed.minArea - mesh_quality.minArea) > threshold * mesh_quality.minArea if mesh_quality.minArea > 0 else False
        relaxed.use_minTwist = abs(relaxed.minTwist - mesh_quality.minTwist) > threshold
        relaxed.use_minDeterminant = abs(relaxed.minDeterminant - mesh_quality.minDeterminant) > threshold
        relaxed.use_minFaceWeight = abs(relaxed.minFaceWeight - mesh_quality.minFaceWeight) > threshold
        relaxed.use_minVolRatio = abs(relaxed.minVolRatio - mesh_quality.minVolRatio) > threshold
        relaxed.use_minTriangleTwist = abs(relaxed.minTriangleTwist - mesh_quality.minTriangleTwist) > threshold
        
        self.report({'INFO'}, "Copied standard settings to relaxed settings with relaxation factor applied")
        return {'FINISHED'}
