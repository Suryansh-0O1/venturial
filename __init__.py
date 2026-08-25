bl_info = {
    "name": "Venturial",
    "description": "Parametric structured blockMesh and unstructured cfMesh generation suite.",
    "author": "Venturial Team / FOSSEE",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Venturial",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
}

import bpy
from .unstructured_classes import classes as unstructured_classes
from .classy_classes import classes as classy_classes

classes = unstructured_classes + classy_classes

def register():
    print("--- Registering Venturial GUI Suite ---")
    
    from .unstructured_classes import register_props as unstructured_register_props
    from .classy_classes import register_props as classy_register_props
    
    # Register all operator/ui classes first
    for cls in classes:
        bpy.utils.register_class(cls)
        
    # Then attach properties onto bpy.types (requires PropertyGroup classes to be registered)
    unstructured_register_props()
    classy_register_props()

def unregister():
    from .unstructured_classes import unregister_props as unstructured_unregister_props
    from .classy_classes import unregister_props as classy_unregister_props
    
    # Unregister properties first
    unstructured_unregister_props()
    classy_unregister_props()
    
    # Unregister all operator/ui classes
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"Error unregistering {cls.__name__}: {e}")

if __name__ == "__main__":
    register()
