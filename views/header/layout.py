from venturial.views.header.view import (VNT_MT_file_menu, 
                                         VNT_PT_uicategory, 
                                         VNT_MT_about_venturial,
                                         VNT_MT_about_fossee,
                                         VNT_MT_help_menu)

from venturial.models.header.general_operators import VNT_OT_close_venturial
from venturial.utils.custom_icon_object_generator import *


class header_layout:
    """Class that consists of methods to define venturial's header layout"""
    
    def draw(self, layout, context):
        cs = context.scene

        # First row: File menu and tool popover
        row = layout.row(align=True)
        row.menu(VNT_MT_file_menu.bl_idname, text="File")
        row.popover(VNT_PT_uicategory.bl_idname, text=cs.current_tool_text)

        # Second row: Mode property
        row = layout.row(align=True)
        row.prop(cs, "mode", icon_only=True, expand=True)

        # Third row: Venturial and FOSSEE menus
        row = layout.row(align=True)
        row.menu(
            VNT_MT_about_venturial.bl_idname,
            text="  Venturial  ",
            icon_value=custom_icons["venturial_logo"]["venturial_logo"].icon_id
        )
        row = layout.row(align=True)
        row.menu(
            VNT_MT_about_fossee.bl_idname,
            text="  FOSSEE  ",
            icon_value=custom_icons["fossee_logo"]["fossee_logo"].icon_id
        )

class header_preset_layout:
    """Preset Class that consists of methods to define venturial's header layout"""
    
    def draw(self, layout, context):
        # Fourth row: Help menu and close operator
        row = layout.row(align=True)
        row.menu(VNT_MT_help_menu.bl_idname, text="  Help  ", icon="QUESTION")
        row = layout.row(align=True)
        row.alert = True
        row.operator(VNT_OT_close_venturial.bl_idname, text="", icon="PANEL_CLOSE")
        row.alert = False