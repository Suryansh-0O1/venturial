import bpy
from bpy.types import Node, NodeTree, NodeSocket
from .Node import Venturial_Node

class N_Enm_P(Node, Venturial_Node):
    '''
    Node to display integer values
    '''

    bl_idname = 'N_Enm_P'
    bl_label = 'Enum Property'
    bl_icon = 'NONE'

    def update_enm(self, context):
        print('Enum value updated')
        self.update()

    name: bpy.props.StringProperty(name='name', default='Enum')
    default: bpy.props.EnumProperty(
        items = [('PCG', 'PCG', 'PCG Solver')
        , ('RND', 'RND', 'Random Solver'), 
        ('SMP', 'SMP', 'Simple Solver')], 
        name='default', 
        default='PCG',
        update=update_enm)
    

    def init(self, context):
        self.outputs.new('NodeSocketString', 'Value')
    
    def copy(self, node):
        print('Copying node', node)
    
    def free(self):
        print('Removing node', self, "Sayonara!")
    
    def draw_buttons(self, context, layout):
        layout.prop(self, 'name')
        layout.prop(self, 'default')
    
    def draw_buttons_ext(self, context, layout):
        layout.label(text='Enum Node')
        layout.prop(self, 'name')
        layout.prop(self, 'default')
    
    def update(self):
        print('Enum value updated')
        self.outputs['Value'].default_value = self.default


