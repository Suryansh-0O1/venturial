import bpy
import os
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

class VNT_OT_generate_snappyhex_dict(Operator, ExportHelper):
    """Generate and save a snappyHexMeshDict file"""
    bl_idname = "vnt.generate_snappyhex_dict"
    bl_label = "Generate snappyHexMeshDict"
    
    filename_ext = ""
    filter_glob: bpy.props.StringProperty(default="*", options={'HIDDEN'})
    
    def execute(self, context):
        from venturial.models.snappyhexmesh.snappydict_writer import generate_snappy_dict, write_snappy_dict_to_file
        
        # Generate dictionary and save to preview
        dictionary = generate_snappy_dict(context.scene)
        context.scene.snappy_dict_preview = dictionary
        
        if self.filepath:
            # Make sure directory exists
            directory = os.path.dirname(self.filepath)
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                except Exception as e:
                    self.report({'ERROR'}, f"Failed to create directory: {e}")
                    return {'CANCELLED'}
            
            # Ensure the filepath ends with 'snappyHexMeshDict'
            target_path = self.filepath
            if not os.path.basename(target_path) or '.' in os.path.basename(target_path):
                target_path = os.path.join(target_path, 'snappyHexMeshDict')
            
            # Write to file
            success = write_snappy_dict_to_file(context.scene, target_path)
            if success:
                self.report({'INFO'}, f"Dictionary saved to {target_path}")
            else:
                self.report({'ERROR'}, f"Failed to write dictionary to {target_path}")
                return {'CANCELLED'}
        
        return {'FINISHED'}
