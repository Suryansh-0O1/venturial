from .models.unstructured_properties import CFMeshProperties, CFMeshPatch, CFMeshBoxRefinement, CFMeshSurfaceRefinement, CFMeshCylinderRefinement

from .views.unstructured_operators.ops_meshing import (
    CFMESH_OT_GenerateCFMesh,
)

from .views.unstructured_operators.ops_geometry import (
    CFMESH_OT_RefreshPatches,
    CFMESH_OT_AddBoxRefinement,
    CFMESH_OT_RemoveBoxRefinement,
    CFMESH_OT_AddSurfaceRefinement,
    CFMESH_OT_RemoveSurfaceRefinement,
    CFMESH_OT_AddCylinderRefinement,
    CFMESH_OT_RemoveCylinderRefinement,
    CFMESH_OT_AddWakePreset,
    CFMESH_OT_AddCylinderWakePreset,
    CFMESH_OT_ImportSTL
)

from .views.unstructured_operators.ops_solver import (
    CFMESH_OT_RunSolver,
)

from .views.unstructured_operators.ops_postprocess import (
    CFMESH_OT_LaunchParaView,
    CFMESH_OT_LoadResult,
    CFMESH_OT_OpenExportDir
)

from .views.unstructured_operators.ops_inspect import (
    CFMESH_OT_SetInspectBBox,
    CFMESH_OT_InspectRegion
)

from .views.unstructured_operators.ops_visualize_slice import (
    CFMESH_OT_VisualizeSlice
)

from .views.unstructured_operators.ops_visualize_boundary import (
    CFMESH_OT_ColorByField
)

from .views.unstructured_operators.ops_analyze import (
    CFMESH_OT_RunCheckMesh,
    CFMESH_OT_ShowResiduals
)

from .views.unstructured_ui import (
    VIEW3D_PT_CFMeshPanel,
    VIEW3D_PT_MeshSettings,
    VIEW3D_PT_SolverSettings,
    VIEW3D_PT_PostProcess
)

classes = (
    # Properties
    CFMeshPatch,
    CFMeshBoxRefinement,
    CFMeshSurfaceRefinement,
    CFMeshCylinderRefinement,
    CFMeshProperties,
    
    # Meshing
    CFMESH_OT_GenerateCFMesh,
    CFMESH_OT_ImportSTL,
    
    # Geometry
    CFMESH_OT_RefreshPatches,
    CFMESH_OT_AddBoxRefinement,
    CFMESH_OT_RemoveBoxRefinement,
    CFMESH_OT_AddSurfaceRefinement,
    CFMESH_OT_RemoveSurfaceRefinement,
    CFMESH_OT_AddCylinderRefinement,
    CFMESH_OT_RemoveCylinderRefinement,
    CFMESH_OT_AddWakePreset,
    CFMESH_OT_AddCylinderWakePreset,
    
    # Inspect
    CFMESH_OT_SetInspectBBox,
    CFMESH_OT_InspectRegion,
    
    # Analyze
    CFMESH_OT_RunCheckMesh,
    CFMESH_OT_ShowResiduals,
    
    # Solver
    CFMESH_OT_RunSolver,
    
    # Post Process
    CFMESH_OT_LaunchParaView,
    CFMESH_OT_LoadResult,
    CFMESH_OT_OpenExportDir,
    
    # Visualize
    CFMESH_OT_VisualizeSlice,
    CFMESH_OT_ColorByField,
    
    # UI Panels
    VIEW3D_PT_CFMeshPanel,
    VIEW3D_PT_MeshSettings,
    VIEW3D_PT_SolverSettings,
    VIEW3D_PT_PostProcess
)

def register_props():
    import bpy
    bpy.types.Scene.cfmesh_props = bpy.props.PointerProperty(type=CFMeshProperties)

def unregister_props():
    import bpy
    del bpy.types.Scene.cfmesh_props
