import bpy
IMPORT_OPERATOR_IDNAME = "venturial.import_file"
EXPORT_OPERATOR_IDNAME = "venturial.export_file"


def draw_venturial_import_button(self, context):
    """Draws the 'Import Data' button in the Node Editor header 
       if the context is the Venturial Node Tree.
    """
    layout = self.layout
    space = context.space_data
    
    if space.type == 'NODE_EDITOR' and space.tree_type == 'venturial.node_tree':
        row = layout.row(align=True)
        row.operator(IMPORT_OPERATOR_IDNAME, text="Import Data", icon='IMPORT')
        print("Import button drawn")

def draw_venturial_export_button(self, context):
    """Draws the 'Export Data' button in the Node Editor header 
       if the context is the Venturial Node Tree.
    """
    layout = self.layout
    space = context.space_data
    if space.type == 'NODE_EDITOR' and space.tree_type == 'venturial.node_tree':
        row = layout.row(align=True)
        row.operator(EXPORT_OPERATOR_IDNAME, text="Export Data", icon='EXPORT')
        print("Export button drawn")

def draw_venturial_buttons(self, context):
    """Draws Import, Export, and Print Tree buttons if in the correct context."""
    layout = self.layout
    space = context.space_data
    if space.type == 'NODE_EDITOR' and space.tree_type == 'venturial.node_tree':
        row = layout.row(align=True)
        row.operator(IMPORT_OPERATOR_IDNAME, text="Import", icon='IMPORT')
        row.operator(EXPORT_OPERATOR_IDNAME, text="Export", icon='EXPORT')
        row.operator("venturial.inspect_active_tree_structured", text="Print Tree", icon='CONSOLE')
