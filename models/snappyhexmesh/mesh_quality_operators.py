import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import (StringProperty, FloatProperty, IntProperty, 
                       BoolProperty, EnumProperty, CollectionProperty, 
                       PointerProperty, FloatVectorProperty)

# Property group for the relaxed mesh quality settings
class RelaxedMeshQualityProperties(PropertyGroup):
    """Relaxed mesh quality properties for snappyHexMesh"""
    
    maxNonOrtho: FloatProperty(
        name="Max Non-Orthogonality",
        description="Maximum non-orthogonality allowed in relaxed mode. Set to 180 to disable",
        default=75.0,
        min=0.0,
        max=180.0
    )

# Property group for mesh quality settings
class MeshQualityProperties(PropertyGroup):
    """Main properties for snappyHexMesh mesh quality controls"""
    
    # Basic mesh quality settings
    includeMeshQualityDict: BoolProperty(
        name="Include Mesh Quality Dict",
        description="Include external mesh quality dictionary file",
        default=True
    )
    
    meshQualityDictPath: StringProperty(
        name="Mesh Quality Dict Path",
        description="Path to external mesh quality dictionary file",
        default="meshQualityDict"
    )
    
    # Relaxed settings are stored in a separate property group
    # (will be implemented via the Scene properties)
    
    # Advanced settings
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
    
    # Basic mesh quality settings (if not using an external file)
    # These will be displayed if includeMeshQualityDict is false
    maxNonOrtho: FloatProperty(
        name="Max Non-Orthogonality",
        description="Maximum non-orthogonality allowed. Set to 180 to disable",
        default=65.0,
        min=0.0,
        max=180.0
    )
    
    maxBoundarySkewness: FloatProperty(
        name="Max Boundary Skewness",
        description="Maximum boundary face skewness allowed",
        default=20.0,
        min=0.0
    )
    
    maxInternalSkewness: FloatProperty(
        name="Max Internal Skewness",
        description="Maximum internal face skewness allowed",
        default=4.0,
        min=0.0
    )
    
    maxConcave: FloatProperty(
        name="Max Concaveness",
        description="Maximum concaveness allowed",
        default=80.0,
        min=0.0,
        max=180.0
    )
    
    minFlatness: FloatProperty(
        name="Min Flatness",
        description="Ratio of minimum projected area to actual area",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    minVol: FloatProperty(
        name="Min Volume",
        description="Minimum cell volume",
        default=1e-13,
        precision=15
    )
    
    minTetQuality: FloatProperty(
        name="Min Tet Quality",
        description="Minimum quality of tetrahedral cells (1=regular, 0=flat)",
        default=1e-30,
        min=0.0,
        max=1.0
    )
    
    minArea: FloatProperty(
        name="Min Area",
        description="Minimum face area",
        default=-1.0
    )
    
    minTwist: FloatProperty(
        name="Min Twist",
        description="Minimum face twist",
        default=0.02,
        min=0.0,
        max=1.0
    )
    
    minDeterminant: FloatProperty(
        name="Min Determinant",
        description="Minimum cell determinant (1=hex, 0=bad)",
        default=0.001,
        min=0.0,
        max=1.0
    )
    
    minFaceWeight: FloatProperty(
        name="Min Face Weight",
        description="Minimum face interpolation weight (0..1)",
        default=0.05,
        min=0.0,
        max=1.0
    )
    
    minVolRatio: FloatProperty(
        name="Min Volume Ratio",
        description="Minimum volume ratio of neighboring cells",
        default=0.01,
        min=0.0,
        max=1.0
    )
    
    minTriangleTwist: FloatProperty(
        name="Min Triangle Twist",
        description="Minimum triangulated face twist",
        default=-1.0,
        min=-1.0,
        max=1.0
    )
    
    nSmoothSurfaceNormals: IntProperty(
        name="Smooth Surface Normals",
        description="Number of smoothing iterations of surface normals",
        default=1,
        min=0
    )
    
    nSmoothNormals: IntProperty(
        name="Smooth Normals",
        description="Number of smoothing iterations of interior mesh movement direction",
        default=3,
        min=0
    )
    
    nSmoothThickness: IntProperty(
        name="Smooth Thickness",
        description="Smooth layer thickness over surface patches",
        default=10,
        min=0
    )
    
    maxNonOrthoAngle: FloatProperty(
        name="Max Non-Ortho Angle",
        description="Max non-orthogonality for layers",
        default=60.0,
        min=0.0,
        max=180.0
    )

# Operator to select a mesh quality dictionary file
class VNT_OT_select_mesh_quality_dict(Operator):
    """Select a mesh quality dictionary file"""
    bl_idname = "vnt.select_mesh_quality_dict"
    bl_label = "Select Mesh Quality Dict"
    
    filepath: StringProperty(subtype="FILE_PATH")
    
    def execute(self, context):
        context.scene.meshQualityDictPath = self.filepath
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
