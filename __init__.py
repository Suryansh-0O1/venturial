bl_info = {
    "name": "Venturial",
    "description": "A GUI to alleviate the effort of constructing OpenFOAM cases.",
    "author": "Rajdeep Adak at FOSSEE, IIT Bombay",
    "contributors": "visit www.github.com/venturial/contributors",
    "version": (0, 1, 0),
    "blender": (3, 2, 1),
    "location": "View3D > Side bar > Venturial",
    "category": "Development",
}

import bpy, bmesh, os
import bpy.utils.previews

from bpy.utils import register_class, unregister_class

from bpy.props import (
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    BoolProperty,
    StringProperty,
    PointerProperty,
    CollectionProperty,
    EnumProperty,
)

from bpy.types import Operator, Panel, AddonPreferences, PropertyGroup, UIList


from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d

from venturial.startup.get_tutorials_list import add_tutorials_to_scene
from venturial.startup.get_recents_list import add_recents_to_scene

from venturial.models.header.file_handling_operators import *
from venturial.models.header.developer_menu_operators import *
from venturial.models.header.general_operators import *
from venturial.models.header.help_menu_operators import *

from venturial.models.mainpanel_sublayout_operators import *
from venturial.models.blockmesh.design_operators import *
from venturial.models.visualizer_operators import (
    VNT_OT_vertex_data_control,
    VNT_OT_edge_data_control,
    VNT_OT_boundary_data_control,
)
# from venturial.models.blockmesh.edge_operators import *
from venturial.models.tutorials_menu_operators import *

# from venturial.models.geometry_designer_operators import *
# from venturial.models.mesh_file_manager_operators import *
from venturial.models.blockmesh.get_vertices_operators import *
from venturial.models.blockmesh.boundary_control_operators import *
from venturial.models.run_panel_operators import *

from venturial.views.schemas.UIList_schemas import *
from venturial.views.user_mode_view import VNT_PT_usermodeview
from venturial.views.header.view import *
from venturial.views.mainpanel.meshing_tools.blockmesh import VNT_PT_cell_location
from venturial.views.mainpanel.meshing_tools.snappyhexmesh import (
    VNT_OT_create_new_geometry,
    VNT_OT_delete_geometry,
    VNT_OT_export_stl_geometry,
    VNT_OT_generate_snappyhex_dict, 
)
from venturial.views.mainpanel.view import (
    VNT_OT_active_project_indicator,
    VNT_OT_list_category,
    get_mainpanel_categories,
)
from venturial.views.mainpanel.tutorials import VNT_PT_filter_tutorials
from venturial.views.mainpanel.recents import VNT_PT_filter_recents
from venturial.views.mainpanel.visualizer import VNT_PT_statistics_settings

from venturial.utils.custom_icon_object_generator import (
    register_custom_icon,
    unregister_custom_icon,
)

from venturial.lib.update_methods import *
from venturial.lib.preferences_properties import VNT_user_preferences_collection
from venturial.lib.global_properties import VNT_global_properties_collection, VNT_global_properties_collection_edge_verts, CUSTOM_LocProps

from venturial.models.edges_panel_operators import *

# Import castellated mesh classes directly
from venturial.models.snappyhexmesh.castellated_operators import (
    CastellatedFeature,
    RefinementRegion,
    PatchInfo,
    RefinementSurfaceRegion,
    RefinementSurface,
    VNT_OT_add_feature,
    VNT_OT_browse_feature_file,
    VNT_OT_remove_feature,
    VNT_OT_add_refinement_surface, 
    VNT_OT_browse_surface_file,
    VNT_OT_remove_refinement_surface,
    VNT_OT_add_surface_region,
    VNT_OT_remove_surface_region,
    VNT_OT_add_refinement_region,
    VNT_OT_remove_refinement_region,
    CAST_UL_features_list,
    CAST_UL_refinement_surfaces,
    CAST_UL_refinement_regions,
    DistanceLevelPair,
    VNT_OT_add_distance_level_pair,
    VNT_OT_remove_distance_level_pair,
    CAST_UL_distance_level_pairs,
    VNT_OT_add_feature_distance_level_pair,
    VNT_OT_remove_feature_distance_level_pair,
    CAST_UL_feature_distance_level_pairs,
    CAST_UL_surface_regions
)

from venturial.models.snappyhexmesh.snap_operators import (
    SnapControlsProperties,
    VNT_OT_select_unselect_allsnap
)

from venturial.models.snappyhexmesh.layer_operators import (
    LayerAdditionProperties, 
    LayerPatchSettings,
    VNT_OT_add_layer_patch,
    VNT_OT_remove_layer_patch,
    VNT_OT_duplicate_layer_patch,
    VNT_OT_import_boundary_patches,
    LAYER_UL_patches_list,
    VNT_OT_configure_layer_settings
)
from venturial.models.snappyhexmesh.mesh_quality_operators import (
    MeshQualityProperties,
    RelaxedMeshQualityProperties,
    VNT_OT_select_mesh_quality_dict
)

from venturial.models.snappyhexmesh.geometry_operators import geometry_index_update
from venturial.models.snappyhexmesh.tooltip_updater import register as register_tooltips

classes = (
    VNT_user_preferences_collection,
    VNT_OT_save_preferences,
    VNT_OT_reset_preferences,
    VNT_OT_import_preferences,
    VNT_OT_new_case,
    VNT_OT_select_mesh_filepath,
    VNT_OT_build_mesh,
    VNT_OT_import_mesh,
    VNT_OT_open_case,
    VNT_OT_delete_mesh_file_items,
    VNT_OT_deactivate_mesh_file_item,
    VNT_OT_stl_browse,
    VNT_OT_import_stl_geometry,
    VNT_OT_export_stl_geometry,
    VNT_OT_dev_mode,
    VNT_OT_dev_tools,
    VNT_OT_user_general_settings,
    VNT_OT_select_default_mesh_filepath,
    VNT_OT_select_default_tut_filepath,
    VNT_OT_select_default_user_data_filepath,
    VNT_OT_list_category,
    VNT_OT_venturial_maintools,
    VNT_OT_venturial_homepage,
    VNT_OT_fossee_homepage,
    VNT_OT_close_venturial,
    VNT_OT_user_guide,
    VNT_OT_developer_guide,
    VNT_OT_feature_request,
    VNT_OT_report_bugs,
    VNT_OT_developer_support,
    VNT_OT_user_community,
    VNT_OT_developer_community,
    VNT_OT_release_notes,
    VNT_PT_usermodeview,
    VNT_OT_mainpanel_layout,
    VNT_OT_delete_geometry,
    fileitemproperties,
    recent_item_properties,
    tutorialitemproperties,
    VNT_MT_dev_menu,
    VNT_MT_file_menu,
    VNT_PT_uicategory,
    VNT_MT_about_venturial,
    VNT_MT_about_fossee,
    VNT_MT_help_menu,
    CUSTOM_LocProps,
    VNT_global_properties_collection_edge_verts,
    VNT_global_properties_collection,
    VNT_UL_mesh_file_manager,
    VNT_UL_mesh_file_coroner,
    CUSTOM_UL_verts,
    CUSTOM_UL_blocks,
    CUSTOM_UL_faces,
    CUSTOM_UL_edges_Main,
    CUSTOM_UL_edges_Sub,
    CUSTOM_UL_face_merge,
    VNT_OT_faceactions,
    VNT_OT_set_face_name,
    VNT_OT_set_type_face,
    VNT_PT_cell_location,
    VNT_OT_selectfaces,
    VNT_OT_clearfaces,
    VNT_OT_fill_dict_file,
    VNT_OT_cleardictfileonly,
    VNT_OT_New_Boundary,
    VNT_OT_vertactions,
    VNT_OT_add_update_verts,
    VNT_OT_select_unselect_allverts,
    VNT_OT_clearverts,
    VNT_PT_statistics_settings,
    VNT_OT_location_spawnner,
    VNT_OT_add_to_viewport,
    VNT_OT_compose,
    VNT_OT_get_blocks,
    VNT_OT_remove_blocks,
    VNT_OT_remove_all_blocks,
    VNT_OT_clearblocks,
    VNT_OT_blocksdatacontrol,
    VNT_OT_showselectedblocks,
    VNT_OT_select_unselect_allblocks,
    VNT_OT_vertex_data_control,
    VNT_OT_edge_data_control,
    VNT_OT_boundary_data_control,
    VNT_OT_merge_faces,
    VNT_OT_merge_faces_delete,
    # VNT_OT_generate_edge,
    # VNT_OT_edit_edge, 
    # VNT_OT_destroy_edge,
    VNT_OT_more_tutorials_viewer,
    VNT_OT_tutorial_viewer,
    VNT_PT_filter_tutorials,
    VNT_PT_filter_recents,
    VNT_OT_active_project_indicator,
    OBJECT_OT_add_single_vertex,
    VNT_OT_new_edge,
    VNT_OT_new_vert,
    VNT_OT_remove_edge,
    VNT_OT_remove_vert,
    VNT_OT_create_new_geometry,
    # Add castellated mesh classes
    CastellatedFeature,
    RefinementRegion,
    PatchInfo,
    RefinementSurfaceRegion,
    RefinementSurface,
    VNT_OT_add_feature,
    VNT_OT_browse_feature_file,
    VNT_OT_remove_feature,
    VNT_OT_add_refinement_surface,
    VNT_OT_browse_surface_file,
    VNT_OT_remove_refinement_surface,
    VNT_OT_add_surface_region,
    VNT_OT_remove_surface_region,
    VNT_OT_add_refinement_region,
    VNT_OT_remove_refinement_region,
    CAST_UL_features_list,
    CAST_UL_refinement_surfaces,
    CAST_UL_refinement_regions,
    DistanceLevelPair,
    VNT_OT_add_distance_level_pair,
    VNT_OT_remove_distance_level_pair,
    CAST_UL_distance_level_pairs,
    VNT_OT_add_feature_distance_level_pair,
    VNT_OT_remove_feature_distance_level_pair,
    CAST_UL_feature_distance_level_pairs,
    CAST_UL_surface_regions,
    
    SnapControlsProperties,
    VNT_OT_select_unselect_allsnap,
    LayerAdditionProperties,
    LayerPatchSettings,
    VNT_OT_add_layer_patch,
    VNT_OT_remove_layer_patch,
    VNT_OT_duplicate_layer_patch,
    VNT_OT_import_boundary_patches,
    VNT_OT_configure_layer_settings,
    LAYER_UL_patches_list,
    MeshQualityProperties,
    RelaxedMeshQualityProperties,
    VNT_OT_select_mesh_quality_dict,
    VNT_OT_generate_snappyhex_dict,
)

def register():

    register_custom_icon(
        "venturial_logo", "/venturial/icons/custom_icons/venturial_logo.png"
    )
    register_custom_icon("fossee_logo", "/venturial/icons/custom_icons/fossee_logo.png")
    register_custom_icon(
        "new_mesh_file_2", "/venturial/icons/custom_icons/new_mesh_file_2.png"
    )
    register_custom_icon(
        "build_mesh_2", "/venturial/icons/custom_icons/build_mesh_2.png"
    )
    register_custom_icon(
        "warning_sign_1", "/venturial/icons/custom_icons/warning_sign_1.png"
    )
    register_custom_icon(
        "file-browser-2", "/venturial/icons/custom_icons/file-browser-2.png"
    )

    for cls in classes:
        register_class(cls)

    # Fix: Access RefinementRegion directly instead of through bpy.types
    from venturial.models.snappyhexmesh.castellated_operators import (
        RefinementRegion,
        CastellatedFeature,
        DistanceLevelPair
    )
    
    # feature-level pairs
    CastellatedFeature.distance_level_pairs = CollectionProperty(
        type=DistanceLevelPair,
        name="Distance-Level Pairs"
    )
    CastellatedFeature.distance_level_pairs_index = IntProperty(default=0)

    # region-level pairs (already present)
    RefinementRegion.distance_level_pairs = CollectionProperty(
        type=DistanceLevelPair,
        name="Distance-Level Pairs"
    )
    RefinementRegion.distance_level_pairs_index = IntProperty(default=0)
    
    # Global gap level increment property
    bpy.types.Scene.use_gap_level = BoolProperty(
        name="Use Gap Level Increment",
        description="Use gap level increment for small gaps between surfaces",
        default=False
    )
    
    bpy.types.Scene.gap_level_increment = IntProperty(
        name="Gap Level Increment",
        description="Additional refinement level for cells in narrow gaps",
        default=2,
        min=0,
        max=10
    )
    
    # Additional castellated mesh properties for the new UI sections
    
    # Feature angle properties
    bpy.types.Scene.resolveFeatureAngle = FloatProperty(
        name="Resolve Feature Angle",
        description="Angle for feature resolution",
        default=30.0,
        min=0.0,
        max=180.0
    )
    
    bpy.types.Scene.planarAngle = FloatProperty(
        name="Planar Angle",
        description="Angle for determining planar features",
        default=30.0,
        min=0.0,
        max=180.0
    )
    
    # Refinement region properties for RefinementRegion class
    RefinementRegion.name = StringProperty(
        name="Name",
        description="Name of the refinement region",
        default="box"
    )
    
    RefinementRegion.source_type = EnumProperty(
        name="Source Type",
        description="Type of geometry source",
        items=[
            ('geometry', "Geometry Object", "Use a geometry object from the scene"),
            ('stl', "STL File", "Use an STL file")
        ],
        default='geometry'
    )
    
    RefinementRegion.geometry_object = StringProperty(
        name="Geometry Object",
        description="Name of the geometry object to use"
    )
    
    RefinementRegion.mode = EnumProperty(
        name="Mode",
        description="Refinement mode",
        items=[
            ('inside', "Inside", "Refine cells inside the region"),
            ('distance', "Distance", "Refine cells within specified distance of the region")
        ],
        default='inside'
    )
    
    RefinementRegion.level = IntProperty(
        name="Level",
        description="Refinement level for inside mode",
        default=1,
        min=0
    )
    
    RefinementRegion.use_advanced_distance = BoolProperty(
        name="Multiple Distance Levels",
        description="Use multiple distance-level pairs for more complex refinement",
        default=False
    )
    
    RefinementRegion.distance = FloatProperty(
        name="Distance",
        description="Distance from surface for refinement",
        default=1.0,
        min=0.0
    )
    
    RefinementRegion.level_at_distance = IntProperty(
        name="Level",
        description="Refinement level at the specified distance",
        default=1,
        min=0
    )
    
    # Location in mesh coordinates
    bpy.types.Scene.locationInMeshX = FloatProperty(
        name="X",
        description="X coordinate of location in mesh point",
        default=-100.0
    )
    
    bpy.types.Scene.locationInMeshY = FloatProperty(
        name="Y",
        description="Y coordinate of location in mesh point",
        default=0.0
    )
    
    bpy.types.Scene.locationInMeshZ = FloatProperty(
        name="Z",
        description="Z coordinate of location in mesh point",
        default=50.0
    )
    
    bpy.types.Scene.allowFreeStandingZoneFaces = BoolProperty(
        name="Allow Free Standing Zone Faces",
        description="Allow free-standing zone faces",
        default=True
    )
    
    # Advanced options
    bpy.types.Scene.handleSnapProblems = BoolProperty(
        name="Handle Snap Problems",
        description="Do not remove cells likely to give snapping problems",
        default=False
    )
    
    bpy.types.Scene.useTopologicalSnapDetection = BoolProperty(
        name="Use Topological Snap Detection",
        description="Use topological test for cells to-be-squashed (disable to use geometric test)",
        default=True
    )
    
    # Collection to store refinement regions
    bpy.types.Scene.cast_refinement_regions = CollectionProperty(
        type=RefinementRegion,
        name="Refinement Regions"
    )
    
    bpy.types.Scene.cast_refinement_regions_index = IntProperty(default=0)
    
    # Add this in the register function after the other layer-related properties
    bpy.types.Scene.show_layer_advanced = BoolProperty(
        name="Show Advanced Layer Settings",
        default=False
    )
    
    bpy.types.Scene.layer_strategy = EnumProperty(
        name="Layer Strategy",
        description="Strategy for layer addition",
        items=[
            ('standard', "Standard", "Standard layer addition approach"),
            ('conservative', "Conservative", "More cautious approach for complex geometry"),
            ('aggressive', "Aggressive", "Try harder to add layers even in complex areas")
        ],
        default='standard'
    )
    
    # After other layer addition properties
    bpy.types.Scene.detectExtrusionIsland = BoolProperty(
        name="Detect Extrusion Islands",
        description="Detect and extrude islands of cells for better layer coverage",
        default=True
    )
    
    # The rest of register function continues...
    bpy.types.Scene.stl_file = StringProperty(name="STL File", default="")
    bpy.types.Scene.stl_file_name = StringProperty(name="STL File Name", default="")
    bpy.types.Scene.search_tuts = StringProperty(default="Search Tutorials")
    bpy.types.Scene.search_recents = StringProperty(default="Search Recents")
    bpy.types.Scene.edit_dict_name = BoolProperty(default=True)

    bpy.types.Scene.current_tool_text = StringProperty(default="BlockMesh")
    bpy.types.Scene.meshing_tool = EnumProperty(
        items=[("BlockMesh", "BlockMesh", ""), ("SnappyHexMesh", "SnappyHexMesh", "")],
        default="BlockMesh",
        update=update_current_tool_text_1,
    )

    bpy.types.Scene.solution_tools = EnumProperty(
        items=[
            ("Solution Modeling", "Solution Modeling", ""),
            ("Post-Processing", "Post-Processing", ""),
        ],
        update=update_current_tool_text_2,
    )

    bpy.types.Scene.spawn_type = EnumProperty(
        items=[
            ("Grid", "Grid", ""),
            ("3D Cursor", "3D Cursor", ""),
            ("Center", "Center", ""),
        ],
        default="Grid",
    )

    bpy.types.Scene.prompt_meshing_tool = EnumProperty(
        default={"BlockMesh"},
        items=[("BlockMesh", "BlockMesh", ""), ("SnappyHexMesh", "SnappyHexMesh", "")],
        options={"ENUM_FLAG"},
        update=update_mesh_dict_names,
    )

    bpy.types.Scene.mainpanel_categories = EnumProperty(
        items=get_mainpanel_categories,
        default=0
    )

    bpy.types.Scene.cellShapes = EnumProperty(
        items=[
            ("Hexahedron", "Hexahedron", ""),
            ("Wedge (Experimental)", "Wedge (Experimental)", ""),
            ("Prism", "Prism", ""),
            ("Pyramid (Experimental)", "Pyramid (Experimental)", ""),
            ("Tetrahedron (Experimental)", "Tetrahedron (Experimental)", ""),
            (
                "Tetrahedral wedge (Experimental)",
                "Tetrahedral wedge (Experimental)",
                "",
            ),
        ],
        default="Hexahedron",
        description="Cell Shape Types",
    )

    bpy.types.Scene.cellShape_units = IntProperty(min=1, max=50, default=1)

    bpy.types.Scene.bm_dict_name = StringProperty(default="blockMeshDict")
    bpy.types.Scene.shm_dict_name = StringProperty()

    bpy.types.Scene.pref_pointer = bpy.props.PointerProperty(
        type=VNT_user_preferences_collection
    )

    bpy.types.Scene.mfile_item_ptr = bpy.props.PointerProperty(type=fileitemproperties)
    bpy.types.Scene.mfile_item = CollectionProperty(type=fileitemproperties)
    bpy.types.Scene.mfile_item_index = IntProperty(update=update_uicategory_mode)

    bpy.types.Scene.tut_item_ptr = bpy.props.PointerProperty(
        type=tutorialitemproperties
    )
    bpy.types.Scene.tut_item = CollectionProperty(type=tutorialitemproperties)
    bpy.types.Scene.tut_item_index = IntProperty()

    bpy.types.Scene.rec_item_ptr = bpy.props.PointerProperty(
        type=recent_item_properties
    )
    bpy.types.Scene.rec_item = CollectionProperty(type=recent_item_properties)
    bpy.types.Scene.rec_item_index = IntProperty()

    bpy.types.Scene.mesh_dict_path = StringProperty()
    bpy.types.Scene.row_en = BoolProperty(default=True)

    bpy.types.Scene.cell_x = IntProperty(
        name="X: ",
        description="Select Number of cells along X",
        min=1,
        max=1000,
        default=1,
        update=update_cellxyz,
    )

    bpy.types.Scene.cell_y = IntProperty(
        name="Y: ",
        description="Select Number of cells along Y",
        min=1,
        max=1000,
        default=1,
        update=update_cellxyz,
    )

    bpy.types.Scene.cell_z = IntProperty(
        name="Z: ",
        description="Select Number of cells along Z",
        min=1,
        max=1000,
        default=1,
        update=update_cellxyz,
    )

    bpy.types.Scene.ctm = FloatProperty(
        name="Convert To Meters:",
        description="Set converttoMeters parameter of Blockmeshdict",
        min=0.001,
        max=100.0,
        default=0.1,
    )

    bpy.types.Scene.transform = BoolProperty(default=False)

    bpy.types.Scene.transformation_methods = EnumProperty(
        items=[
            ("Move", "Move (G)", "Shortcut: G"),
            ("Rotate", "Rotate (R)", "Shortcut: R"),
            ("Scale", "Scale (S)", "Shortcut: S"),
        ],
        default="Move",
    )

    bpy.types.Scene.snapping = BoolProperty(default=False, update=update_snapping)

    bpy.types.Scene.snapping_methods = EnumProperty(
        items=[("VERTEX", "Vertex", ""), ("EDGE", "Edge", ""), ("FACE", "Face", "")],
        default="VERTEX",
        update=update_snapping_method,
    )

    bpy.types.Scene.simblk = CollectionProperty(type=VNT_global_properties_collection)
    bpy.types.Scene.simblk_index = IntProperty()

    bpy.types.Scene.bcustom = CollectionProperty(type=VNT_global_properties_collection) # for blocks
    bpy.types.Scene.bcustom_index = IntProperty()

    bpy.types.Scene.vcustom = CollectionProperty(type=VNT_global_properties_collection) # for vertices
    bpy.types.Scene.vcustom_index = IntProperty()

    bpy.types.Scene.fcustom = CollectionProperty(type=VNT_global_properties_collection) # for faces
    bpy.types.Scene.fcustom_index = IntProperty()

    bpy.types.Scene.faceList_master = EnumProperty("Face List", items=list_current_faces)
    bpy.types.Scene.faceList_slave = EnumProperty("Face List", items=list_current_faces)

    bpy.types.Scene.fmcustom = CollectionProperty(type=VNT_global_properties_collection) # for face merging
    bpy.types.Scene.fmcustom_index = IntProperty()

    bpy.types.Scene.ecustom = CollectionProperty(type=VNT_global_properties_collection_edge_verts) # for edges
    bpy.types.Scene.ecustom_index = IntProperty()

    bpy.types.Scene.vert_index = IntProperty(name="Vertex Index", default=0)

    bpy.types.Scene.edge_control_methods = EnumProperty(
        items=[("IP", "Interpolation Points", ""), ("AA", "Axis angle", "")],
        default="IP",
    )

    bpy.types.Scene.curve_type = EnumProperty(
        items=[
            ("ARC", "Arc", "Arc type of edge"),
            ("PLY", "Polyline", "Polyline type of edge"),
            ("SPL", "Spline", "Spline type of edge"),
            ("BSPL", "BSpline", "BSpline type of edge"),
        ],
        default="ARC",
    )

    bpy.types.Scene.cnt = IntProperty()

    bpy.types.Scene.mode = EnumProperty(
        items=[
            ("OBJECT", "Object Mode", "", "OBJECT_DATAMODE", 1),
            ("VERT", "Vertex Mode", "", "VERTEXSEL", 2),
            ("FACE", "Face Mode", "", "FACESEL", 3),
            ("EDGE", "Edge Mode", "", "EDGESEL", 4),
        ],
        default="OBJECT",
        update=update_mode,
    )

    bpy.types.Scene.bdclist = EnumProperty(
        name="",
        description="Select Boundary Condition",
        items=[
            ("wedge", "wedge", ""),
            ("empty", "empty", ""),
            ("symmetryPlane", "symmetryPlane", ""),
            ("wall", "wall", ""),
            ("patch", "patch", ""),
        ],
    )

    bpy.types.Scene.face_name = PointerProperty(type=VNT_global_properties_collection)
    bpy.types.Scene.facedes = PointerProperty(type=VNT_global_properties_collection)

    bpy.types.Scene.acustom = CollectionProperty(type=VNT_global_properties_collection)
    bpy.types.Scene.acustom_index = IntProperty()

    bpy.types.Scene.pcustom = CollectionProperty(type=VNT_global_properties_collection)
    bpy.types.Scene.pcustom_index = IntProperty()

    bpy.types.Scene.scustom = CollectionProperty(type=VNT_global_properties_collection)
    bpy.types.Scene.scustom_index = IntProperty()

    bpy.types.Scene.bscustom = CollectionProperty(type=VNT_global_properties_collection)
    bpy.types.Scene.bscustom_index = IntProperty()

    bpy.types.Scene.ipcnt = IntProperty(
        name="IP: ",
        description="Select Number of Interpolation Points",
        min=1,
        max=30,
        default=1,
    )

    bpy.types.Scene.face_sel_mode = BoolProperty(default=False, update=update_face_mode)

    bpy.types.Scene.statistics = BoolProperty(default=False)

    bpy.types.Scene.bfc = BoolProperty(default=False, description="Backface Culling")

    bpy.types.Scene.xray = BoolProperty(default=False, description="X ray mode")

    bpy.types.Scene.xray_opacity = FloatProperty(
        name="X-ray opacity", description="X-ray opacity", min=0.0, max=1.0, default=0.5
    )

    bpy.types.Scene.geo_params = EnumProperty(
        description="Geometry parameters",
        items=[
            ("Center", "Center", ""),
            ("Orientation", "Orientation", ""),
            ("Outline", "Outline", ""),
        ],
        default={"Center", "Orientation", "Outline"},
        options={"ENUM_FLAG"},
    )

    bpy.types.Scene.outline_color = FloatVectorProperty(
        name="Outline Color",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.0, 0.5, 0.0, 1.0),
    )

    bpy.types.Scene.shading = EnumProperty(
        description="Geometry Shading",
        items=[("Solid", "Solid", ""), ("Wire", "Wire", "")],
    )

    bpy.types.Scene.wire_opacity = FloatProperty(
        name="Wire opacity", description="Wire opacity", min=0.0, max=1.0, default=0.5
    )

    bpy.types.Scene.enable_vert_vis = BoolProperty(name="")
    bpy.types.Scene.enable_edge_vis = BoolProperty(name="")
    bpy.types.Scene.enable_bound_vis = BoolProperty(name="")

    bpy.types.Scene.vert_order = BoolProperty(name="")

    bpy.types.Scene.vert_props = EnumProperty(
        description="Vertex visualization properties",
        items=[("Indices", "Indices", ""), ("Coordinates", "Coordinates", "")],
        default={"Indices"},
        options={"ENUM_FLAG"},
    )

    bpy.types.Scene.vert_source = EnumProperty(
        description="Vertex visualization properties",
        items=[("Geometry", "Geometry", ""), ("blockmeshdict", "blockmeshdict", "")],
        default="Geometry",
    )

    bpy.types.Scene.vert_text_size = IntProperty(
        name="Text Size:",
        description="Select Size of Vertex Info Text being Displayed",
        min=6,
        max=100,
        default=40,
    )

    bpy.types.Scene.vert_text_color = FloatVectorProperty(
        name="Text Color",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.0, 0.0, 1.0, 1.0),
    )

    bpy.types.Scene.active_projects = EnumProperty(
        description="horizontally placed dynamic list of active projects in the project manager.",
        items=get_active_projects,
    )

    bpy.types.Scene.geometry_items = CollectionProperty(type=fileitemproperties)  # Reusing existing class
    bpy.types.Scene.geometry_items_index = IntProperty(
        name="Geometry Items Index",
        default=0,
        update=geometry_index_update
    )

    bpy.types.Scene.castellatedMesh = BoolProperty(name="Castellated Mesh", default=False)
    bpy.types.Scene.snap = BoolProperty(name="Snap", default=False)
    bpy.types.Scene.addLayers = BoolProperty(name="Add Layers", default=False)

    bpy.types.Scene.maxLocalCells = IntProperty(
        name="Max Local Cells",
        description="Maximum local cells for castellated mesh",
        default=100000,
        min=1000
    )
    
    bpy.types.Scene.maxGlobalCells = IntProperty(
        name="Max Global Cells",
        description="Maximum global cells for castellated mesh",
        default=2000000,
        min=1000
    )
    
    bpy.types.Scene.minRefinementCells = IntProperty(
        name="Min Refinement Cells",
        description="Minimum cells to refine",
        default=0,
        min=0
    )
        
    bpy.types.Scene.maxLoadUnbalance = FloatProperty(
        name="Max Load Unbalance",
        description="Maximum load unbalance factor",
        default=0.1,
        min=0.0,
        max=1.0
    )
    
    bpy.types.Scene.nCellsBetweenLevels = IntProperty(
        name="Cells Between Levels",
        description="Number of buffer cells between refinement levels",
        default=2,  # Changed from 1 to 2
        min=1
    )
    
    bpy.types.Scene.resolveFeatureAngle = FloatProperty(
        name="Resolve Feature Angle",
        description="Angle for feature resolution",
        default=30.0,
        min=0.0,
        max=180.0
    )
    
    bpy.types.Scene.planarAngle = FloatProperty(
        name="Planar Angle",
        description="Angle for determining planar features",
        default=30.0,
        min=0.0,
        max=180.0
    )
    
    bpy.types.Scene.locationInMeshX = FloatProperty(
        name="X",
        description="X coordinate of location in mesh point",
        default=5.0
    )
    
    bpy.types.Scene.locationInMeshY = FloatProperty(
        name="Y",
        description="Y coordinate of location in mesh point",
        default=0.28
    )
    
    bpy.types.Scene.locationInMeshZ = FloatProperty(
        name="Z",
        description="Z coordinate of location in mesh point",
        default=0.43
    )
    
    bpy.types.Scene.allowFreeStandingZoneFaces = BoolProperty(
        name="Allow Free Standing Zone Faces",
        description="Allow free-standing zone faces",
        default=True
    )
    
    bpy.types.Scene.cast_features = CollectionProperty(
        type=CastellatedFeature,
        name="Features"
    )
    
    bpy.types.Scene.cast_features_index = IntProperty(default=0)
    
    bpy.types.Scene.cast_refinement_surfaces = CollectionProperty(
        type=RefinementSurface,
        name="Refinement Surfaces"
    )
    
    bpy.types.Scene.cast_refinement_surfaces_index = IntProperty(default=0)
    
    bpy.types.Scene.cast_refinement_regions = CollectionProperty(
        type=RefinementRegion,
        name="Refinement Regions"
    )
    
    bpy.types.Scene.cast_refinement_regions_index = IntProperty(default=0)
    
    bpy.types.Scene.nSmoothPatch = IntProperty(
        name="Smooth Patch Iterations",
        description="Number of patch smoothing iterations before finding correspondence to surface",
        default=3,
        min=0
    )
    
    bpy.types.Scene.tolerance = FloatProperty(
        name="Tolerance",
        description="Maximum relative distance for points to be attracted by surface",
        default=2.0,
        min=0.0
    )
    
    bpy.types.Scene.nSolveIter = IntProperty(
        name="Solve Iterations",
        description="Number of mesh displacement relaxation iterations",
        default=30,
        min=0
    )
    
    bpy.types.Scene.nRelaxIter = IntProperty(
        name="Relax Iterations",
        description="Maximum number of snapping relaxation iterations",
        default=5,
        min=0
    )
    
    bpy.types.Scene.useFeatureSnap = BoolProperty(
        name="Use Feature Snapping",
        description="Enable feature edge snapping",
        default=True
    )
    
    bpy.types.Scene.nFeatureSnapIter = IntProperty(
        name="Feature Snap Iterations",
        description="Number of feature edge snapping iterations",
        default=10,
        min=0
    )
    
    bpy.types.Scene.implicitFeatureSnap = BoolProperty(
        name="Implicit Feature Snap",
        description="Detect features by sampling the surface",
        default=False
    )
    
    bpy.types.Scene.explicitFeatureSnap = BoolProperty(
        name="Explicit Feature Snap",
        description="Use castellatedMeshControls features",
        default=True
    )
    
    bpy.types.Scene.multiRegionFeatureSnap = BoolProperty(
        name="Multi-region Feature Snap",
        description="Detect features between multiple surfaces",
        default=False
    )
    
    # Layer addition properties
    bpy.types.Scene.relativeSizes = BoolProperty(
        name="Relative Sizes",
        description="Are thickness parameters relative to cell size or absolute",
        default=True
    )
    
    bpy.types.Scene.thickness_mode = EnumProperty(
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
    
    bpy.types.Scene.expansionRatio = FloatProperty(
        name="Expansion Ratio",
        description="Expansion factor for layer mesh",
        default=1.0,
        min=1.0,
        max=10.0
    )
    
    bpy.types.Scene.finalLayerThickness = FloatProperty(
        name="Final Layer Thickness",
        description="Thickness of layer furthest from wall",
        default=0.3,
        min=0.001
    )
    
    bpy.types.Scene.firstLayerThickness = FloatProperty(
        name="First Layer Thickness",
        description="Thickness of layer next to wall",
        default=0.3,
        min=0.001
    )
    
    bpy.types.Scene.overallThickness = FloatProperty(
        name="Overall Thickness",
        description="Total thickness of all layers",
        default=0.5,
        min=0.001
    )
    
    bpy.types.Scene.minThickness = FloatProperty(
        name="Minimum Thickness",
        description="Minimum thickness of total layers",
        default=0.25,
        min=0.0
    )
    
    bpy.types.Scene.featureAngle = FloatProperty(
        name="Feature Angle",
        description="Angle at which to not extrude surface",
        default=130.0,
        min=0.0,
        max=180.0
    )
    
    bpy.types.Scene.nGrow = IntProperty(
        name="Grow Layers",
        description="Number of layers of connected faces to grow",
        default=0,
        min=0
    )
    
    bpy.types.Scene.maxFaceThicknessRatio = FloatProperty(
        name="Max Face Thickness Ratio",
        description="Stop layer growth on highly warped cells",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    bpy.types.Scene.nSmoothSurfaceNormals = IntProperty(
        name="Smooth Surface Normals",
        description="Smoothing iterations for surface normals",
        default=1,
        min=0
    )
    
    bpy.types.Scene.nSmoothThickness = IntProperty(
        name="Smooth Thickness",
        description="Iterations to smooth layer thickness",
        default=10,
        min=0
    )
    
    bpy.types.Scene.minMedialAxisAngle = FloatProperty(
        name="Min Medial Axis Angle",
        description="Angle used to pick up medial axis points",
        default=90.0,
        min=0.0,
        max=180.0
    )
    
    bpy.types.Scene.maxThicknessToMedialRatio = FloatProperty(
        name="Max Thickness to Medial Ratio",
        description="Reduce growth where thickness to medial distance is large",
        default=0.3,
        min=0.0,
        max=1.0
    )
    
    bpy.types.Scene.nSmoothNormals = IntProperty(
        name="Smooth Normals",
        description="Smoothing iterations for mesh movement direction",
        default=3,
        min=0
    )
    
    bpy.types.Scene.slipFeatureAngle = FloatProperty(
        name="Slip Feature Angle",
        description="Angle above which mesh can slip at non-patched sides",
        default=30.0,
        min=0.0,
        max=180.0
    )
    
    bpy.types.Scene.layerRelaxIter = IntProperty(
        name="Layer Relax Iterations",
        description="Maximum snapping relaxation iterations",
        default=5,
        min=0
    )
    
    bpy.types.Scene.nBufferCellsNoExtrude = IntProperty(
        name="Buffer Cells No Extrude",
        description="Buffer region for new layer terminations",
        default=0,
        min=0
    )
    
    bpy.types.Scene.nLayerIter = IntProperty(
        name="Layer Iterations",
        description="Max number of layer addition iterations",
        default=50,
        min=1
    )
    
    bpy.types.Scene.nRelaxedIter = IntProperty(
        name="Relaxed Iterations",
        description="Iterations after which relaxed mesh quality controls are used",
        default=20,
        min=0
    )
    
    bpy.types.Scene.additionalReporting = BoolProperty(
        name="Additional Reporting",
        description="Report problematic face centers",
        default=False
    )
    
    bpy.types.Scene.layer_patches = CollectionProperty(
        type=LayerPatchSettings,
        name="Layer Patches"
    )
    
    bpy.types.Scene.layer_patches_index = IntProperty(default=0)
    
    # Mesh quality properties
    bpy.types.Scene.includeMeshQualityDict = BoolProperty(
        name="Include Mesh Quality Dict",
        description="Include external mesh quality dictionary file",
        default=True
    )
    
    bpy.types.Scene.meshQualityDictPath = StringProperty(
        name="Mesh Quality Dict Path",
        description="Path to external mesh quality dictionary file",
        default="meshQualityDict"
    )
    
    bpy.types.Scene.relaxedMaxNonOrtho = FloatProperty(
        name="Relaxed Max Non-Orthogonality",
        description="Maximum non-orthogonality allowed in relaxed mode",
        default=75.0,
        min=0.0,
        max=180.0
    )
    
    bpy.types.Scene.nSmoothScale = IntProperty(
        name="Smooth Scale Iterations",
        description="Number of error distribution iterations",
        default=4,
        min=0
    )
    
    bpy.types.Scene.errorReduction = FloatProperty(
        name="Error Reduction",
        description="Amount to scale back displacement at error points",
        default=0.75,
        min=0.0,
        max=1.0
    )
    
    # Basic mesh quality settings if not using external file
    bpy.types.Scene.maxNonOrtho = FloatProperty(
        name="Max Non-Orthogonality",
        description="Maximum non-orthogonality allowed",
        default=65.0,
        min=0.0,
        max=180.0
    )
    
    bpy.types.Scene.maxBoundarySkewness = FloatProperty(
        name="Max Boundary Skewness",
        description="Maximum boundary face skewness allowed",
        default=20.0,
        min=0.0
    )
    
    bpy.types.Scene.maxInternalSkewness = FloatProperty(
        name="Max Internal Skewness",
        description="Maximum internal face skewness allowed",
        default=4.0,
        min=0.0
    )
    
    bpy.types.Scene.maxConcave = FloatProperty(
        name="Max Concaveness",
        description="Maximum concaveness allowed",
        default=80.0,
        min=0.0,
        max=180.0
    )
    
    bpy.types.Scene.minFlatness = FloatProperty(
        name="Min Flatness",
        description="Ratio of minimum projected area to actual area",
        default=0.5,
        min=0.0,
        max=1.0
    )
    
    bpy.types.Scene.minVol = FloatProperty(
        name="Min Volume",
        description="Minimum cell volume",
        default=1e-13,
        precision=15
    )
    
    bpy.types.Scene.minTetQuality = FloatProperty(
        name="Min Tet Quality",
        description="Minimum quality of tetrahedral cells",
        default=1e-30,
        min=0.0,
        max=1.0
    )
    
    bpy.types.Scene.snappy_dict_preview = StringProperty(default="")
    
    bpy.types.Scene.current_surface_tab = EnumProperty(
        name="Surface Settings",
        description="Surface refinement settings tabs",
        items=[
            ('regions', "Regions", "Region-specific refinement settings"),
            ('zones', "Zones", "Face and cell zone settings"),
            ('advanced', "Advanced", "Advanced surface settings"),
        ],
        default='regions'
    )
    
    # Update tooltips after all properties are registered
    register_tooltips()
    
    bpy.app.handlers.load_factory_startup_post.append(add_tutorials_to_scene)
    bpy.app.handlers.load_factory_startup_post.append(add_recents_to_scene)


def unregister():
    for cls in reversed(classes):
        try:
            unregister_class(cls)
        except Exception as e:
            print(f"Error unregistering {cls.__name__}: {e}")

    unregister_custom_icon(
        "venturial_logo", "/venturial/icons/custom_icons/venturial_logo.png"
    )
    unregister_custom_icon(
        "fossee_logo", "/venturial/icons/custom_icons/fossee_logo.png"
    )
    unregister_custom_icon(
        "new_mesh_file_2", "/venturial/icons/custom_icons/new_mesh_file_2.png"
    )
    unregister_custom_icon(
        "build_mesh_2", "/venturial/icons/custom_icons/build_mesh_2.png"
    )
    unregister_custom_icon(
        "warning_sign_1", "/venturial/icons/custom_icons/warning_sign_1.png"
    )
    unregister_custom_icon(
        "file-browser-2", "/venturial/icons/custom_icons/file-browser-2.png"
    )

    property_names = [
        "stl_file", "stl_file_name", "ui_category", "tool_type", "prompt_meshing_tool",
        "scene_blockmesh_panel_categories", "test_enum", "cellShapes", "cellShape_units",
        "mfile_item_ptr", "mfile_item", "mfile_item_index", "mesh_dict_name",
        "mesh_dict_path", "row_en", "cell_x", "cell_y", "cell_z", "ctm", "transform",
        "transformation_methods", "snapping", "snapping_methods", "simblk", "simblk_index",
        "bcustom", "bcustom_index", "vcustom", "vcustom_index", "fcustom", "fcustom_index",
        "ecustom", "ecustom_index", "vert_index", "cnt", "mode", "bdclist", "face_name",
        "facedes", "acustom", "acustom_index", "pcustom", "pcustom_index", "scustom",
        "scustom_index", "bscustom", "bscustom_index", "ipcnt", "edgelist", "face_sel_mode",
        "geometry_items", "geometry_items_index", "castellatedMesh", "snap", "addLayers",
        "maxLocalCells", "maxGlobalCells", "minRefinementCells", "maxLoadUnbalance",
        "nCellsBetweenLevels", "resolveFeatureAngle", "planarAngle",
        "locationInMeshX", "locationInMeshY", "locationInMeshZ",
        "allowFreeStandingZoneFaces", "cast_features", "cast_features_index",
        "cast_refinement_surfaces", "cast_refinement_surfaces_index",
        "cast_refinement_regions", "cast_refinement_regions_index",
        "nSmoothPatch", "tolerance", "nSolveIter", "nRelaxIter", 
        "useFeatureSnap", "nFeatureSnapIter", "implicitFeatureSnap", 
        "explicitFeatureSnap", "multiRegionFeatureSnap",
        "relativeSizes", "thickness_mode", "expansionRatio", "finalLayerThickness",
        "firstLayerThickness", "overallThickness", "minThickness", "featureAngle",
        "nGrow", "maxFaceThicknessRatio", "nSmoothSurfaceNormals", "nSmoothThickness",
        "minMedialAxisAngle", "maxThicknessToMedialRatio", "nSmoothNormals",
        "slipFeatureAngle", "layerRelaxIter", "nBufferCellsNoExtrude", "nLayerIter",
        "nRelaxedIter", "additionalReporting", "layer_patches", "layer_patches_index",
        "includeMeshQualityDict", "meshQualityDictPath", "relaxedMaxNonOrtho",
        "nSmoothScale", "errorReduction", "maxNonOrtho", "maxBoundarySkewness",
        "maxInternalSkewness", "maxConcave", "minFlatness", "minVol", "minTetQuality",
        "snappy_dict_preview", "current_surface_tab", "use_gap_level", "gap_level_increment",
        "handleSnapProblems", "useTopologicalSnapDetection", "show_layer_advanced",
        "layer_strategy", "detectExtrusionIsland"
    ]
    
    for prop in property_names:
        if hasattr(bpy.types.Scene, prop):
            try:
                delattr(bpy.types.Scene, prop)
            except Exception as e:
                print(f"Failed to delete property {prop}: {e}")
    
    try:
        if add_tutorials_to_scene in bpy.app.handlers.load_factory_startup_post:
            bpy.app.handlers.load_factory_startup_post.remove(add_tutorials_to_scene)
        if add_recents_to_scene in bpy.app.handlers.load_factory_startup_post:
            bpy.app.handlers.load_factory_startup_post.remove(add_recents_to_scene)
    except Exception as e:
        print(f"Error removing handlers: {e}")
