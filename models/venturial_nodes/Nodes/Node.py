import bpy
from bpy.types import NodeTree
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class Venturial_Node_Tree(NodeTree):
    '''Venturial node tree type that will show up in the editor type list'''
    bl_idname = 'venturial.node_tree'
    bl_label = "Venturial Nodes"
    bl_icon = 'NODETREE'

    imported_file_path: bpy.props.StringProperty(
        name="Imported File",
        description="Path to the last file imported for this specific tree instance",
        default="",
        subtype='FILE_PATH'
    )

class Venturial_Node:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'venturial.node_tree'

class Venturial_Node_Category(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'venturial.node_tree'