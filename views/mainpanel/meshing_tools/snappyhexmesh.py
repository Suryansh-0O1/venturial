class snappyhexmesh_menu:

    def layout(self, tools, context):
        cs = context.scene
        row = tools.row(align=True)
        col_label = row.column(align=True)
        col_label.label(text="Select STL File")
        
        col_prop = row.column(align=True)
         
        col_prop.prop(cs, "stl_file", text="") 
        
        col_button = row.column(align=True)
        col_button.operator("vnt.stl_browse", text="", icon='FILE_FOLDER')
        
        row2 = tools.row(align=True)
        row2.operator("vnt.import_stl_geometry", text="Import Geometry")