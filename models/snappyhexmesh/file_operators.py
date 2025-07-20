import bpy
import os
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

class VNT_OT_export_stl_geometry(Operator, ExportHelper):
    """Export selected geometry as STL file"""
    bl_idname = "vnt.export_stl_geometry"
    bl_label = "Export STL Geometry"
    
    filename_ext = ".stl"
    filter_glob: bpy.props.StringProperty(default="*.stl", options={'HIDDEN'})
    
    def execute(self, context):
        if not context.selected_objects:
            self.report({'ERROR'}, "No objects selected for export")
            return {'CANCELLED'}
        
        bpy.ops.export_mesh.stl(
            filepath=self.filepath,
            check_existing=True,
            filter_glob="*.stl",
            use_selection=True,
            global_scale=1.0,
            use_scene_unit=False,
            ascii=False,
            use_mesh_modifiers=True,
            batch_mode='OFF'
        )
        context.scene.stl_file = self.filepath
        context.scene.stl_file_name = os.path.basename(self.filepath)
        
        self.report({'INFO'}, f"Exported STL to {self.filepath}")
        return {'FINISHED'}
