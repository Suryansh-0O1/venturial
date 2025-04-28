import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from pyvnt import *

NODE_Y_SPACING = -60
LEVEL_X_SPACING = -300
SIBLING_Y_SPACING = -60
FRAME_PADDING = 40

# Dictionary to track the last used y-position at each x-coordinate
last_y_position_at_x = {}

def get_next_y_position(x_pos, requested_y_pos):
    """
    Get the next available y-position at the given x-coordinate.
    This ensures nodes at the same x-level won't overlap.
    """
    global last_y_position_at_x
    
    # If this x-position has been used before, use the last y-position at this x
    # plus spacing, unless the requested y-pos is already lower
    if x_pos in last_y_position_at_x:
        return min(requested_y_pos, last_y_position_at_x[x_pos] + SIBLING_Y_SPACING)
    else:
        return requested_y_pos

def update_last_y_position(x_pos, y_pos):
    """
    Update the last used y-position at the given x-coordinate.
    This should be called after placing a node.
    """
    global last_y_position_at_x
    if x_pos not in last_y_position_at_x or y_pos < last_y_position_at_x[x_pos]:
        last_y_position_at_x[x_pos] = y_pos

def create_blender_node(node_tree, node_type, name, location, parent_frame=None):
    """Create a Blender node of the specified type"""
    node = node_tree.nodes.new(type=node_type)
    node.name = name
    # node.label = name 
    node.location = location
    if parent_frame:
        node.parent = parent_frame
    return node

def setup_node_properties(blender_node, pyvnt_node):
    """Set up properties for different node types"""
    print(f"Setting up properties")
    # print(f"\nSetting up properties for {blender_node.name} ({blender_node.bl_idname})")
    if isinstance(pyvnt_node, Int_P):
        print(f"Setting up Int_P node with value: {pyvnt_node.give_val()}")
        blender_node.outputs['Value'].default_value = pyvnt_node.give_val()
        blender_node.minimum = pyvnt_node._Int_P__minimum
        blender_node.maximum = pyvnt_node._Int_P__maximum
    elif isinstance(pyvnt_node, Flt_P):
        print(f"Setting up Flt_P node with value: {pyvnt_node.give_val()}")
        blender_node.outputs['Value'].default_value = pyvnt_node.give_val()
        blender_node.minimum = pyvnt_node._Flt_P__minimum
        blender_node.maximum = pyvnt_node._Flt_P__maximum
    elif isinstance(pyvnt_node, Str_P):
        print(f"Setting up Str_P node with value: {pyvnt_node.give_val()}")
        blender_node.outputs['Value'].default_value = pyvnt_node.give_val()
    elif isinstance(pyvnt_node, Enm_P):
        print(f"Setting up Enm_P node with value: {pyvnt_node.give_val()}")
        blender_node.outputs['Value'].default_value = pyvnt_node.give_val()
    elif isinstance(pyvnt_node, Vector_P):
        print(f"Setting up Vector_P node with values: x={pyvnt_node._Vector_P__x.give_val()}, y={pyvnt_node._Vector_P__y.give_val()}, z={pyvnt_node._Vector_P__z.give_val()}")
        blender_node.x = pyvnt_node._Vector_P__x.give_val()
        blender_node.y = pyvnt_node._Vector_P__y.give_val()
        blender_node.z = pyvnt_node._Vector_P__z.give_val()
    elif isinstance(pyvnt_node, Dim_Set_P):
        print(f"Setting up Dim_Set_P node with value: {pyvnt_node.give_val()}")
        blender_node.outputs['Dimention Set'].default_value = pyvnt_node.give_val()
    elif isinstance(pyvnt_node, Key_C):
        print(f"Setting up Key_C node with value: {pyvnt_node.give_val()}")
        blender_node.name = pyvnt_node.name

def create_value_node(node_tree, value, name, location, parent_frame=None):
    """Create a value node based on the value type"""
    print(f"\nCreating value node for {name} with value: {value}")
    
    # Get the next available y-position at this x-coordinate
    x_pos, y_pos = location
    y_pos = get_next_y_position(x_pos, y_pos)
    
    if isinstance(value, (Int_P, Flt_P, Enm_P, Vector_P, Dim_Set_P)):
        if isinstance(value, Int_P):
            node = create_blender_node(node_tree, 'N_Int_P', f"{name}_value", (x_pos, y_pos), parent_frame)
            node.outputs['Value'].default_value = value.give_val()
            node.minimum = value._Int_P__minimum
            node.maximum = value._Int_P__maximum
        elif isinstance(value, Flt_P):
            node = create_blender_node(node_tree, 'N_Flt_P', f"{name}_value", (x_pos, y_pos), parent_frame)
            node.outputs['Value'].default_value = value.give_val()
            node.minimum = value._Flt_P__minimum
            node.maximum = value._Flt_P__maximum
        elif isinstance(value, Enm_P):
            node = create_blender_node(node_tree, 'N_Str_P', f"{name}_value", (x_pos, y_pos), parent_frame)
            # node.outputs['Value'].default_value = value.give_val()
            # print("fghyu"+str(value))
            node.default = value.give_val()
        elif isinstance(value, Vector_P):
            node = create_blender_node(node_tree, 'N_Vec_P', f"{name}_value", (x_pos, y_pos), parent_frame)
            node.x = value._Vector_P__x.give_val()
            node.y = value._Vector_P__y.give_val()
            node.z = value._Vector_P__z.give_val()
        elif isinstance(value, Dim_Set_P):
            node = create_blender_node(node_tree, 'N_Dim_P', f"{name}_value", (x_pos, y_pos), parent_frame)
            print(f"Setting Dimention Set for {name} to {value.give_val()}")
            node.m,node.l,node.t,node.temp,node.mol,node.c,node.li = value.give_val()
        
        update_last_y_position(x_pos, y_pos)
        
        return node
    
    return None

def process_key_c_value(node_tree, value, name, x_pos, y_pos, parent_node, parent_frame=None):
    """Process a single value from a Key_C node recursively"""
    print(f"Processing value: {name} = {value}")
    
    # Get the next available y-position at this x-coordinate
    y_pos = get_next_y_position(x_pos, y_pos)
    
    if isinstance(value, (List_CP, Node_C)):
        child_x = x_pos + LEVEL_X_SPACING
        child_node = create_nodes_recursive(value, node_tree, parent_frame, child_x, y_pos, parent_node)
        update_last_y_position(x_pos, y_pos)
        
        return child_node
    elif isinstance(value, (Int_P, Flt_P, Str_P, Vector_P, Dim_Set_P, Enm_P)):
        child_x = x_pos + LEVEL_X_SPACING
        value_node = create_value_node(node_tree, value, name, (child_x, y_pos), parent_frame)
        update_last_y_position(x_pos, y_pos)
        return value_node
    else:
        child_x = x_pos + LEVEL_X_SPACING
        value_node = create_value_node(node_tree, value, name, (child_x, y_pos), parent_frame)
        update_last_y_position(x_pos, y_pos)
        return value_node

def set_node_list(blender_node, pyvnt_node, node_tree, x_pos, current_y):
    """
    Set up properties and children for a node list
    
    Args:
        blender_node: The Blender node to set up
        pyvnt_node: The PyVNT node 
        node_tree: The node tree to add nodes to
        x_pos: X position for child nodes
        current_y: Y position for child nodes
    """
    # setup_node_properties(blender_node, pyvnt_node)
    
    if isinstance(pyvnt_node, (Node_C, List_CP)):
        if isinstance(pyvnt_node, Node_C):
            print(f"Processing data items for Node_C: {pyvnt_node.name}")
            child_x = x_pos + LEVEL_X_SPACING
            for data_item in pyvnt_node.get_ordered_items():
                print(f"Processing data item: {data_item.name}")
                child_y = get_next_y_position(child_x, current_y)
                child_node = create_nodes_recursive(
                    data_item, node_tree, blender_node, child_x, child_y, blender_node
                )
                if child_node:
                    update_last_y_position(child_x, child_y)
        
        elif isinstance(pyvnt_node, List_CP):
            if not pyvnt_node.is_a_node():
                print(f"Processing data for list {pyvnt_node._Value_P__name}")
                data = pyvnt_node.get_elems()
                child_x = x_pos + LEVEL_X_SPACING
                for elems in data:
                    for child in elems:
                        # Get the next available y-position at this x
                        child_y = get_next_y_position(child_x, current_y)
                        child_node = create_nodes_recursive(
                            child, node_tree, blender_node, child_x, child_y, blender_node
                        )
                        if child_node:
                            update_last_y_position(child_x, child_y)

            child_x = x_pos + LEVEL_X_SPACING
            
            for child in pyvnt_node.children:
                child_y = get_next_y_position(child_x, current_y)
                child_node = create_nodes_recursive(
                    child, node_tree, blender_node, child_x, child_y, blender_node
                )
                # Update the last used y-position
                if child_node:
                    update_last_y_position(child_x, child_y)

def create_nodes_recursive(pyvnt_node, node_tree, parent_frame=None, x_pos=0, y_pos=0, parent_node=None):
    """
    Recursively create Blender nodes from PyVNT nodes
    """
    # print(f"\nCreating node for {pyvnt_node.__class__.__name__} with name: {pyvnt_node.name} at ({x_pos}, {y_pos})")
    # Get the next available y-position at this x-coordinate
    y_pos = get_next_y_position(x_pos, y_pos)
    
    if parent_node is None:
        print(f"Parent node is None")

    blender_node = None
    if isinstance(pyvnt_node, Node_C):
        print("Creating N_Dict_C node")
        if parent_node is None:
            blender_node = create_blender_node(node_tree, 'N_OUTPUT_P', pyvnt_node.name, (x_pos, y_pos), parent_frame)
        else:
            blender_node = create_blender_node(node_tree, 'N_Dict_C', pyvnt_node.name, (x_pos, y_pos), parent_frame)

        # Update the last used y-position at this x
        update_last_y_position(x_pos, y_pos)
        
        # Connect Dict_C to parent if it exists
        if parent_node and isinstance(parent_node, bpy.types.Node):
            try:
                if parent_node.bl_idname in ['N_Dict_C','N_OUTPUT_P','N_List_CP']:
                    print(f"Connecting Dict_C node {blender_node.name} to parent dictionary {parent_node.name}")
                    node_tree.links.new(blender_node.outputs[0], parent_node.inputs[0])
                    print(f"Successfully connected {blender_node.name} to {parent_node.name}")
                
            except Exception as e:
                print(f"Failed to connect Dict_C to parent: {e}")
                
        # Set up properties and children
        set_node_list(blender_node, pyvnt_node, node_tree, x_pos, y_pos)
                
    elif isinstance(pyvnt_node, List_CP):
        print("Creating N_List_CP node")
        if pyvnt_node.is_a_node():
            blender_node = create_blender_node(node_tree, 'N_List_CP', pyvnt_node.name, (x_pos, y_pos), parent_frame)
            print(f"Creating N_List_CP node  {blender_node.name}")
            blender_node.isNode = pyvnt_node.is_a_node()
            update_last_y_position(x_pos, y_pos)
            set_node_list(blender_node, pyvnt_node, node_tree, x_pos, y_pos)
        else:
            data=pyvnt_node.get_elems()[0]
            if (len(data)>0) and (pyvnt_node.is_a_node()==False):
                if all(type(x) == type(data[0]) for x in data) and (type(data[0])) in [Int_P,Flt_P]:
                    # data_multi_node=create_value_node(node_tree, pyvnt_node, pyvnt_node._Value_P__name, (x_pos, current_y), parent_frame)
                    blender_node = create_blender_node(node_tree, 'N_MultiValue_P', f"{pyvnt_node._Value_P__name}_value", (x_pos, y_pos), parent_frame)
                    blender_node.num_values=len(data)
                    update_last_y_position(x_pos, y_pos)
                    
                    if isinstance(data[0],Int_P):
                        mm=0
                        mx=0
                        for n in data:
                            mm=min(mm,n._Int_P__minimum)
                            mx=max(mx,n._Int_P__maximum)
                        blender_node.min_value=mm
                        blender_node.max_value=mx
                        blender_node.value_type='INT'
                        for i,n in enumerate(data):
                            blender_node.inputs[i].default_value=n.give_val()   
                    elif isinstance(data[0],Flt_P):
                        mm=0
                        mx=0
                        for n in data:
                            mm=min(mm,n._Flt_P__minimum)
                            mx=max(mx,n._Flt_P__maximum)
                        blender_node.min_value=int(mm)
                        blender_node.max_value=int(mx)
                        blender_node.value_type='FLOAT'
                        for i,n in enumerate(data):
                            blender_node.inputs[i].default_value=n.give_val()
                    
                else:
                    blender_node = create_blender_node(node_tree, 'N_List_CP', pyvnt_node._Value_P__name, (x_pos, y_pos), parent_frame)
                    blender_node.isNode = pyvnt_node.is_a_node()
                    update_last_y_position(x_pos, y_pos)
                    set_node_list(blender_node, pyvnt_node, node_tree, x_pos, y_pos)
            else:
                blender_node = create_blender_node(node_tree, 'N_List_CP', pyvnt_node._Value_P__name, (x_pos, y_pos), parent_frame)
                blender_node.isNode = pyvnt_node.is_a_node()
                
                # Update the last used y-position at this x
                update_last_y_position(x_pos, y_pos)
                
                # Set up properties and children
                set_node_list(blender_node, pyvnt_node, node_tree, x_pos, y_pos)  


        if parent_node and isinstance(parent_node, bpy.types.Node):
            if blender_node.bl_idname == 'N_MultiValue_P':
                node_tree.links.new(blender_node.outputs[0], parent_node.inputs[0])
                print(f"Successfully connected {blender_node.name} to {parent_node.name}")
            else:
                try:
                    if blender_node.isNode:
                        if parent_node.bl_idname in ['N_Dict_C','N_OUTPUT_P']:
                            node_tree.links.new(blender_node.outputs[0], parent_node.inputs[0])
                    else:
                        if parent_node.bl_idname in ['N_Key_C', 'N_Dict_C','N_OUTPUT_P','N_List_CP']:
                            node_tree.links.new(blender_node.outputs[0], parent_node.inputs[0])
                except Exception as e:
                    print(f"Failed to connect List_CP to parent: {e}")
        
    elif isinstance(pyvnt_node, Key_C):
        print("Creating N_Key_C node")
        blender_node = create_blender_node(node_tree, 'N_Key_C', pyvnt_node.name, (x_pos, y_pos), parent_frame)
        update_last_y_position(x_pos, y_pos)
        
        # Process items from the Key_C node
        items = list(pyvnt_node.get_items())
        if items:
            print(f"Processing Key_C items: {items}")
            for i, (name, value) in enumerate(items):
                # Get the next y-position for this value
                value_y = get_next_y_position(x_pos, y_pos - (i * 100))
                
                value_node = process_key_c_value(node_tree, value, name, x_pos, value_y, blender_node, parent_frame)
                if value_node:
                    try:
                        node_tree.links.new(value_node.outputs[0], blender_node.inputs[0])
                        print(f"Successfully connected {value_node.name} to {blender_node.name}")
                    except Exception as e:
                        print(f"Failed to connect value node: {e}")
                    update_last_y_position(x_pos, value_y)

        # Connect Key_C to parent dictionary if it exists
        if parent_node and isinstance(parent_node, bpy.types.Node) and parent_node.bl_idname in ['N_Dict_C','N_OUTPUT_P']:
            try:
                print(f"Connecting Key_C node {blender_node.name} to parent dictionary {parent_node.name}")
                node_tree.links.new(blender_node.outputs[0], parent_node.inputs[0])
                print(f"Successfully connected {blender_node.name} to {parent_node.name}")
            except Exception as e:
                print(f"Failed to connect Key_C to parent dictionary: {e}")
    
    elif isinstance(pyvnt_node, (Int_P, Flt_P, Enm_P, Vector_P, Dim_Set_P)):
        # Create value nodes directly
        blender_node = create_value_node(node_tree, pyvnt_node, pyvnt_node._Value_P__name, (x_pos, y_pos), parent_frame)

        # Connect value node to parent if it exists
        if parent_node and isinstance(parent_node, bpy.types.Node):
            try:
                print(f"Connecting value node {blender_node.name} to parent {parent_node.name}")
                node_tree.links.new(blender_node.outputs[0], parent_node.inputs[0])
                print(f"Successfully connected {blender_node.name} to {parent_node.name}")
            except Exception as e:
                print(f"Failed to connect value node to parent: {e}")
    
    return blender_node

class VENTURIAL_OT_import_file(Operator, ImportHelper):
    """Operator to import a file for the Venturial Node system"""
    bl_idname = "venturial.import_file"
    bl_label = "Import Venturial Data"
    bl_options = {'REGISTER', 'UNDO'}

    filepath: StringProperty(
        name="File Path",
        description="Path to the file to import",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    def execute(self, context):
        """Import the file and create nodes"""
        print(f"Importing file: {self.filepath}")
        
        # Reset the y-position tracking
        global last_y_position_at_x
        last_y_position_at_x = {}

        # Try to parse the file content
        try:
            with open(self.filepath, 'r') as f:
                content = f.read()
            try:
                pyvnt_node = OpenFoamParser().parse_file(content)
                print(pyvnt_node)
                show_tree(pyvnt_node)
            except Exception as parse_error:
                self.report({'ERROR'}, f"Failed to parse file: {str(parse_error)}\nAlso failed to read: {str(read_error)}")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to read file: {str(e)}")
            return {'CANCELLED'}
        
        # Get or create the node tree
        node_tree = context.space_data.node_tree
        if not node_tree:
            node_tree = bpy.data.node_groups.new("Venturial Node Tree", 'venturial.node_tree')
            context.space_data.node_tree = node_tree
        
        # Clear existing nodes
        for node in node_tree.nodes:
            node_tree.nodes.remove(node)
        
        # Start position for root node - rightmost position
        start_x = 1000
        start_y = 0
        
        # Create nodes recursively
        try:
            create_nodes_recursive(pyvnt_node, node_tree, None, start_x, start_y)
            self.report({'INFO'}, "Successfully imported node tree")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create nodes: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
