import bpy
from bpy.types import Operator

class NODE_OT_Add_Elem(Operator):
    bl_idname = "node.list_add_element"
    bl_label = "Add Element"
    bl_description = "Add an element to the list node"

    def execute(self, context):
        node = context.active_node
        new_input = node.inputs.new('List_CP_Socket_In', 'Element')
        new_input.link_limit = 4095 # Allows multiple inputs to a single socket, can be replaced with `use_multi_socket` in latest version
        new_input.display_shape = 'SQUARE'
        return {'FINISHED'}

class NODE_OT_Remove_Elem(Operator):
    bl_idname = "node.list_remove_element"
    bl_label = "Remove Element"
    bl_description = "Remove an element from the list node"

    def execute(self, context):
        node = context.active_node
        node.inputs.remove(node.inputs.active)
        return {'FINISHED'}

