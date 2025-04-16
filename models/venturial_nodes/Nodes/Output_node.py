import bpy
from bpy.types import Node, NodeTree, NodeSocket
from venturial_nodes.Nodes.Node import Venturial_Node


class Node_Socket_In(NodeSocket):
    '''
    Custom Socket for Dict_C class
    '''

    bl_idname = 'Node_Socket_In'
    bl_label = 'Node Input Socket'

    key: bpy.props.StringProperty(name='key', default='')

    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 1)

class Node_Socket_Out(NodeSocket):
    '''
    Custom Socket for Dict_C class
    '''

    bl_idname = 'Node_Socket_Out'
    bl_label = 'Node Output Socket'

    key: bpy.props.StringProperty(name='keys', default='')

    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216,1)



# Implementation of Output Node for venturial - HEAD NODE
class N_OUTPUT_P(Node, Venturial_Node):
    '''
    Output/Head node for the Venturial node tree
    This node represents the final output of the node tree
    '''

    bl_idname = 'N_OUTPUT_P'
    bl_label = 'OUTPUT NODE'
    bl_icon = 'OUTPUT'
    
    # Designate this as a head node
    is_head_node: bpy.props.BoolProperty(default=True, options={'HIDDEN'})
    values: bpy.props.StringProperty(name='values', default='')
    
    # Constructor of the node class
    def init(self, context):
        custom_input=self.inputs.new('Node_Socket_In','Dict_C')
        custom_input.link_limit = 4095
        self.outputs.new('Node_Socket_Out','Dict_C')
    
    def copy(self, node):
        print('Copying node', node)
    
    def free(self):
        print('Removing node', self, "Sayonara!")
    
    # Elements to draw on the node
    def draw_buttons(self, context, layout):
        layout.prop(self, 'name')
     


