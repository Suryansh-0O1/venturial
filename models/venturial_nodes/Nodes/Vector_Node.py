import bpy
from bpy.types import Node, NodeTree, NodeSocket
from .Node import Venturial_Node

class Vec_P_Socket(NodeSocket):
    '''
    Custom Socket for Vector Property
    '''

    bl_idname = 'Vec_P_Socket'
    bl_label = 'Vector Property Socket'

    x: bpy.props.FloatProperty(name='x', default=0.0)
    y: bpy.props.FloatProperty(name='y', default=0.0)
    z: bpy.props.FloatProperty(name='z', default=0.0)

    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 1)

# # Implementation of Int Node for pyvnt
class N_Vec_P(Node, Venturial_Node):
    '''
    Node to display integer values
    '''

    bl_idname = 'N_Vec_P'
    bl_label = 'Vector Property'

    def _update_node_and_value(self, context):
        """Internal helper called when any relevant property changes."""
        self.update()



    name: bpy.props.StringProperty(name='name', default='Vector')
    minimum: bpy.props.FloatProperty(
        name='Minimum',
        description='The minimum allowed value',
        default=0,
        update=_update_node_and_value
    )
    maximum: bpy.props.FloatProperty(
        name='Maximum',
        description='The maximum allowed value',
        default=100,
        update=_update_node_and_value
    )
    x: bpy.props.FloatProperty(name='x', default=0.0,update=_update_node_and_value)
    y: bpy.props.FloatProperty(name='y', default=0.0,update=_update_node_and_value)
    z: bpy.props.FloatProperty(name='z', default=0.0,update=_update_node_and_value)

    # Constructor of the node class
    def init(self, context):
        self.outputs.new('Vec_P_Socket', 'Vector')
        self.update()
        # self.outputs.new('NodeSocketFloat', 'x')
        # self.outputs.new('NodeSocketFloat', 'y')
        # self.outputs.new('NodeSocketFloat', 'z')

    
    def copy(self, node):
        print('Copying node', node)
    
    def free(self):
        print('Removing node', self, "Sayonara!")
    
    # Elements to draw on the node
    def draw_buttons(self, context, layout):
        layout.label(text=f"Value: ({self.x}, {self.y}, {self.z})")
        layout.prop(self, 'name')
        layout.prop(self, 'x')
        layout.prop(self, 'y')
        layout.prop(self, 'z')
    
    # Elements to draw on the side panel
    def draw_buttons_ext(self, context, layout):
        layout.label(text='Vector Node')
        layout.prop(self, 'name')
        layout.prop(self, 'x')
        layout.prop(self, 'y')
        layout.prop(self, 'z')
        layout.label(text='Minimum And Maximum Value To clamp Default Value')
        layout.prop(self, 'minimum')
        layout.prop(self, 'maximum')

    
    def update(self):
        """Clamps the x, y, z values and updates the output socket."""
        if self.minimum > self.maximum:
            print(f"Warning: Minimum ({self.minimum}) was greater than Maximum ({self.maximum}). Swapping them.")
            self.minimum, self.maximum = self.maximum, self.minimum
    
        # Clamp each component
        x_clamped = max(self.minimum, min(self.x, self.maximum))
        y_clamped = max(self.minimum, min(self.y, self.maximum))
        z_clamped = max(self.minimum, min(self.z, self.maximum))
        
        # Only update if values actually changed (prevents infinite recursion)
        if self.x != x_clamped:
            self.x = x_clamped
        if self.y != y_clamped:
            self.y = y_clamped
        if self.z != z_clamped:
            self.z = z_clamped

        # Update the Vector output socket
        if 'Vector' in self.outputs:
            self.outputs['Vector'].x = self.x
            self.outputs['Vector'].y = self.y
            self.outputs['Vector'].z = self.z
        else:
            print(f"Warning: Output socket 'Vector' not found for node '{self.name}' during update.")