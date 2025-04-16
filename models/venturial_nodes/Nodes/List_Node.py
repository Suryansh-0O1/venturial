import bpy
from bpy.types import Node, NodeTree, NodeSocket
from venturial_nodes.Nodes.Node import Venturial_Node

class List_CP_Socket_In(NodeSocket):
    '''
    Custom Socket for Key_C class
    '''

    bl_idname = 'List_CP_Socket_In'
    bl_label = 'List_CP Input Socket'

    key: bpy.props.StringProperty(name='values', default='')

    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.5, 1)

class List_CP_Socket_Out(NodeSocket):
    '''
    Custom Socket for Key_C class
    '''
    bl_idname = 'List_CP_Socket_Out'
    bl_label = 'List_CP Output Socket'

    key: bpy.props.StringProperty(name='values', default='')

    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.5, 1)

class N_List_CP(Node, Venturial_Node):
    '''
    Node to store List_CP class variables
    '''

    bl_idname = 'N_List_CP'
    bl_label = 'List_CP'
    bl_icon = 'NONE'

    name: bpy.props.StringProperty(name='name', default='List_CP')
    values: bpy.props.StringProperty(name='values', default='') # to be replaced
    isNode: bpy.props.BoolProperty(name='isNode', default=False)
    

    # Constructor of the node class
    def init(self, context):
        custom_input = self.inputs.new('List_CP_Socket_In', 'Element')
        custom_input.link_limit = 4095 # Allows multiple inputs to a single socket, can be replaced with `use_multi_socket` in latest version
        custom_input.display_shape = 'SQUARE'

        self.outputs.new('List_CP_Socket_Out', 'List_CP')
    
    def copy(self, node):
        print('Copying node', node)
    
    def free(self):
        print("Removing Node", self, "Soayonara!")

    def draw_buttons(self, context, layout):
        layout.prop(self, 'isNode')
        layout.prop(self, 'name')

    
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, 'isNode')
        layout.label(text='List_CP Node')