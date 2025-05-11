import bpy
import os
from bpy.app.handlers import persistent

# Core operator imports
from venturial.models.snappyhexmesh.geometry_operators import VNT_OT_create_new_geometry, VNT_OT_delete_geometry
from venturial.models.snappyhexmesh.file_operators import VNT_OT_export_stl_geometry
from venturial.models.snappyhexmesh.dictionary_operators import VNT_OT_generate_snappyhex_dict

# Import tooltips but use a different approach for displaying them
from venturial.models.snappyhexmesh.tooltips import (
    CASTELLATED_TOOLTIPS,
    SNAP_TOOLTIPS,
    LAYER_TOOLTIPS,
    QUALITY_TOOLTIPS,
    DICTIONARY_TOOLTIPS
)

class snappyhexmesh_menu:
    """Main menu handler for SnappyHexMesh interface, providing tabbed access to all settings"""
    
    def layout(self, tools, context):
        """Main layout handler that dispatches to the appropriate tab"""
        cs = context.scene
        
        # Route to the appropriate tab method based on current selection
        tab = cs.mainpanel_categories
        if tab == "Geometry":
            self.geometry_tab(tools, context)
        elif tab in ["Castellated", "Castellation"]:
            self.castellated_tab(tools, context)
        elif tab == "Snap":
            self.snap_tab(tools, context)
        elif tab == "LayerControl":
            self.layercontrol_tab(tools, context)
        elif tab == "MeshQuality":
            self.meshquality_tab(tools, context)
        elif tab == "Dictionary":
            self.dictionary_tab(tools, context)
        else:
            # Default fallback
            self.geometry_tab(tools, context)
    
    def geometry_tab(self, tools, context):
        """Geometry import/export and management interface"""
        cs = context.scene

        # STL File section
        row = tools.row(align=True)
        row.column(align=True).label(text="Select STL File")
        row.column(align=True).prop(cs, "stl_file", text="") 
        row.column(align=True).operator("vnt.stl_browse", text="", icon='FILE_FOLDER')
        
        row = tools.row(align=True)
        row.operator("vnt.import_stl_geometry", text="Import Geometry")
        row.operator("vnt.export_stl_geometry", text="Export Current Geometry")
        
        row = tools.row(align=True)
        row.label(text="Name of STL File")
        row.prop(cs, "stl_file_name", text="")
        
        # Geometry management
        row = tools.row(align=True)
        row.column(align=True).label(text="User Defined Geometry")
        row = tools.row(align=True)
        row.column(align=True).template_list("UI_UL_list", "geometry_items", cs, "geometry_items", 
                                            cs, "geometry_items_index", rows=3)
        col_button = row.column(align=True)
        col_button.operator("vnt.create_new_geometry", text="", icon="ADD")
        col_button.operator("vnt.delete_geometry", text="", icon="REMOVE")

    def castellated_tab(self, tools, context):
        """Castellated mesh creation settings interface"""
        cs = context.scene
        box = tools.box()
        box.label(text="Castellation Options")
        
        # Master enable switch
        row = box.row()
        row.prop(cs, "castellatedMesh", text="Enable Castellated Mesh")
        
        if not cs.castellatedMesh:
            return
        
        # --- SECTION 1: GENERAL REFINEMENT PARAMETERS ---
        ref_box = tools.box()
        ref_box.label(text="Global Refinement Parameters", icon="SETTINGS")
        
        col = ref_box.column(align=True)
        
        # Cell count limits
        row = col.row()
        row.label(text="Max Local Cells:")
        row.prop(cs, "maxLocalCells", text="")
        
        row = col.row()
        row.label(text="Max Global Cells:")
        row.prop(cs, "maxGlobalCells", text="")
        
        row = col.row()
        row.label(text="Min Refinement Cells:")
        row.prop(cs, "minRefinementCells", text="")
        
        # Mesh balance
        row = col.row()
        row.label(text="Max Load Unbalance:")
        row.prop(cs, "maxLoadUnbalance", text="")
        
        # Buffer cells
        row = col.row()
        row.label(text="Cells Between Levels:")
        row.prop(cs, "nCellsBetweenLevels", text="")
        
        # --- SECTION 2: FEATURE EDGE REFINEMENT ---
        feature_box = tools.box()
        feature_box.label(text="Feature Edge Refinement", icon="EDGESEL")
        
        # Feature list 
        row = feature_box.row()
        col = row.column()
        col.template_list("CAST_UL_features_list", "", cs, "cast_features", 
                          cs, "cast_features_index", rows=2)
        
        col_buttons = row.column(align=True)
        col_buttons.operator("vnt.add_feature", text="", icon="ADD")
        col_buttons.operator("vnt.remove_feature", text="", icon="REMOVE")
        
        # Settings for selected feature
        if len(cs.cast_features) > 0 and cs.cast_features_index >= 0:
            feature = cs.cast_features[cs.cast_features_index]
            row = feature_box.row()
            row.prop(feature, "file", text="Feature Edge File")
            
            # File browser button
            browse_op = row.operator("vnt.browse_feature_file", text="", icon="FILE_FOLDER")
            browse_op.feature_index = cs.cast_features_index
            
            # Refinement levels configuration
            level_box = feature_box.box()
            level_box.label(text="Refinement Levels", icon="SORTSIZE")
            
            # Refinement mode selector
            row = level_box.row()
            row.label(text="Refinement Type:")
            row = level_box.row()
            row.prop(feature, "refinement_mode", text="")
            
            # Settings container
            input_box = level_box.box()
            
            # Mode-specific UI
            if feature.refinement_mode == 'uniform':
                row = input_box.row(align=True)
                row.label(text="Level:")
                row.prop(feature, "level", text="")
                
                syntax_box = level_box.box()
                syntax_box.label(text="Generated OpenFOAM Syntax:")
                syntax_box.label(text=f"levels (({feature.level} {feature.level}));")
                
            elif feature.refinement_mode == 'single_distance':
                col = input_box.column(align=True)
                
                row = col.row(align=True)
                row.label(text="Distance:")
                row.prop(feature, "distance", text="")
                
                row = col.row(align=True)
                row.label(text="Level:")
                row.prop(feature, "level_at_distance", text="")
                
                syntax_box = level_box.box()
                syntax_box.label(text="Generated OpenFOAM Syntax:")
                syntax_box.label(text=f"levels (({feature.distance} {feature.level_at_distance}));")
                
            else:  # multi_distance
                row = input_box.row()
                row.label(text="Multiple distance-level pairs:")
                
                # List of pairs
                row = input_box.row()
                col = row.column()
                col.template_list("CAST_UL_feature_distance_level_pairs", "", 
                                  feature, "distance_level_pairs",
                                  feature, "distance_level_pairs_index", rows=3)
                
                # Controls
                col_buttons = row.column(align=True)
                col_buttons.operator("vnt.add_feature_distance_level_pair", text="", icon="ADD")
                col_buttons.operator("vnt.remove_feature_distance_level_pair", text="", icon="REMOVE")
                
                if len(feature.distance_level_pairs) == 0:
                    input_box.operator("vnt.add_feature_distance_level_pair", 
                                       text="Add First Distance-Level Pair", icon="ADD")
                
                # Syntax preview
                syntax_box = level_box.box()
                syntax_box.label(text="Generated OpenFOAM Syntax:")
                
                if len(feature.distance_level_pairs) > 0:
                    pairs_text = " ".join([f"({p.distance} {p.level})" for p in feature.distance_level_pairs])
                    syntax_box.label(text=f"levels ({pairs_text});")
                else:
                    syntax_box.label(text="levels ();  (Empty - add pairs above)")
        
        # --- SECTION 3: SURFACE REFINEMENT ---
        surface_box = tools.box()
        surface_box.label(text="Surface Refinement", icon="SURFACE_DATA")
        
        # Global surface options
        global_options = surface_box.box()
        global_options.label(text="Global Options", icon="WORLD")
        
        # Gap Level Increment 
        row = global_options.row()
        row.prop(cs, "use_gap_level", text="Gap Level Increment")
        
        if cs.use_gap_level:
            row = global_options.row()
            row.label(text="Value:")
            row.prop(cs, "gap_level_increment", text="")
        
        # Surface list
        row = surface_box.row()
        col = row.column()
        col.template_list("CAST_UL_refinement_surfaces", "", cs, "cast_refinement_surfaces", 
                          cs, "cast_refinement_surfaces_index", rows=3)
        
        # Controls
        col_buttons = row.column(align=True)
        col_buttons.operator("vnt.add_refinement_surface", text="", icon="ADD")
        col_buttons.operator("vnt.remove_refinement_surface", text="", icon="REMOVE")
        
        # Handle empty list case
        if len(cs.cast_refinement_surfaces) == 0:
            row = surface_box.row()
            row.label(text="Add a refinement surface")
        
        # Settings for selected surface
        elif cs.cast_refinement_surfaces_index >= 0 and cs.cast_refinement_surfaces_index < len(cs.cast_refinement_surfaces):
            surface = cs.cast_refinement_surfaces[cs.cast_refinement_surfaces_index]
            
            settings_box = surface_box.box()
            
            # Source type selection
            row = settings_box.row()
            row.label(text="Source Type:")
            row.prop(surface, "source_type", text="")
            
            # Geometry-specific settings
            if surface.source_type == 'geometry':
                geom_box = settings_box.box()
                geom_box.label(text="Geometry Settings", icon="MESH_DATA")
                
                # Object selection
                row = geom_box.row()
                row.label(text="Object:")
                row.prop_search(surface, "geometry_object", cs, "geometry_items", text="")
                
                if len(cs.geometry_items) == 0:
                    row = geom_box.row()
                    row.operator("vnt.create_new_geometry", text="Create Geometry", icon="ADD")
                
                # Refinement levels
                row = geom_box.row(align=True)
                row.label(text="Refinement Level:")
                row.prop(surface, "min_level", text="Min")
                row.prop(surface, "max_level", text="Max")
                
                # Zone settings
                zone_box = geom_box.box()
                zone_box.label(text="Zones", icon="OBJECT_DATA")
                
                row = zone_box.row()
                row.label(text="Face Zone:")
                row.prop(surface, "face_zone", text="")
                
                row = zone_box.row()
                row.label(text="Cell Zone:")
                row.prop(surface, "cell_zone", text="")
                
                if surface.face_zone or surface.cell_zone:
                    row = zone_box.row()
                    row.label(text="Cell Zone Inside:")
                    row.prop(surface, "cell_zone_inside", text="")
            
            # STL-specific settings
            else:  # STL source
                stl_box = settings_box.box()
                stl_box.label(text="STL Settings", icon="FILE_3D")
                
                # Name
                row = stl_box.row()
                row.label(text="Name:")
                row.prop(surface, "name", text="")
                
                # Refinement levels
                row = stl_box.row(align=True)
                row.label(text="Refinement Level:")
                row.prop(surface, "min_level", text="Min")
                row.prop(surface, "max_level", text="")
                
                # Region settings for STL
                region_box = stl_box.box()
                region_box.label(text="Surface Regions", icon="MOD_EDGESPLIT")
                
                # Region list
                row = region_box.row()
                col = row.column()
                col.template_list("CAST_UL_surface_regions", "", surface, "regions", 
                              surface, "regions_index", rows=3)
                
                # Controls
                col_buttons = row.column(align=True)
                col_buttons.operator("vnt.add_surface_region", text="", icon="ADD")
                if len(surface.regions) > 0:
                    col_buttons.operator("vnt.remove_surface_region", text="", icon="REMOVE")
                
                # Selected region settings
                if len(surface.regions) > 0 and surface.regions_index >= 0 and surface.regions_index < len(surface.regions):
                    region = surface.regions[surface.regions_index]
                    
                    region_panel = region_box.box()
                    region_panel.label(text=f"Region: {region.name}", icon="TOOL_SETTINGS")
                    
                    # Basic settings
                    name_row = region_panel.row(align=True)
                    name_row.label(text="Name:")
                    name_row.prop(region, "name", text="")
                    
                    level_row = region_panel.row(align=True)
                    level_row.label(text="Refinement Levels:")
                    level_row.prop(region, "min_level", text="Min")
                    level_row.prop(region, "max_level", text="")
                    
                    # Patch settings
                    patch_row = region_panel.row()
                    patch_row.prop(region, "use_patch_info", text="Use Patch Info", icon="MATERIAL")
                    
                    if region.use_patch_info:
                        patch_box = region_panel.box()
                        
                        type_row = patch_box.row(align=True)
                        type_row.label(text="Type:")
                        type_row.prop(region.patch_info, "patch_type", text="")
                        
                        if region.patch_info.patch_type not in ['empty', 'wedge']:
                            group_row = patch_box.row(align=True)
                            group_row.label(text="Group:")
                            group_row.prop(region.patch_info, "in_group", text="")
                else:
                    help_row = region_box.row()
                    help_row.label(text="No regions defined - click '+' to add regions", icon="INFO")
        
        # --- SECTION 4: FEATURE ANGLE SETTINGS ---
        feature_angle_box = tools.box()
        feature_angle_box.label(text="Feature Angle Settings", icon="MOD_BEVEL")
        
        row = feature_angle_box.row(align=True)
        row.label(text="Resolve Feature Angle:")
        row.prop(cs, "resolveFeatureAngle", text="")
        
        row = feature_angle_box.row(align=True)
        row.label(text="Planar Angle:")
        row.prop(cs, "planarAngle", text="")
        
        # --- SECTION 5: REGION REFINEMENT ---
        region_refine_box = tools.box()
        region_refine_box.label(text="Region Refinement", icon="MESH_CUBE")
        
        # Region list
        row = region_refine_box.row()
        col = row.column()
        col.template_list("CAST_UL_refinement_regions", "", cs, "cast_refinement_regions", 
                          cs, "cast_refinement_regions_index", rows=3)
        
        # Controls
        col_buttons = row.column(align=True)
        col_buttons.operator("vnt.add_refinement_region", text="", icon="ADD")
        col_buttons.operator("vnt.remove_refinement_region", text="", icon="REMOVE")
        
        # Selected region settings
        if len(cs.cast_refinement_regions) > 0 and cs.cast_refinement_regions_index >= 0 and cs.cast_refinement_regions_index < len(cs.cast_refinement_regions):
            region = cs.cast_refinement_regions[cs.cast_refinement_regions_index]
            
            region_settings = region_refine_box.box()
            region_settings.label(text=f"Region: {region.name}", icon="TOOL_SETTINGS")
            
            # Basic settings
            row = region_settings.row()
            row.label(text="Name:")
            row.prop(region, "name", text="")
            
            # Source type settings
            row = region_settings.row()
            row.label(text="Source Type:")
            row.prop(region, "source_type", text="")
            
            if region.source_type == 'geometry':
                row = region_settings.row()
                row.label(text="Object:")
                row.prop_search(region, "geometry_object", cs, "geometry_items", text="")
                
                if len(cs.geometry_items) == 0:
                    row = region_settings.row()
                    row.operator("vnt.create_new_geometry", text="Create Geometry", icon="ADD")
            
            # Refinement mode settings
            row = region_settings.row()
            row.label(text="Mode:")
            row.prop(region, "mode", text="")
            
            # Level settings based on mode
            level_box = region_settings.box()
            level_box.label(text="Refinement Levels", icon="SORTSIZE")
            
            if region.mode == 'inside':
                row = level_box.row()
                row.label(text="Level:")
                row.prop(region, "level", text="")
            else:  # distance mode
                row = level_box.row()
                row.label(text="Use multiple distances:")
                row.prop(region, "use_advanced_distance", text="")
                
                if region.use_advanced_distance:
                    row = level_box.row()
                    col = row.column()
                    col.template_list("CAST_UL_distance_level_pairs", "", region, "distance_level_pairs", 
                                     region, "distance_level_pairs_index", rows=3)
                    
                    # Controls
                    col_buttons = row.column(align=True)
                    col_buttons.operator("vnt.add_distance_level_pair", text="", icon="ADD")
                    col_buttons.operator("vnt.remove_distance_level_pair", text="", icon="REMOVE")
                    
                    if len(region.distance_level_pairs) == 0:
                        row = level_box.row()
                        row.operator("vnt.add_distance_level_pair", text="Add First Distance-Level Pair", icon="ADD")
                else:
                    row = level_box.row(align=True)
                    row.label(text="Distance:")
                    row.prop(region, "distance", text="")
                    
                    row = level_box.row(align=True)
                    row.label(text="Level:")
                    row.prop(region, "level_at_distance", text="")
        elif len(cs.cast_refinement_regions) == 0:
            row = region_refine_box.row()
            row.label(text="No refinement regions defined - click '+' to add", icon="INFO")
        
        # --- SECTION 6: MESH SELECTION ---
        mesh_sel_box = tools.box()
        mesh_sel_box.label(text="Mesh Selection", icon="ORIENTATION_CURSOR")
        
        # Location in mesh
        row = mesh_sel_box.row()
        row.label(text="Location In Mesh:")
        
        coords_row = mesh_sel_box.row(align=True)
        coords_row.prop(cs, "locationInMeshX", text="X")
        coords_row.prop(cs, "locationInMeshY", text="Y")
        coords_row.prop(cs, "locationInMeshZ", text="Z")
        
        # Zone face setting
        row = mesh_sel_box.row()
        row.prop(cs, "allowFreeStandingZoneFaces", text="Allow Free Standing Zone Faces")
        
        # Advanced Options
        advanced_box = mesh_sel_box.box()
        advanced_box.label(text="Advanced Options", icon="PREFERENCES")
        
        row = advanced_box.row()
        row.prop(cs, "handleSnapProblems", text="Handle Snap Problems")
        
        row = advanced_box.row()
        row.prop(cs, "useTopologicalSnapDetection", text="Use Topological Snap Detection")

    def snap_tab(self, tools, context):
        """Snap settings interface"""
        cs = context.scene
        box = tools.box()
        box.label(text="Snap Settings")
        
        row = box.row()
        row.prop(cs, "snap", text="Enable Snap")
        
        if cs.snap:
            # Snap control settings
            box_settings = tools.box()
            box_settings.label(text="Snap Controls", icon="SNAP_ON")
            
            # Basic controls
            col = box_settings.column(align=True)
            
            # Tolerance
            row = col.row()
            row.label(text="Tolerance")
            row.prop(cs, "tolerance", text="")
            
            # Continue adding tooltips to other snap controls
            # ...existing code...

    def layercontrol_tab(self, tools, context):
        """Layer addition settings interface"""
        cs = context.scene
        box = tools.box()
        box.label(text="Layer Addition Settings")
        
        row = box.row()
        row.prop(cs, "addLayers", text="Enable Layer Addition")
        
        # Continue adding tooltips to layer settings
        # ...existing code...

    def meshquality_tab(self, tools, context):
        """Mesh quality settings interface"""
        cs = context.scene
        box = tools.box()
        box.label(text="Mesh Quality Settings")
        
        include_box = tools.box()
        include_box.label(text="Mesh Quality Dictionary", icon="FILE_TEXT")
        row = include_box.row()
        row.prop(cs, "includeMeshQualityDict", text="Include External Mesh Quality Dictionary")
        
        # Continue adding tooltips to quality settings
        # ...existing code...

    def dictionary_tab(self, tools, context):
        """Dictionary generation settings interface"""
        cs = context.scene
        box = tools.box()
        box.label(text="Dictionary Controls")
        
        # Add tooltips to dictionary settings
        # ...existing code...

@persistent
def clean_geometry_items(dummy):
    scene = bpy.context.scene
    items = scene.geometry_items
    for i in range(len(items) - 1, -1, -1):
        if not bpy.data.objects.get(items[i].name):
            items.remove(i)

if clean_geometry_items not in bpy.app.handlers.depsgraph_update_post:
    bpy.app.handlers.depsgraph_update_post.append(clean_geometry_items)

