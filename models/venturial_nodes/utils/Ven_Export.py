import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty
from pyvnt import *
from ..DataConvertore import DataConvertorNodeToPyVNT

convertor = DataConvertorNodeToPyVNT()

def trace_from_head_node(head_node, parent_pyvnt=None, visited=None, node_cache=None):
    """
    Recursively build a PyVNT node tree starting from the head node,
    following input connections backward.
    
    Args:
        head_node: The Blender node to start from
        parent_pyvnt: The parent PyVNT node (None for root node)
        visited: Set of visited node IDs to prevent cycles
        node_cache: Dictionary to store created PyVNT nodes by original node ID
        
    Returns:
        PyVNT node representing this node and its children
    """
    # Initialize the cache and visited set if they're None
    if visited is None:
        visited = set()
    if node_cache is None:
        node_cache = {}

    # Using (name, bl_idname, pointer) as the unique key 
    node_key = (head_node.name, head_node.bl_idname, head_node.as_pointer())
    blender_pointer = head_node.as_pointer()

    print(f"Processing: {head_node.name} (Type: {head_node.bl_idname}, BlenderPointer: {blender_pointer})") # Log the key components

    # Check cache using node_key
    if node_key in node_cache:
        cached_node = node_cache[node_key]
        print(f"Using cached node for {node_key} (PyVNT ID: {id(cached_node)})")
        return cached_node

    # Check visited using node_key
    if node_key in visited:
        print(f"Cycle detected: Already visited {node_key}, returning None.")
        return None

    # CORE CHANGE: Add node_key to visited
    visited.add(node_key)

    # Create the appropriate PyVNT node based on node type
    current_pyvnt = None

    # Handle different node types
    if head_node.bl_idname == "N_OUTPUT_P":
        current_pyvnt = Node_C(head_node.name)
    elif head_node.bl_idname == "N_Dict_C":
        current_pyvnt = Node_C(head_node.name)
    elif head_node.bl_idname == "N_List_CP":
        # For List_CP, explicitly create a new empty list each time
        current_pyvnt = List_CP(head_node.name, isNode=head_node.isNode)
    elif head_node.bl_idname == "N_Key_C":
        current_pyvnt = Key_C(head_node.name) 
    elif head_node.bl_idname == "N_Int_P":
        current_pyvnt = convertor.convert_To_Int_C(
            head_node.name,
            head_node.outputs['Value'].default_value,
            head_node.minimum,
            head_node.maximum
        )
    elif head_node.bl_idname == "N_Flt_P":
        current_pyvnt = convertor.convert_To_Flt_C(
            head_node.name,
            head_node.outputs['Value'].default_value,
            head_node.minimum,
            head_node.maximum
        )
    elif head_node.bl_idname == "N_Str_P":
        current_pyvnt = convertor.convert_To_Str_P(
            head_node.name,
            head_node.outputs['Value'].default_value
        )
    elif head_node.bl_idname == "N_Enm_P":
        current_pyvnt = convertor.convert_To_Enm_C(
            head_node.name,
            head_node.outputs['Value'].default_value
        )
    elif head_node.bl_idname == "N_Dim_P":
        dimensions = head_node.outputs['Dimention Set'].default_value
        current_pyvnt = convertor.convert_To_Dim_Set_C(
            head_node.name,
            dimensions
        )
    elif head_node.bl_idname == "N_Vec_P":
        current_pyvnt = convertor.convert_To_VecTor_List_CP(
            head_node.name,head_node.minimum,head_node.maximum,[head_node.x,head_node.y,head_node.z]
        )
    elif head_node.bl_idname == "N_MultiValue_P":
        # Passing node.inputs as list for getting there default values
        current_pyvnt = convertor.convert_To_MultiValue_List_CP(
            head_node.name,head_node.min_value,head_node.max_value,head_node.inputs,head_node.value_type
        )
    else:
        # Trash node 
        current_pyvnt = Node_C("TRASH")

    print(f"Created PyVNT node: {head_node.name} (ID: {id(current_pyvnt)}, Type: {type(current_pyvnt).__name__})")
    
    node_cache[node_key] = current_pyvnt

    if len(head_node.inputs) > 0:
        for i, input_socket in enumerate(head_node.inputs):
            if input_socket.is_linked:
                for link in input_socket.links:
                    from_node = link.from_node
                    print(f"Processing input {i} from {from_node.name} to {head_node.name}")
                    # Pass the node_cache to maintain unique instances
                    child_pyvnt = trace_from_head_node(from_node, current_pyvnt, visited, node_cache)
                    if child_pyvnt is not None:
                        # Connect child to parent based on their types
                        if isinstance(current_pyvnt, Node_C):
                            if isinstance(child_pyvnt, Key_C):
                                current_pyvnt.add_data(child_pyvnt)
                            elif isinstance(child_pyvnt, Node_C):
                                current_pyvnt.add_child(child_pyvnt)
                            elif isinstance(child_pyvnt, List_CP) and child_pyvnt.is_a_node():
                                current_pyvnt.add_child(child_pyvnt)
                        elif isinstance(current_pyvnt, Key_C):
                            current_pyvnt.append_val(child_pyvnt._Value_P__name, child_pyvnt)
                        elif isinstance(current_pyvnt, List_CP):
                            if current_pyvnt.is_a_node():
                                current_pyvnt.append_child(child_pyvnt)
                            else:
                                current_pyvnt.append_elem([child_pyvnt])
    return current_pyvnt

def give_head_node(context):
    active_node_tree = context.space_data.node_tree
    if not active_node_tree.nodes:
        print("(Tree contains no nodes)")
        return None
    head_nodes = [n for n in active_node_tree.nodes if 
                       (hasattr(n, 'is_head_node') and n.is_head_node) or 
                       n.bl_idname == 'N_OUTPUT_P']
    return head_nodes

class VENTURIAL_OT_inspect_active_tree_structured(Operator):
    """Prints the active Venturial Node Tree structure like a file tree to the console"""
    bl_idname = "venturial.inspect_active_tree_structured"
    bl_label = "Inspect Active Venturial Tree (File Tree)"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space and space.type == 'NODE_EDITOR' and
                space.node_tree and
                hasattr(space.node_tree, 'bl_idname') and
                space.node_tree.bl_idname == 'venturial.node_tree')

    def execute(self, context):
        # First check for head node (Output node)
        head_nodes = give_head_node(context)
        if head_nodes:
            print(f"=== HEAD NODE TRACE VIEW ===")
            head_node = head_nodes[0]  # Take the first head node if multiple exist

            print(f"Starting trace from head node: {head_node.name}")

            self.pyvnt_node = trace_from_head_node(head_node) # Build the PyVNT node tree starting from the head node

            # Display the resulting node tree
            if self.pyvnt_node:
                print(f"\nPyVNT Node Structure for {head_node.name}:")
                print(self.pyvnt_node)
                show_tree(self.pyvnt_node)
                self.report({'INFO'}, "Successfully printed node tree")
            else:
                print("Failed to build PyVNT node structure")
            print("\n" + "-"*70 + "\n")

        else:
            print("No Head Node Found")
            return {'CANCELLED'}

        return {'FINISHED'}
    
class VENTURIAL_OT_export_file(Operator, ExportHelper):
    """Export the current Venturial node tree to a file"""
    bl_idname = "venturial.export_file"
    bl_label = "Export Venturial Node Tree"
    bl_options = {'REGISTER'}

    filename_ext = ".txt"

    filepath: StringProperty(
        name="File Path",
        description="Path to save the exported file",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    )
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space.type == 'NODE_EDITOR' and
                space.node_tree and
                space.node_tree.bl_idname == 'venturial.node_tree')

    def execute(self, context):
        print("Exporting node tree - calling structured tree inspector")
        head_nodes = give_head_node(context)
                       
        if head_nodes:
            print(f"=== HEAD NODE TRACE VIEW ===")
            head_node = head_nodes[0]
            print(f"Starting trace from head node: {head_node.name}")
            pyvnt_node = trace_from_head_node(head_node)
            
            # Display the resulting node tree
            if pyvnt_node:
                print(f"\nPyVNT Node Structure for {head_node.name}:")
                show_tree(pyvnt_node)
                print(self.filepath)
                writeTo( pyvnt_node,path=self.filepath)
                self.report({'INFO'}, f"Successfully written node tree at {self.filepath}")
            else:
                print("Failed to build PyVNT node structure")
            print("\n" + "-"*70 + "\n")

        else:
            print("No Head Node Found")
            return {'CANCELLED'}
        return {'FINISHED'}
