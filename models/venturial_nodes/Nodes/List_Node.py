import bpy
from bpy.types import Node, NodeTree, NodeSocket
from venturial_nodes.Nodes.Node import Venturial_Node
from ..Operator.Node_Links_Swapper import reorder_links ,path_from_id

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
    link_order: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    # Constructor of the node class
    def init(self, context):
        custom_input = self.inputs.new('List_CP_Socket_In', 'Element')
        custom_input.link_limit = 4095 # Allows multiple inputs to a single socket, can be replaced with `use_multi_socket` in latest version
        custom_input.display_shape = 'SQUARE'

        self.outputs.new('List_CP_Socket_Out', 'List_CP')
    
    def update(self):
        input_socket = self.inputs.get('Element')
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
        print("Removing Node", self, "Soayonara!")

    def draw_buttons(self, context, layout):
        layout.prop(self, 'isNode')
        layout.prop(self, 'name')

    
    def draw_buttons_ext(self, context, layout):
        layout.label(text='List Order')
        for i, item in enumerate(self.link_order):
            row = layout.row(align=True)
            row.label(text=item.name)
            path = path_from_id(self)

            op_up = row.operator("node.move_link_order", text="", icon="TRIA_UP")
            op_up.node_path = path
            op_up.index = i
            op_up.direction = 'UP'
            
            op_down = row.operator("node.move_link_order", text="", icon="TRIA_DOWN")
            op_down.node_path = path
            op_down.index = i
            op_down.direction = 'DOWN'


    # Link Order Change Operator
    def move_link(self, index, direction):
        items = self.link_order
        if direction == 'UP' and index > 0:
            items.move(index, index - 1)
        elif direction == 'DOWN' and index < len(items) - 1:
            items.move(index, index + 1)
        else:
            return
        reorder_links(self,'Element')

    
