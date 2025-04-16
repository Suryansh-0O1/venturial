import bpy
from bpy.types import Node, NodeSocket, Operator
from bpy.props import EnumProperty, IntProperty, FloatProperty

from venturial_nodes.Nodes.Node import Venturial_Node

class MultiValue_Socket_Out(NodeSocket):
    bl_idname = 'MultiValue_Socket_Out'
    bl_label = 'Multi Value Output Socket'

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return (0.8, 0.8, 0.2, 1.0)

class NODE_OT_multi_value_add(Operator):
    bl_idname = "node.multi_value_add"
    bl_label = "Add Value Input"
    bl_description = "Add another value input socket"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_node and context.active_node.bl_idname == 'N_MultiValue_P'

    def execute(self, context):
        node = context.active_node
        node.num_values += 1
        return {'FINISHED'}

class NODE_OT_multi_value_remove(Operator):
    bl_idname = "node.multi_value_remove"
    bl_label = "Remove Value Input"
    bl_description = "Remove the last value input socket"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_node and context.active_node.bl_idname == 'N_MultiValue_P' and context.active_node.num_values > 1

    def execute(self, context):
        node = context.active_node
        if node.num_values > 1:
            node.num_values -= 1
        return {'FINISHED'}


class N_MultiValue_P(Node, Venturial_Node):
    bl_idname = 'N_MultiValue_P'
    bl_label = 'Multi Value'
    bl_icon = 'SEQUENCE'

    def _update_sockets(self, context):
        """Called when value_type, num_values, min_value, or max_value changes."""
        if self.max_value < self.min_value:
            if self.is_property_set("max_value"):
                self.min_value = self.max_value
            else:
                self.max_value = self.min_value
        self.update_dynamic_sockets()
    

    value_type: EnumProperty(
        name="Value Type",
        description="Type of value sockets to use",
        items=[('INT', "Integer", "Use integer sockets"),
               ('FLOAT', "Float", "Use float sockets")],
        default='FLOAT',
        update=_update_sockets
    )

    num_values: IntProperty(
        name="Number of Values",
        description="How many value inputs to show",
        default=1,
        min=1,
        update=_update_sockets
    )

    min_value: IntProperty(
        name="Min",
        description="Minimum allowed value for sockets",
        default=0,
        update=_update_sockets
    )

    max_value: IntProperty(
        name="Max",
        description="Maximum allowed value for sockets",
        default=1,
        update=_update_sockets
    )

    _int_defaults: list = []
    _float_defaults: list = []


    def init(self, context):
        self.outputs.new('MultiValue_Socket_Out', 'Values Out')
        self.update_dynamic_sockets(is_init=True)

    def draw_buttons(self, context, layout):
        col = layout.column(align=True)
        # Type Toggle
        col.prop(self, "value_type", expand=True)

        # Min/Max Row
        row_limits = col.row(align=True)
        row_limits.prop(self, "min_value")
        row_limits.prop(self, "max_value")

        # +/- Buttons Row
        row_add_remove = col.row(align=True)
        row_add_remove.operator(NODE_OT_multi_value_add.bl_idname, text="", icon='ADD')
        row_add_remove.operator(NODE_OT_multi_value_remove.bl_idname, text="", icon='REMOVE')

    def update_dynamic_sockets(self, is_init=False):
        """Remove old sockets and create new ones based on properties."""
        current_min = float(self.min_value)
        current_max = float(self.max_value)

        if not is_init:
            # Store defaults, clamp them based on the *new* min/max limits
            self._int_defaults = [int(max(current_min, min(current_max, inp.default_value))) \
                                  for inp in self.inputs if inp.bl_idname == 'NodeSocketInt']
            self._float_defaults = [max(current_min, min(current_max, inp.default_value)) \
                                    for inp in self.inputs if inp.bl_idname == 'NodeSocketFloat']

        # Remove existing dynamic input sockets
        for i in range(len(self.inputs) - 1, -1, -1):
             self.inputs.remove(self.inputs[i])

        if self.value_type == 'FLOAT':
            socket_type_idname = 'NodeSocketFloat'
            default_list = self._float_defaults
            base_default_val = 0.0
            clamped_base_default = max(current_min, min(current_max, base_default_val))
        else:
            socket_type_idname = 'NodeSocketInt'
            default_list = self._int_defaults
            base_default_val = 0
            clamped_base_default = int(max(current_min, min(current_max, float(base_default_val))))


        # 4. Create new sockets
        for i in range(self.num_values):
            socket_name = f"Value_{i}"
            new_socket = self.inputs.new(socket_type_idname, socket_name)
            try:
                restored_default = default_list[i]
                if self.value_type == 'FLOAT':
                    new_socket.default_value = max(current_min, min(current_max, float(restored_default)))
                else:
                    new_socket.default_value = int(max(current_min, min(current_max, float(restored_default))))
            except IndexError:
                new_socket.default_value = clamped_base_default

            if self.value_type == 'FLOAT':
                if hasattr(new_socket, "min_value"):
                    new_socket.min_value = float(self.min_value)
                if hasattr(new_socket, "max_value"):
                    new_socket.max_value = float(self.max_value)
                if hasattr(new_socket, "soft_min"):
                    new_socket.soft_min = float(self.min_value)
                if hasattr(new_socket, "soft_max"):
                    new_socket.soft_max = float(self.max_value)
            else:
                if hasattr(new_socket, "min_value"):
                    new_socket.min_value = self.min_value
                if hasattr(new_socket, "max_value"):
                    new_socket.max_value = self.max_value


    def copy(self, node):
        print(f"Copying node {self.name} from {node.name}")


    def free(self):
        print(f"Freeing node {self.name}")


    def update(self):
        """Called frequently by Blender, enforce clamping on socket values."""
        print(f"Node {self.name} update method called.")
        current_min = float(self.min_value)
        current_max = float(self.max_value)

        for socket in self.inputs:
            original_value = socket.default_value
            clamped_value = original_value # Initialize with original

            if socket.bl_idname == 'NodeSocketFloat':
                clamped_value = max(current_min, min(current_max, float(original_value)))
            elif socket.bl_idname == 'NodeSocketInt':
                # Ensure we are comparing floats for clamping range check
                clamped_value = int(max(current_min, min(current_max, float(original_value))))
            socket.default_value=clamped_value
