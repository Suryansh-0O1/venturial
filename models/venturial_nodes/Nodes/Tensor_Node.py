import bpy
from bpy.types import Node, NodeTree, NodeSocket
from .Node import Venturial_Node  

class Ten_P_Socket(NodeSocket):
    '''
    Custom Socket for Tensor Property
    '''

    bl_idname = 'Ten_P_Socket'
    bl_label = 'Tensor Property Socket'

    xx: bpy.props.FloatProperty(name='xx', default=0.0)
    xy: bpy.props.FloatProperty(name='xy', default=0.0)
    xz: bpy.props.FloatProperty(name='xz', default=0.0)

    yx: bpy.props.FloatProperty(name='yx', default=0.0)
    yy: bpy.props.FloatProperty(name='yy', default=0.0)
    yz: bpy.props.FloatProperty(name='yz', default=0.0)

    zx: bpy.props.FloatProperty(name='zx', default=0.0)
    zy: bpy.props.FloatProperty(name='zy', default=0.0)
    zz: bpy.props.FloatProperty(name='zz', default=0.0)

    def draw(self, context, layout, node, text):
        layout.label(text=text)    
    
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 1)

# Implementation of Int Node for pyvnt
class N_Ten_P(Node, Venturial_Node):
    '''
    Node to display integer values
    '''

    bl_idname = 'N_Ten_P'
    bl_label = 'Tensor Property'
    # bl_icon = 'NONE'

    name: bpy.props.StringProperty(name='name', default='Tensor')

    xx: bpy.props.FloatProperty(name='xx', default=0.0)
    xy: bpy.props.FloatProperty(name='xy', default=0.0)
    xz: bpy.props.FloatProperty(name='xz', default=0.0)

    yx: bpy.props.FloatProperty(name='yx', default=0.0)
    yy: bpy.props.FloatProperty(name='yy', default=0.0)
    yz: bpy.props.FloatProperty(name='yz', default=0.0)

    zx: bpy.props.FloatProperty(name='zx', default=0.0)
    zy: bpy.props.FloatProperty(name='zy', default=0.0)
    zz: bpy.props.FloatProperty(name='zz', default=0.0)

    # Constructor of the node class
    def init(self, context):
        self.outputs.new('Ten_P_Socket', 'Tensor')
        
        self.outputs.new('NodeSocketFloat', 'xx')
        self.outputs.new('NodeSocketFloat', 'xy')
        self.outputs.new('NodeSocketFloat', 'xz')

        self.outputs.new('NodeSocketFloat', 'yx')
        self.outputs.new('NodeSocketFloat', 'yy')
        self.outputs.new('NodeSocketFloat', 'yz')

        self.outputs.new('NodeSocketFloat', 'zx')
        self.outputs.new('NodeSocketFloat', 'zy')
        self.outputs.new('NodeSocketFloat', 'zz')

        self.inputs.new('NodeSocketFloat', 'xx')
        self.inputs.new('NodeSocketFloat', 'xy')
        self.inputs.new('NodeSocketFloat', 'xz')

        self.inputs.new('NodeSocketFloat', 'yx')
        self.inputs.new('NodeSocketFloat', 'yy')
        self.inputs.new('NodeSocketFloat', 'yz')

        self.inputs.new('NodeSocketFloat', 'zx')
        self.inputs.new('NodeSocketFloat', 'zy')
        self.inputs.new('NodeSocketFloat', 'zz')
    
    def copy(self, node):
        print('Copying node', node)
    
    def free(self):
        print('Removing node', self, "Sayonara!")
    
    # Elements to draw on the node
    def draw_buttons(self, context, layout):
        lay = layout.box()
        lay.label(text=f"Tensor: ")
        lay.label(text=f"{self.xx}, {self.xy}, {self.xz}")
        lay.label(text=f"{self.yx}, {self.yy}, {self.yz}")
        lay.label(text=f"{self.zx}, {self.zy}, {self.zz}")


        layout.prop(self, 'name')
    
    # Elements to draw on the side panel
    def draw_buttons_ext(self, context, layout):
        layout.label(text='Vector Node')
        layout.prop(self, 'name')
        layout.prop(self, 'default')
        layout.prop(self, 'minimum')
        layout.prop(self, 'maximum')


