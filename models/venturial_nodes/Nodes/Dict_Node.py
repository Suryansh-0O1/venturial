
import bpy
from bpy.types import Node, NodeTree, NodeSocket
from venturial_nodes.Nodes.Node import Venturial_Node

class Dict_C_Socket_In(NodeSocket):
    '''
    Custom Socket for Dict_C class
    '''

    bl_idname = 'Dict_C_Socket_In'
    bl_label = 'Dict_C Input Socket'

    key: bpy.props.StringProperty(name='key', default='')

    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 1)

class Dict_C_Socket_Out(NodeSocket):
    '''
    Custom Socket for Dict_C class
    '''

    bl_idname = 'Dict_C_Socket_Out'
    bl_label = 'Dict_C Output Socket'

    key: bpy.props.StringProperty(name='keys', default='')

    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216,1)

class N_Dict_C(Node, Venturial_Node):
    '''
    Node to store Dict_C class variables
    '''

    bl_idname = 'N_Dict_C'
    bl_label = 'Dict_C'
    bl_icon = 'NONE'

    name: bpy.props.StringProperty(name='name', default='Dict_C')
    values: bpy.props.StringProperty(name='values', default='') # to be replaced
    

    # Constructor of the node class
    def init(self, context):
        custom_input = self.inputs.new('Dict_C_Socket_In', 'Dict_C')
        custom_input.link_limit = 4095 # Allows multiple inputs to a single socket, can be replaced with `use_multi_socket` in latest version
        custom_input.display_shape = 'SQUARE'

        self.outputs.new('Dict_C_Socket_Out', 'Dict_C')
    
    def copy(self, node):
        print('Copying node', node)
    
    def free(self):
        print('Removing node', self, "Sayonara!")
    
    # Elements to draw on the node
    def draw_buttons(self, context, layout):
        layout.prop(self, 'name')
        