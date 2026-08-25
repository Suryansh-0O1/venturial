from .models.classy_preferences import ClassyBlocksPreferences
from .models.classy_properties import ClassyFacePatch, ClassyMeshObjectProperties, ClassyMeshSceneProperties
from .views.classy_ui import CLASSY_PT_main_panel
from .views.classy_operators import (
    CLASSY_OT_generate_mesh,
    CLASSY_OT_run_blockmesh,
    CLASSY_OT_convert_vtk,
    CLASSY_OT_reload_mesh,
    CLASSY_OT_export_terrain_stl,
    CLASSY_OT_project_to_stl,
    CLASSY_OT_run_all,
    CLASSY_OT_add_box,
    CLASSY_OT_add_cylinder,
    CLASSY_OT_add_frustum,
    CLASSY_OT_extrude_sketch,
    CLASSY_OT_revolve_sketch,
    CLASSY_OT_tag_extrude,
    CLASSY_OT_tag_revolve,
    CLASSY_OT_tag_loft,
    CLASSY_OT_add_boundary_patch,
    CLASSY_OT_remove_boundary_patch,
    CLASSY_OT_preview_projection,
    CLASSY_OT_clear_preview
)
from .utils.classy.sketch_tool import CLASSY_OT_add_sketch_point
from .utils.classy.foam_directories import FoamDirectoryProperties, CLASSY_PT_foam_directories
from .utils.classy.tutorial_manager import (
    TutorialManagerProperties,
    CLASSY_OT_search_tutorials,
    CLASSY_OT_copy_tutorial,
    CLASSY_OT_confirm_case_path,
    CLASSY_PT_tutorial_manager
)
from .utils.classy.dependencies import CLASSY_OT_install_python_deps, CLASSY_OT_install_openfoam

classes = (
    ClassyBlocksPreferences,
    ClassyFacePatch,
    ClassyMeshObjectProperties,
    ClassyMeshSceneProperties,
    CLASSY_PT_main_panel,
    CLASSY_OT_generate_mesh,
    CLASSY_OT_run_blockmesh,
    CLASSY_OT_convert_vtk,
    CLASSY_OT_reload_mesh,
    CLASSY_OT_export_terrain_stl,
    CLASSY_OT_project_to_stl,
    CLASSY_OT_add_sketch_point,
    CLASSY_OT_run_all,
    CLASSY_OT_add_box,
    CLASSY_OT_add_cylinder,
    CLASSY_OT_add_frustum,
    CLASSY_OT_extrude_sketch,
    CLASSY_OT_revolve_sketch,
    CLASSY_OT_tag_extrude,
    CLASSY_OT_tag_revolve,
    CLASSY_OT_tag_loft,
    CLASSY_OT_add_boundary_patch,
    CLASSY_OT_remove_boundary_patch,
    CLASSY_OT_preview_projection,
    CLASSY_OT_clear_preview,
    FoamDirectoryProperties,
    CLASSY_PT_foam_directories,
    TutorialManagerProperties,
    CLASSY_OT_search_tutorials,
    CLASSY_OT_copy_tutorial,
    CLASSY_OT_confirm_case_path,
    CLASSY_PT_tutorial_manager,
    CLASSY_OT_install_python_deps,
    CLASSY_OT_install_openfoam,
)

import bpy
from .utils.classy import auto_update, dependencies, sketch_tool

@bpy.app.handlers.persistent
def _on_load_post(filepath) -> None:
    try:
        prefs = bpy.context.preferences.addons.get("venturial")
        if not prefs:
            return
        p = prefs.preferences
        scene_props = bpy.context.scene.classy_mesh_props

        if not scene_props.case_path:
            remembered = getattr(p, "last_case_dir", None) or getattr(p, "default_case_dir", None)
            if remembered:
                scene_props.case_path = remembered

        scene_props.use_auto_update = False
    except Exception:
        pass

def register_props():
    bpy.types.Object.classy_block_props = bpy.props.PointerProperty(type=ClassyMeshObjectProperties)
    bpy.types.Scene.classy_mesh_props = bpy.props.PointerProperty(type=ClassyMeshSceneProperties)
    bpy.types.Scene.foam_dirs = bpy.props.PointerProperty(type=FoamDirectoryProperties)
    bpy.types.Scene.tutorial_manager = bpy.props.PointerProperty(type=TutorialManagerProperties)
    auto_update.register()
    dependencies.register_startup_checks()
    if _on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load_post)

def unregister_props():
    if _on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load_post)
    dependencies.unregister_startup_checks()
    auto_update.unregister()
    sketch_tool.unregister_handlers()
    if hasattr(bpy.types.Scene, "foam_dirs"): del bpy.types.Scene.foam_dirs
    if hasattr(bpy.types.Scene, "tutorial_manager"): del bpy.types.Scene.tutorial_manager
    if hasattr(bpy.types.Object, "classy_block_props"): del bpy.types.Object.classy_block_props
    if hasattr(bpy.types.Scene, "classy_mesh_props"): del bpy.types.Scene.classy_mesh_props
