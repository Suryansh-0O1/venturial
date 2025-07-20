import bpy
from bpy.types import Node, NodeTree, NodeSocket,PropertyGroup
from .Node import Venturial_Node
from ..Operator.Node_Links_Swapper import reorder_links ,path_from_id

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
    link_order: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    
    # Constructor of the node class
    def init(self, context):
        custom_input=self.inputs.new('Node_Socket_In','Dict_C')
        custom_input.link_limit = 4095
        self.outputs.new('Node_Socket_Out','Dict_C')
    
    def update(self):
        input_socket = self.inputs.get('Dict_C')
        if not input_socket:
            return

        current_links = [link.from_socket.node.name for link in input_socket.links]

        existing = [item.name for item in self.link_order]
        if set(current_links) != set(existing):
            self.link_order.clear()
            print("Clering link order")
            print("Current links: ", current_links)
            print("Existing link: ", existing)
            for name in current_links:
                self.link_order.add().name = name
            print("Link order: ", self.link_order)

    def copy(self, node):
        print('Copying node', node)
    
    def free(self):
        print('Removing node', self, "Sayonara!")
    
    # Elements to draw on the node
    def draw_buttons(self, context, layout):
        layout.prop(self, 'name')
     
    def draw_buttons_ext(self, context, layout):
        layout.label(text='Dictionary Order')
        for i, item in enumerate(self.link_order):
            row = layout.row(align=True)
            row.label(text=item.name)
            
            path = path = path_from_id(self)
            
            op_up = row.operator("node.move_link_order", text="", icon="TRIA_UP")
            op_up.node_path = path
            op_up.index = i
            op_up.direction = 'UP'
            
            op_down = row.operator("node.move_link_order", text="", icon="TRIA_DOWN")
            op_down.node_path = path
            op_down.index = i
            op_down.direction = 'DOWN'


    def move_link(self, index, direction):
        items = self.link_order
        if direction == 'UP' and index > 0:
            items.move(index, index - 1)
        elif direction == 'DOWN' and index < len(items) - 1:
            items.move(index, index + 1)
        else:
            return
        reorder_links(self,'Dict_C')


