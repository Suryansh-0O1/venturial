import bpy
from bpy.types import Node, NodeTree, NodeSocket, PropertyGroup
from venturial_nodes.Nodes.Node import Venturial_Node

class Property_Types(PropertyGroup):
    '''
    Property Group to store Key_C class variables
    '''

    name: bpy.props.StringProperty(name='name', default='')
    value: bpy.props.IntProperty(name='value', default=0) or bpy.props.FloatProperty(name='value', default=0.0) or bpy.props.EnumProperty(name='value',items=[], default='')

class Key_C_Socket_In(NodeSocket):
    '''
    Custom Socket for Key_C class
    '''

    bl_idname = 'Key_C_Socket_In'
    bl_label = 'Key_C Input Socket'

    # key: bpy.props.StringProperty(name='values', default='')

    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (0, 0.56, 0.196, 1)

class Key_C_Socket_Out(NodeSocket):
    '''
    Custom Socket for Key_C class
    '''

    bl_idname = 'Key_C_Socket_Out'
    bl_label = 'Key_C Output Socket'

    default_value: bpy.props.StringProperty(name='values', default='')

    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 1)

class N_Key_C(Node, Venturial_Node):
    '''
    Node to store Key_C class variables
    '''

    bl_idname = 'N_Key_C'
    bl_label = 'Key_C'
    bl_icon = 'NONE'

    name: bpy.props.StringProperty(name='name', default='Key_C')
    # values: bpy.props.CollectionProperty(type=Key_C_Socket_In)
    

    # Constructor of the node class
    def init(self, context):
        custom_input = self.inputs.new('Key_C_Socket_In', 'Key_C')
        custom_input.link_limit = 4095 # Allows multiple inputs to a single socket, can be replaced with `use_multi_socket` in latest version
        custom_input.display_shape = 'SQUARE'

        self.outputs.new('Key_C_Socket_Out', 'Key_C')
    
    def copy(self, node):
        print('Copying node', node)
    
    def free(self):
        print('Removing node', self, "Sayonara!")
    
    # Elements to draw on the node
    def draw_buttons(self, context, layout):
        layout.prop(self, 'name')
    
    def update(self):
        for sock in self.inputs:
            values = []
            for conn in sock.links:
                # Check if the from_socket is a vector socket
                if hasattr(conn.from_socket, 'bl_idname') and conn.from_socket.bl_idname == 'Vec_P_Socket':
                    # Handle Vec_P_Socket specially - it has x, y, z properties instead of default_value
                    values.append((conn.from_socket.x, conn.from_socket.y, conn.from_socket.z))
                else:
                    # For regular sockets with default_value
                    if hasattr(conn.from_socket, 'default_value'):
                        values.append(conn.from_socket.default_value)
                    else:
                        values.append(None)  # Handle any other unexpected socket types
            print(f'Node updated -> {values}')
    
    def socket_value_update(self, context):
        print('Socket value updated')
        self.update()
    
        