
import bpy
from bpy.types import Node, NodeTree, NodeSocket
from venturial_nodes.Nodes.Node import Venturial_Node

class N_Str_P(Node, Venturial_Node):
    '''
    Node to display and output string values.
    '''

    bl_idname = 'N_Str_P'
    bl_label = 'String Property'

    def _update_node_and_value(self, context):
        """Internal helper called when any relevant property changes."""
        self.update()

    name: bpy.props.StringProperty(
        name='Name',
        description='Display name for the node',
        default='String'
    )
    default: bpy.props.StringProperty(
        name='Value',
        description='The current string value',
        default='String',
        update=_update_node_and_value
    )

    def init(self, context):
        """Initializes the node when added to the tree."""
        self.outputs.new('NodeSocketString', 'Value')
        self.update()

    def copy(self, node):
        """Called when the node is duplicated."""
        print(f"Copying properties from node: {node.name} to {self.name}")

    def free(self):
        """Called when the node is removed."""
        print(f"Removing node: {self.name} ({self.bl_idname}). Sayonara!")

    # Elements to draw on the node
    def draw_buttons(self, context, layout):
        """Defines the UI layout within the node."""
        layout.prop(self,'name')
        layout.prop(self, 'default')

    def draw_buttons_ext(self, context, layout):
        """Defines the UI layout in the N-Panel when the node is selected."""
        layout.label(text='String Property Settings')
        layout.prop(self, 'name')
        layout.prop(self, 'default')

    # Main update logic for the node
    def update(self):
        """Updates the output socket."""

        if self.default != self.default:
            self.default = self.default

        if 'Value' in self.outputs:
            self.outputs['Value'].default_value = self.default
        else:
            print(f"Warning: Output socket 'Value' not found for node '{self.name}' during update.")
