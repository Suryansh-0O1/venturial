import bpy
from bpy.types import Node, NodeTree, NodeSocket
from venturial_nodes.Nodes.Node import Venturial_Node

class N_Int_P(Node, Venturial_Node):
    '''
    Node to display and output integer values with configurable bounds.
    '''

    bl_idname = 'N_Int_P'
    bl_label = 'Int Property'

    def _update_node_and_value(self, context):
        """Internal helper called when any relevant property changes."""
        self.update()

    name: bpy.props.StringProperty(
        name='Name',
        description='Display name for the node',
        default='Int'
    )
    minimum: bpy.props.IntProperty(
        name='Minimum',
        description='The minimum allowed value',
        default=0,
        update=_update_node_and_value
    )
    maximum: bpy.props.IntProperty(
        name='Maximum',
        description='The maximum allowed value',
        default=100,
        update=_update_node_and_value
    )
    default: bpy.props.IntProperty(
        name='Value',
        description='The current integer value',
        default=1,
        update=_update_node_and_value
    )

    def init(self, context):
        """Initializes the node when added to the tree."""
        self.outputs.new('NodeSocketInt', 'Value')
        self.update()

    def copy(self, node):
        """Called when the node is duplicated."""
        print(f"Copying properties from node: {node.name} to {self.name}")

    def free(self):
        """Called when the node is removed."""
        print(f"Removing node: {self.name} ({self.bl_idname}). Sayonara!")

    def draw_buttons(self, context, layout):
        """Defines the UI layout within the node."""
        layout.prop(self, 'default')

    def draw_buttons_ext(self, context, layout):
        """Defines the UI layout in the N-Panel when the node is selected."""
        layout.label(text='Int Property Settings')
        layout.prop(self, 'name')
        layout.prop(self, 'default')
        layout.prop(self, 'minimum')
        layout.prop(self, 'maximum')

    def update(self):
        """Clamps the value and updates the output socket."""

        if self.minimum > self.maximum:
             print(f"Warning: Minimum ({self.minimum}) was greater than Maximum ({self.maximum}). Swapping them.")
             self.minimum, self.maximum = self.maximum, self.minimum

        # Clamp the main value 
        clamped_value = max(self.minimum, min(self.default, self.maximum))

        if self.default != clamped_value:
            self.default = clamped_value

        if 'Value' in self.outputs:
            self.outputs['Value'].default_value = self.default
        else:
            print(f"Warning: Output socket 'Value' not found for node '{self.name}' during update.")
