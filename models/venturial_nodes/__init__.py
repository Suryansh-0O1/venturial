import bpy
import importlib
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

from .Nodes.Node import Venturial_Node_Tree, Venturial_Node_Category
from .Nodes.Int_Node import N_Int_P
from .Nodes.Flt_Node import N_Flt_P
from .Nodes.Enm_Node import N_Enm_P
from .Nodes.Str_Node import N_Str_P
from .Nodes.Vector_Node import N_Vec_P, Vec_P_Socket
from .Nodes.Tensor_Node import N_Ten_P, Ten_P_Socket
from .Nodes.Dim_Set_Node import N_Dim_P, Dim_P_Socket
from .Nodes.Key_Node import N_Key_C, Key_C_Socket_In, Key_C_Socket_Out
from .Nodes.Dict_Node import N_Dict_C, Dict_C_Socket_In, Dict_C_Socket_Out
from .Nodes.List_Node import N_List_CP, List_CP_Socket_In, List_CP_Socket_Out
from .Nodes.Output_node import N_OUTPUT_P,Node_Socket_In,Node_Socket_Out
from .Nodes.MultiValue_Node import N_MultiValue_P, MultiValue_Socket_Out, NODE_OT_multi_value_add, NODE_OT_multi_value_remove
from .Operator.List_Operators import NODE_OT_Add_Elem, NODE_OT_Remove_Elem

from .Operator.Node_Links_Swapper import NODE_OT_move_link_order
from .utils.Ven_Import import VENTURIAL_OT_import_file
from .utils.Ven_Export import VENTURIAL_OT_export_file
from .utils.Ven_Export import VENTURIAL_OT_inspect_active_tree_structured

_draw_venturial_buttons_func = None

node_categories = [
    Venturial_Node_Category("VENTURIAL", "Venturial Nodes", items=[
        NodeItem("N_OUTPUT_P"),
        NodeItem("N_Dict_C"),
        NodeItem("N_List_CP"),
        NodeItem("N_Key_C"),
        NodeItem("N_Int_P"),
        NodeItem("N_Flt_P"),
        NodeItem("N_Str_P"),
        NodeItem("N_Enm_P"),
        NodeItem("N_Vec_P"),
        NodeItem("N_Ten_P"),
        NodeItem("N_Dim_P"),
        NodeItem("N_MultiValue_P"),
    ])
]

classes_to_register = [
    NODE_OT_move_link_order,
    NODE_OT_Add_Elem,
    NODE_OT_Remove_Elem,
    NODE_OT_multi_value_add,
    NODE_OT_multi_value_remove,
    # Node Tree
    Venturial_Node_Tree,
    # Sockets
    Vec_P_Socket,
    Ten_P_Socket,
    Dim_P_Socket,
    Key_C_Socket_In,
    Key_C_Socket_Out,
    Dict_C_Socket_In,
    Dict_C_Socket_Out,
    List_CP_Socket_In,
    List_CP_Socket_Out,
    Node_Socket_In,
    Node_Socket_Out,
    MultiValue_Socket_Out,
    # Node Implementations
    N_Int_P,
    N_Str_P,
    N_Flt_P,
    N_Enm_P,
    N_Vec_P,
    N_Ten_P,
    N_Dim_P,
    N_Key_C,
    N_Dict_C,
    N_List_CP,
    N_OUTPUT_P,
    N_MultiValue_P,
    # Import Export 
    VENTURIAL_OT_import_file,
    VENTURIAL_OT_export_file,
    VENTURIAL_OT_inspect_active_tree_structured
]

def register():
    global _draw_venturial_buttons_func
    
    try:
        from .ButtonDraw_UI_Header import draw_venturial_buttons # Import the consolidated draw function
        _draw_venturial_buttons_func = draw_venturial_buttons
        print("Successfully imported draw_venturial_buttons.")
    except ImportError as e:
        print(f"ERROR: Failed to import draw_venturial_buttons: {e}")
        _draw_venturial_buttons_func = None

    # Register operators first
    print("Registering operators...")
    try:
        print(f"Attempting to register NODE_OT_move_link_order with bl_idname: {NODE_OT_move_link_order.bl_idname}")
        bpy.utils.register_class(NODE_OT_move_link_order)
        print(f"Successfully registered NODE_OT_move_link_order")
    except Exception as e:
        print(f"Error registering NODE_OT_move_link_order: {e}")

    for cls in classes_to_register:
        if cls == NODE_OT_move_link_order:
            continue
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            pass
        except Exception as e:
            print(f"Error registering class {cls.__name__}: {e}")

    # 3. Register Node Categories
    try:
        nodeitems_utils.register_node_categories('venturial.node_tree', node_categories)
    except Exception as e:
        print(f"Error registering node categories: {e}")

    # 4. Append UI drawing functions
    if _draw_venturial_buttons_func:
        try:
            bpy.types.NODE_HT_header.append(_draw_venturial_buttons_func)
        except Exception as e:
            print(f"Error appending draw function to NODE_HT_header: {e}")
    else:
        print("Import/Export button UI function not available, skipping append.")

    print("--- Venturial Nodes Module Registered ---")

def unregister():
    global  _draw_venturial_buttons_func
    print("--- Unregistering Venturial Nodes Module ---")

    # 1. Remove UI drawing functions (if it was added)
    if _draw_venturial_buttons_func:
        try:
            bpy.types.NODE_HT_header.remove(_draw_venturial_buttons_func)
        except ValueError:
            pass # Function was not found, ignore
        except Exception as e:
            print(f"Error removing draw function from NODE_HT_header: {e}")

    # 2. Unregister Node Categories
    try:
        nodeitems_utils.unregister_node_categories('venturial.node_tree')
    except Exception as e:
        print(f"Error unregistering node categories: {e}")

    
    for cls in reversed(classes_to_register):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
        except Exception as e:
            print(f"Error unregistering class {cls.__name__}: {e}")

    _draw_venturial_buttons_func = None
    print("--- Venturial Nodes Module Unregistered ---")

