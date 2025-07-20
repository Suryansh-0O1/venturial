import bpy
from bpy.types import Node, NodeTree, NodeSocket
from .Node import Venturial_Node

class Dim_P_Socket(NodeSocket):
    '''
    Custom Socket for Dimension Property
    '''

    bl_idname = 'Dim_P_Socket'
    bl_label = 'Dimension Property Socket'

    m: bpy.props.IntProperty(name='m', default=0)
    l: bpy.props.IntProperty(name='l', default=0)
    t: bpy.props.IntProperty(name='t', default=0)
    temp: bpy.props.IntProperty(name='temp', default=0) 
    mol: bpy.props.IntProperty(name='mol', default=0)
    c: bpy.props.IntProperty(name='c', default=0) 
    li: bpy.props.IntProperty(name='li', default=0)
    
    dimensions_list: bpy.props.IntVectorProperty(
        name='Dimensions List',
        size=7,  # 7 dimensions
        default=(0, 0, 0, 0, 0, 0, 0)
    )
    
    @property
    def default_value(self):
        return [self.m, self.l, self.t, self.temp, self.mol, self.c, self.li]

    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 1)

class N_Dim_P(Node, Venturial_Node):
    '''
    Node to display integer values
    '''

    bl_idname = 'N_Dim_P'
    bl_label = 'Dimension Property'
    bl_icon = 'NONE'

    def _update_node_and_value(self, context):
        """Internal helper called when any relevant property changes."""
        self.update()

    name: bpy.props.StringProperty(name='name', default='Int')
    minimum: bpy.props.IntProperty(name='minimum', default=-100,update=_update_node_and_value)
    maximum: bpy.props.IntProperty(name='maximum', default=100,update=_update_node_and_value)
    m: bpy.props.IntProperty(name='m', default=0,update=_update_node_and_value)
    l: bpy.props.IntProperty(name='l', default=0,update=_update_node_and_value)
    t: bpy.props.IntProperty(name='t', default=0,update=_update_node_and_value)
    temp: bpy.props.IntProperty(name='temp', default=0,update=_update_node_and_value) 
    mol: bpy.props.IntProperty(name='mol', default=0,update=_update_node_and_value)
    c: bpy.props.IntProperty(name='c', default=0,update=_update_node_and_value) 
    li: bpy.props.IntProperty(name='li', default=0,update=_update_node_and_value)

    def init(self, context):
        self.outputs.new('Dim_P_Socket', 'Dimention Set')
        self.update()

    def copy(self, node):
        print('Copying node', node)
    
    def free(self):
        print('Removing node', self, "Sayonara!")
    
    def draw_buttons(self, context, layout):
        layout.label(text=f"Value: [{self.m}, {self.l}, {self.t}, {self.temp}, {self.mol}, {self.c}, {self.li}]")
        layout.prop(self, 'name')
        layout.prop(self, 'm')
        layout.prop(self, 'l')
        layout.prop(self, 't')
        layout.prop(self, 'temp')
        layout.prop(self, 'mol')
        layout.prop(self, 'c')
        layout.prop(self, 'li')
    
    def draw_buttons_ext(self, context, layout):
        layout.label(text='Int Node')
        layout.prop(self, 'name')
        layout.prop(self, 'm')
        layout.prop(self, 'l')
        layout.prop(self, 't')
        layout.prop(self, 'temp')
        layout.prop(self, 'mol')
        layout.prop(self, 'c')
        layout.prop(self, 'li')
        layout.label(text='Minimum And Maximum Value To clamp Default Value')
        layout.prop(self, 'minimum')
        layout.prop(self, 'maximum')

    def update(self):
        """Clamps the dimension values and updates the output socket."""
        if self.minimum > self.maximum:
            print(f"Warning: Minimum ({self.minimum}) was greater than Maximum ({self.maximum}). Swapping them.")
            self.minimum, self.maximum = self.maximum, self.minimum
    
        m_clamped = max(self.minimum, min(self.m, self.maximum))
        l_clamped = max(self.minimum, min(self.l, self.maximum))
        t_clamped = max(self.minimum, min(self.t, self.maximum))
        temp_clamped = max(self.minimum, min(self.temp, self.maximum))
        mol_clamped = max(self.minimum, min(self.mol, self.maximum))
        c_clamped = max(self.minimum, min(self.c, self.maximum))
        li_clamped = max(self.minimum, min(self.li, self.maximum))
        
        # Only update if values actually changed (prevents infinite recursion)
        if self.m != m_clamped:
            self.m = m_clamped
        if self.l != l_clamped:
            self.l = l_clamped
        if self.t != t_clamped:
            self.t = t_clamped
        if self.temp != temp_clamped:
            self.temp = temp_clamped
        if self.mol != mol_clamped:
            self.mol = mol_clamped
        if self.c != c_clamped:
            self.c = c_clamped
        if self.li != li_clamped:
            self.li = li_clamped
            
        # Update the dimension output socket
        if 'Dimention Set' in self.outputs:
            # Set individual properties
            self.outputs['Dimention Set'].m = self.m
            self.outputs['Dimention Set'].l = self.l
            self.outputs['Dimention Set'].t = self.t
            self.outputs['Dimention Set'].temp = self.temp
            self.outputs['Dimention Set'].mol = self.mol
            self.outputs['Dimention Set'].c = self.c
            self.outputs['Dimention Set'].li = self.li
            
            # Set the dimensions_list property for list access
            self.outputs['Dimention Set'].dimensions_list = (
                self.m, self.l, self.t, self.temp, self.mol, self.c, self.li
            )
        else:
            print(f"Warning: Output socket 'Dimention Set' not found for node '{self.name}' during update.")



