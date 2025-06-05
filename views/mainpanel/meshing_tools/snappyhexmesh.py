import bpy
import os
from bpy.app.handlers import persistent

from venturial.models.snappyhexmesh.geometry_operators import VNT_OT_create_new_geometry, VNT_OT_delete_geometry
from venturial.models.snappyhexmesh.file_operators import VNT_OT_export_stl_geometry
from venturial.models.snappyhexmesh.dictionary_operators import VNT_OT_generate_snappyhex_dict
from venturial.models.snappyhexmesh.dictionary_writers import (
    generate_geometry_subdictionary,
    generate_castellated_subdictionary,
    generate_snap_subdictionary,
    generate_layer_subdictionary,
    generate_quality_subdictionary,
    generate_dictionary_controls_subdictionary,
    format_lines_for_preview
)

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
        
        # Tab selection row
        row = tools.row(align=True)
        row.scale_y = 1.2
        row.prop(cs, "geometry_tab", expand=True)
        
        tools.separator(factor=0.5)
        
        # Display the selected tab
        if cs.geometry_tab == 'DEFINE':
            self.geometry_define_tab(tools, context)
        elif cs.geometry_tab == 'PREVIEW':
            self.geometry_preview_tab(tools, context)
    
    def geometry_define_tab(self, tools, context):
        """Definition interface for geometry import/export and management"""
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
        
        # STL Regions section - only show if STL is imported
        if cs.stl_file_name:
            regions_box = tools.box()
            regions_header = regions_box.row()
            regions_header.label(text="STL Regions", icon="OUTLINER_OB_SURFACE")
            # Removed the duplicate add button from header
            
            row = regions_box.row()
            row.template_list("STL_UL_regions", "", cs, "stl_regions", 
                            cs, "stl_regions_index", rows=3)
            col_buttons = row.column(align=True)
            col_buttons.operator("vnt.add_stl_region", text="", icon="ADD")
            col_buttons.operator("vnt.remove_stl_region", text="", icon="REMOVE")
            
            # Show help text if no regions
            if len(cs.stl_regions) == 0:
                regions_box.label(text="Add regions to map STL surface regions to custom names", icon="INFO")
                regions_box.label(text="These regions can be used for specific refinements later")
        
        # Geometry management
        row = tools.row(align=True)
        row.column(align=True).label(text="User Defined Geometry")
        row = tools.row(align=True)
        row.column(align=True).template_list("UI_UL_list", "geometry_items", cs, "geometry_items", 
                                            cs, "geometry_items_index", rows=3)
        col_button = row.column(align=True)
        col_button.operator("vnt.create_new_geometry", text="", icon="ADD")
        col_button.operator("vnt.delete_geometry", text="", icon="REMOVE")

    def geometry_preview_tab(self, tools, context):
        """Preview tab for geometry dictionary settings"""
        cs = context.scene
        
        preview_box = tools.box()
        preview_box.label(text="Geometry Dictionary Preview", icon="TEXT")
        
        # Use dictionary writer to generate preview
        lines = generate_geometry_subdictionary(cs)
        lines = format_lines_for_preview(lines)
        
        # Display the preview lines in the UI
        col = preview_box.column()
        col.scale_y = 0.85
        for line in lines:
            col.label(text=line)
        
        # Show usage note if no geometry is defined
        if len(cs.geometry_items) == 0:
            note_box = tools.box()
            note_box.label(text="Note: No geometry objects defined", icon="INFO")
            row = note_box.row()
            row.alignment = 'CENTER'
            row.label(text="Go to 'Define' tab and add geometry objects")

    def castellated_tab(self, tools, context):
        """Castellated mesh creation settings interface with tabs for better organization"""
        cs = context.scene
        box = tools.box()
        box.label(text="Castellation Options")
        
        # Master enable switch
        row = box.row()
        row.prop(cs, "castellatedMesh", text="Enable Castellated Mesh")
        
        if not cs.castellatedMesh:
            return
        
        row = tools.row(align=True)
        row.scale_y = 1.2
        row.prop(cs, "castellated_tab", expand=True)
        
        tools.separator(factor=0.5)
        
        # Display the selected tab
        if cs.castellated_tab == 'GENERAL':
            self.castellated_general_tab(tools, context)
        elif cs.castellated_tab == 'FEATURES':
            self.castellated_features_tab(tools, context)
        elif cs.castellated_tab == 'SURFACES':
            self.castellated_surfaces_tab(tools, context)
        elif cs.castellated_tab == 'REGIONS':
            self.castellated_regions_tab(tools, context)
        elif cs.castellated_tab == 'ADVANCED':
            self.castellated_advanced_tab(tools, context)
        elif cs.castellated_tab == 'PREVIEW':
            self.castellated_preview_tab(tools, context)
    
    def castellated_general_tab(self, tools, context):
        """General settings tab for castellated mesh"""
        cs = context.scene
        
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

    def castellated_features_tab(self, tools, context):
        """Feature edge refinement tab for castellated mesh"""
        cs = context.scene
        
        feature_box = tools.box()
        feature_box.label(text="Feature Edge Refinement", icon="EDGESEL")
        
        # Feature list 
        row = feature_box.row()
        col = row.column()
        col.template_list("CAST_UL_features_list", "", cs, "cast_features", 
                          cs, "cast_features_index", rows=3)
        
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
        else:
            info_row = feature_box.row()
            info_row.alignment = 'CENTER'
            info_row.label(text="No features defined. Click '+' to add feature edges.", icon="INFO")
    
    def castellated_surfaces_tab(self, tools, context):
        """Surface refinement tab for castellated mesh"""
        cs = context.scene
        
        # --- SECTION: SURFACE REFINEMENT ---
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

    def castellated_regions_tab(self, tools, context):
        """Region refinement tab for castellated mesh"""
        cs = context.scene
        
        # --- SECTION: REGION REFINEMENT ---
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

    def castellated_advanced_tab(self, tools, context):
        """Advanced settings tab for castellated mesh"""
        cs = context.scene
        
        # --- SECTION 1: FEATURE ANGLE SETTINGS ---
        feature_angle_box = tools.box()
        feature_angle_box.label(text="Feature Angle Settings", icon="MOD_BEVEL")
        
        row = feature_angle_box.row(align=True)
        row.label(text="Resolve Feature Angle:")
        row.prop(cs, "resolveFeatureAngle", text="")
        
        row = feature_angle_box.row(align=True)
        row.label(text="Planar Angle:")
        row.prop(cs, "planarAngle", text="")
        
        # --- SECTION 2: MESH SELECTION ---
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
    
    def castellated_preview_tab(self, tools, context):
        """Preview tab showing the generated castellated mesh dictionary"""
        cs = context.scene
        
        preview_box = tools.box()
        preview_box.label(text="Dictionary Preview", icon="TEXT")
        
        # Use dictionary writer to generate preview
        lines = generate_castellated_subdictionary(cs)
        lines = format_lines_for_preview(lines)
        
        # Create a scrollable area for the preview
        preview_col = preview_box.column()
        preview_col.scale_y = 0.85
        
        for line in lines:
            preview_col.label(text=line)

    def snap_tab(self, tools, context):
        """Snap settings interface with tabs for better organization"""
        cs = context.scene
        
        # Master enable switch with icon
        box = tools.box()
        title_row = box.row()
        title_row.label(text="Snap Controls", icon="SNAP_ON")
        
        master_row = box.row()
        master_row.prop(cs, "snap", text="Enable Surface Snapping")
        
        if not cs.snap:
            info_row = box.row()
            info_row.alignment = 'CENTER'
            info_row.label(text="Surface snapping is disabled", icon="INFO")
            return
        
        row = tools.row(align=True)
        row.scale_y = 1.2
        row.prop(cs, "snap_tab", expand=True)
        
        tools.separator(factor=0.5)
        
        # Display the selected tab
        if cs.snap_tab == 'BASIC':
            self.snap_basic_tab(tools, context)
        elif cs.snap_tab == 'FEATURES':
            self.snap_features_tab(tools, context)
        elif cs.snap_tab == 'PREVIEW':
            self.snap_preview_tab(tools, context)
    
    def snap_basic_tab(self, tools, context):
        """Basic snap settings tab"""
        cs = context.scene
        
        # Basic snapping parameters section
        basic_box = tools.box()
        basic_box.label(text="Basic Snapping Parameters", icon="SETTINGS")
        
        # Smooth Patch
        row = basic_box.row(align=True)
        row.label(text="Smooth Patch Iterations:")
        row.prop(cs, "nSmoothPatch", text="")
        
        # Tolerance
        row = basic_box.row(align=True)
        row.label(text="Tolerance:")
        row.prop(cs, "tolerance", text="")
        
        # Solve Iterations
        row = basic_box.row(align=True)
        row.label(text="Solve Iterations:")
        row.prop(cs, "nSolveIter", text="")
        
        # Relax Iterations
        row = basic_box.row(align=True)
        row.label(text="Relax Iterations:")
        row.prop(cs, "nRelaxIter", text="")
        
    def snap_features_tab(self, tools, context):
        """Feature snapping settings tab"""
        cs = context.scene
        
        # Feature snapping section
        feature_box = tools.box()
        feature_box.label(text="Feature Edge Snapping", icon="EDGESEL")
        
        # Feature snapping toggle
        row = feature_box.row()
        row.prop(cs, "useFeatureSnap", text="Enable Feature Edge Snapping")
        
        # Feature snapping options - only show if enabled
        if cs.useFeatureSnap:
            # Feature Snap Iterations
            row = feature_box.row(align=True)
            row.label(text="Feature Snap Iterations:")
            row.prop(cs, "nFeatureSnapIter", text="")
            
            # Feature detection methods - in a sub-box for clarity
            methods_box = feature_box.box()
            methods_box.label(text="Feature Detection Methods", icon="OUTLINER_OB_LIGHTPROBE")
            
            # Implicit Feature Snap
            row = methods_box.row()
            row.prop(cs, "implicitFeatureSnap", 
                    text="Implicit Feature Detection (sample surface)")
            
            # Explicit Feature Snap
            row = methods_box.row()
            row.prop(cs, "explicitFeatureSnap", 
                    text="Explicit Feature Detection (use defined features)")
            
            # Multi-region Feature Snap
            row = methods_box.row()
            row.prop(cs, "multiRegionFeatureSnap", 
                    text="Multi-region Feature Detection")
    
    def snap_preview_tab(self, tools, context):
        """Preview tab for snap settings"""
        cs = context.scene
        
        preview_box = tools.box()
        preview_box.label(text="Generated OpenFOAM Syntax Preview", icon="TEXT")
        
        # Use dictionary writer to generate preview
        lines = generate_snap_subdictionary(cs)
        lines = format_lines_for_preview(lines)
        
        # Preview content
        col = preview_box.column()
        col.scale_y = 0.85
        
        for line in lines:
            col.label(text=line)

    def layercontrol_tab(self, tools, context):
        """Layer addition settings interface with tabs for better organization"""
        cs = context.scene
        
        # Master enable switch with icon
        box = tools.box()
        title_row = box.row()
        title_row.label(text="Layer Addition Controls", icon="MESH_DATA")
        
        master_row = box.row()
        master_row.prop(cs, "addLayers", text="Enable Layer Addition")
        
        # Return early if layers are disabled
        if not cs.addLayers:
            info_row = box.row()
            info_row.alignment = 'CENTER'
            info_row.label(text="Layer addition is disabled", icon="INFO")
            return
            
        row = tools.row(align=True)
        row.scale_y = 1.2 
        row.prop(cs, "layer_tab", expand=True)
        
        tools.separator(factor=0.5)
        
        # Display the selected tab
        if cs.layer_tab == 'BASIC':
            self.layer_basic_tab(tools, context)
        elif cs.layer_tab == 'FEATURES':
            self.layer_features_tab(tools, context)
        elif cs.layer_tab == 'PATCHES':
            self.layer_patches_tab(tools, context)
        elif cs.layer_tab == 'ADVANCED':
            self.layer_advanced_tab(tools, context)
        elif cs.layer_tab == 'PREVIEW':
            self.layer_preview_tab(tools, context)
    
    def layer_basic_tab(self, tools, context):
        """Basic layer addition settings tab"""
        cs = context.scene
        
        basic_box = tools.box()
        basic_box.label(text="Basic Layer Parameters", icon="SETTINGS")
        
        # Global sizing control
        row = basic_box.row()
        row.prop(cs, "relativeSizes", text="Use Relative Sizes")
        
        # Layer thickness specification method
        row = basic_box.row()
        row.label(text="Thickness Specification Method:")
        row = basic_box.row()
        row.prop(cs, "thickness_mode", text="")
        
        # Layer thickness parameters in an organized grid
        params_box = basic_box.box()
        params_box.label(text="Layer Thickness Parameters")
        grid = params_box.grid_flow(row_major=True, columns=2, even_columns=True)
        
        # Show only parameters relevant to selected thickness mode
        if 'expansion' in cs.thickness_mode:
            row = grid.row(align=True)
            row.label(text="Expansion Ratio:")
            row.prop(cs, "expansionRatio", text="")
        
        if 'overall' in cs.thickness_mode:
            row = grid.row(align=True)
            row.label(text="Overall Thickness:")
            row.prop(cs, "overallThickness", text="")
        
        if 'final' in cs.thickness_mode:
            row = grid.row(align=True)
            row.label(text="Final Layer Thickness:")
            row.prop(cs, "finalLayerThickness", text="")
        
        if 'first' in cs.thickness_mode:
            row = grid.row(align=True)
            row.label(text="First Layer Thickness:")
            row.prop(cs, "firstLayerThickness", text="")
        
        # Always show minimum thickness control
        row = grid.row(align=True)
        row.label(text="Minimum Thickness:")
        row.prop(cs, "minThickness", text="")
    
    def layer_features_tab(self, tools, context):
        """Feature handling for layer addition"""
        cs = context.scene
        
        feature_box = tools.box()
        feature_box.label(text="Feature Handling", icon="EDGESEL")
        
        # Feature controls in a grid layout
        grid = feature_box.grid_flow(row_major=True, columns=2, even_columns=True)
        
        row = grid.row(align=True)
        row.label(text="Feature Angle:")
        row.prop(cs, "featureAngle", text="")
        
        row = grid.row(align=True)
        row.label(text="Growth Layers:")
        row.prop(cs, "nGrow", text="")
        
        # Special feature handling options
        row = feature_box.row()
        row.prop(cs, "detectExtrusionIsland", text="Detect Extrusion Islands")
    
    def layer_patches_tab(self, tools, context):
        """Patch-specific layer settings tab"""
        cs = context.scene
        
        patches_box = tools.box()
        patches_header = patches_box.row(align=True)
        patches_header.label(text="Patch-Specific Settings", icon="SURFACE_DATA")
        patches_header.operator("vnt.import_boundary_patches", text="Import Boundaries", icon="IMPORT")
        
        # Patches list with controls
        row = patches_box.row()
        col = row.column()
        col.template_list("LAYER_UL_patches_list", "", cs, "layer_patches", 
                         cs, "layer_patches_index", rows=3)
        
        # List operations
        col_buttons = row.column(align=True)
        col_buttons.operator("vnt.add_layer_patch", text="", icon="ADD")
        col_buttons.operator("vnt.remove_layer_patch", text="", icon="REMOVE")
        col_buttons.separator()
        col_buttons.operator("vnt.duplicate_layer_patch", text="", icon="DUPLICATE")
        
        # Settings for selected patch
        if len(cs.layer_patches) > 0 and cs.layer_patches_index >= 0 and cs.layer_patches_index < len(cs.layer_patches):
            patch = cs.layer_patches[cs.layer_patches_index]
            
            # Patch settings container
            settings_box = patches_box.box()
            settings_box.label(text=f"Settings for: {patch.name}")
            
            # Basic patch settings
            grid = settings_box.grid_flow(row_major=True, columns=2, even_columns=True)
            row = grid.row(align=True)
            row.label(text="Surface Layers:")
            row.prop(patch, "nSurfaceLayers", text="")
            
            # Custom expansion settings
            row = settings_box.row()
            row.prop(patch, "custom_expansion", text="Custom Expansion Settings")
            
            if patch.custom_expansion:
                grid = settings_box.grid_flow(row_major=True, columns=2, even_columns=True)
                
                row = grid.row(align=True)
                row.label(text="Expansion Ratio:")
                row.prop(patch, "expansionRatio", text="")
                
                row = grid.row(align=True)
                row.label(text="Final Layer Thickness:")
                row.prop(patch, "finalLayerThickness", text="")
                
                row = grid.row(align=True)
                row.label(text="Minimum Thickness:")
                row.prop(patch, "minThickness", text="")
        else:
            # Help message when no patches are selected
            row = patches_box.row()
            row.label(text="Add patches using the + button", icon="INFO")
    
    def layer_advanced_tab(self, tools, context):
        """Advanced layer addition settings"""
        cs = context.scene
        
        adv_box = tools.box()
        adv_box.label(text="Advanced Settings", icon="TOOL_SETTINGS")
        
        # Quality controls in grid layout
        quality_grid = adv_box.grid_flow(row_major=True, columns=2, even_columns=True)
        
        row = quality_grid.row(align=True)
        row.label(text="Max Face Thickness Ratio:")
        row.prop(cs, "maxFaceThicknessRatio", text="")
        
        row = quality_grid.row(align=True)
        row.label(text="Surface Normal Smoothing:")
        row.prop(cs, "nSmoothSurfaceNormals", text="")
        
        row = quality_grid.row(align=True)
        row.label(text="Thickness Smoothing:")
        row.prop(cs, "nSmoothThickness", text="")
        
        # Medial axis analysis settings
        medial_box = adv_box.box()
        medial_box.label(text="Medial Axis Analysis", icon="OUTLINER_OB_LIGHTPROBE")
        
        grid = medial_box.grid_flow(row_major=True, columns=2, even_columns=True)
        
        row = grid.row(align=True)
        row.label(text="Min Medial Axis Angle:")
        row.prop(cs, "minMedialAxisAngle", text="")
        
        row = grid.row(align=True)
        row.label(text="Max Thickness/Medial Ratio:")
        row.prop(cs, "maxThicknessToMedialRatio", text="")
        
        row = grid.row(align=True)
        row.label(text="Normal Smoothing:")
        row.prop(cs, "nSmoothNormals", text="")
        
        # Mesh shrinking settings
        shrink_box = adv_box.box()
        shrink_box.label(text="Mesh Shrinking", icon="FULLSCREEN_ENTER")
        
        grid = shrink_box.grid_flow(row_major=True, columns=2, even_columns=True)
        
        row = grid.row(align=True)
        row.label(text="Slip Feature Angle:")
        row.prop(cs, "slipFeatureAngle", text="")
        
        row = grid.row(align=True)
        row.label(text="Relaxation Iterations:")
        row.prop(cs, "nRelaxIter", text="")
        
        row = grid.row(align=True)
        row.label(text="Buffer Cells No Extrude:")
        row.prop(cs, "nBufferCellsNoExtrude", text="")
        
        row = grid.row(align=True)
        row.label(text="Layer Iterations:")
        row.prop(cs, "nLayerIter", text="")
        
        row = grid.row(align=True)
        row.label(text="Relaxed Iterations:")
        row.prop(cs, "nRelaxedIter", text="")
        
        # Special controls
        row = adv_box.row()
        row.prop(cs, "additionalReporting", text="Generate Additional Reports")
    
    def layer_preview_tab(self, tools, context):
        """Preview tab for layer addition settings"""
        cs = context.scene
        
        preview_box = tools.box()
        preview_box.label(text="Generated OpenFOAM Syntax Preview", icon="TEXT")
        
        # Use dictionary writer to generate preview
        lines = generate_layer_subdictionary(cs)
        lines = format_lines_for_preview(lines)
        
        if not lines:
            # If layers are disabled
            col = preview_box.column()
            col.label(text="Layer addition is disabled")
            return
        
        # Preview content showing actual OpenFOAM dictionary syntax
        col = preview_box.column()
        col.scale_y = 0.85
        
        for line in lines:
            col.label(text=line)

    def meshquality_tab(self, tools, context):
        """Mesh quality settings interface with tabs for better organization"""
        cs = context.scene
        mesh_quality = cs.mesh_quality
        
        # Master section header
        main_box = tools.box()
        main_box.label(text="Mesh Quality Controls", icon="SETTINGS")
        
        # External dictionary option at the top level with better formatting
        row = main_box.row(align=True)
        row.prop(mesh_quality, "includeMeshQualityDict", text="Use External Mesh Quality Dictionary")
        
        if mesh_quality.includeMeshQualityDict:
            dict_row = main_box.row(align=True)
            dict_row.prop(mesh_quality, "meshQualityDictPath", text="")
            dict_row.operator("vnt.select_mesh_quality_dict", text="", icon="FILE_FOLDER")
            
            info_row = main_box.row()
            info_row.alignment = 'CENTER'
            info_row.label(text="External dictionary will be used - only error settings available", icon="INFO")
            info_row.scale_y = 1.2
        
        tools.separator(factor=1.0)
        
        row = tools.row(align=True)
        row.scale_y = 1.2 
        
        # Create a sub-row for each tab to control enabling/disabling
        for tab_id, tab_name in [
            ('STANDARD', "Standard"),
            ('ADVANCED', "Advanced"),
            ('ERROR', "Error"),
            ('PREVIEW', "Preview")
        ]:
            # Determine if this tab should be enabled
            enabled = True
            if mesh_quality.includeMeshQualityDict:
                if tab_id not in ['ERROR', 'PREVIEW']:
                    enabled = False
            
            # Create a sub-row that can be enabled/disabled
            sub = row.row(align=True)
            sub.enabled = enabled
            
            # Add the tab button
            sub.prop_enum(cs, "quality_tab", tab_id, text=tab_name)
        
        # Fix: Only force tab switch if not already on an allowed tab
        if mesh_quality.includeMeshQualityDict and cs.quality_tab not in ['ERROR', 'PREVIEW']:
            cs.quality_tab = 'ERROR'  # Default to ERROR tab when using external dict
        
        tools.separator(factor=0.5)
        
        # Display the selected tab
        if cs.quality_tab == 'STANDARD':
            self.quality_standard_tab(tools, context)
        elif cs.quality_tab == 'ADVANCED':
            self.quality_advanced_tab(tools, context)
        elif cs.quality_tab == 'ERROR':
            self.quality_error_tab(tools, context)
        elif cs.quality_tab == 'PREVIEW':
            self.quality_preview_tab(tools, context)
    
    def quality_standard_tab(self, tools, context):
        """Standard quality constraints tab"""
        cs = context.scene
        mesh_quality = cs.mesh_quality
        
        quality_box = tools.box()
        quality_box.label(text="Standard Quality Constraints", icon="CONSTRAINT")
        
        grid = quality_box.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=False)
        grid.scale_y = 1.1
        
        # Non-orthogonality
        row = grid.row(align=True)
        row.label(text="Max Non-Orthogonality:")
        row.prop(mesh_quality, "maxNonOrtho", text="")
        
        # Skewness
        row = grid.row(align=True)
        row.label(text="Max Boundary Skewness:")
        row.prop(mesh_quality, "maxBoundarySkewness", text="")
        
        row = grid.row(align=True)
        row.label(text="Max Internal Skewness:")
        row.prop(mesh_quality, "maxInternalSkewness", text="")
        
        # Shape quality
        row = grid.row(align=True)
        row.label(text="Max Concaveness:")
        row.prop(mesh_quality, "maxConcave", text="")
        
        row = grid.row(align=True)
        row.label(text="Min Flatness:")
        row.prop(mesh_quality, "minFlatness", text="")
        
        # Volume constraints
        row = grid.row(align=True)
        row.label(text="Min Volume:")
        row.prop(mesh_quality, "minVol", text="")
        
        row = grid.row(align=True)
        row.label(text="Min Tet Quality:")
        row.prop(mesh_quality, "minTetQuality", text="")
    
    def quality_advanced_tab(self, tools, context):
        """Advanced quality settings tab"""
        cs = context.scene
        mesh_quality = cs.mesh_quality
        
        adv_box = tools.box()
        adv_box.label(text="Advanced Quality Settings", icon="PREFERENCES")
        
        grid = adv_box.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=False)
        grid.scale_y = 1.1
        
        row = grid.row(align=True)
        row.label(text="Min Vol Collapse Ratio:")
        row.prop(mesh_quality, "minVolCollapseRatio", text="")
        
        row = grid.row(align=True)
        row.label(text="Min Area:")
        row.prop(mesh_quality, "minArea", text="")
        
        row = grid.row(align=True)
        row.label(text="Min Twist:")
        row.prop(mesh_quality, "minTwist", text="")
        
        row = grid.row(align=True)
        row.label(text="Min Determinant:")
        row.prop(mesh_quality, "minDeterminant", text="")
        
        row = grid.row(align=True)
        row.label(text="Min Face Weight:")
        row.prop(mesh_quality, "minFaceWeight", text="")
        
        row = grid.row(align=True)
        row.label(text="Min Vol Ratio:")
        row.prop(mesh_quality, "minVolRatio", text="")
        
        row = grid.row(align=True)
        row.label(text="Min Triangle Twist:")
        row.prop(mesh_quality, "minTriangleTwist", text="")
    
    def quality_error_tab(self, tools, context):
        """Error distribution settings tab"""
        cs = context.scene
        mesh_quality = cs.mesh_quality
        
        error_box = tools.box()
        error_box.label(text="Error Distribution Settings", icon="SNAP_FACE")
        
        info = error_box.box()
        info_text = info.column()
        info_text.scale_y = 0.9
        info_text.label(text="These settings control how mesh quality violations are")
        info_text.label(text="distributed across the domain during smoothing.")
        
        grid = error_box.grid_flow(row_major=True, columns=2, even_columns=True, even_rows=True)
        grid.scale_y = 1.1
        
        row = grid.row(align=True)
        row.label(text="Smooth Scale Iterations:")
        row.prop(mesh_quality, "nSmoothScale", text="")
        
        row = grid.row(align=True)
        row.label(text="Error Reduction:")
        row.prop(mesh_quality, "errorReduction", text="")
        
    def quality_preview_tab(self, tools, context):
        """Preview tab for mesh quality settings"""
        cs = context.scene
        
        box = tools.box()
        box.label(text="Generated OpenFOAM Syntax Preview", icon="TEXT")
        
        lines = generate_quality_subdictionary(cs)
        lines = format_lines_for_preview(lines)
        
        col = box.column()
        col.scale_y = 0.85
        
        for line in lines:
            col.label(text=line)

    def dictionary_tab(self, tools, context):
        """Dictionary generation interface with a single button to generate and save the dictionary"""
        cs = context.scene
        
        # Debug Flags Section
        debug_box = tools.box()
        debug_box.label(text="Debug Flags", icon="VIEWZOOM")
        
        debug_box.prop(cs, "use_debug_flags", text="Enable Debug Output")
        
        if cs.use_debug_flags:
            flags_col = debug_box.column(align=True)
            
            row = flags_col.row()
            row.prop(cs, "debugFlag_mesh", text="Write intermediate meshes")
            
            row = flags_col.row()
            row.prop(cs, "debugFlag_intersections", text="Write mesh intersections (.obj)")
            
            row = flags_col.row()
            row.prop(cs, "debugFlag_featureSeeds", text="Write feature edge refinement info")
            
            row = flags_col.row()
            row.prop(cs, "debugFlag_attraction", text="Write attraction (.obj)")
            
            row = flags_col.row()
            row.prop(cs, "debugFlag_layerInfo", text="Write layer information")
        
        # Write Flags Section
        write_box = tools.box()
        write_box.label(text="Write Flags", icon="EXPORT")
        
        row = write_box.row()
        row.prop(cs, "writeFlag_scalarLevels", text="Write cell level fields")
        
        row = write_box.row()
        row.prop(cs, "writeFlag_layerSets", text="Write layer cell/face sets")
        
        row = write_box.row()
        row.prop(cs, "writeFlag_layerFields", text="Write layer coverage fields")
        
        # Merge Tolerance Section
        merge_box = tools.box()
        merge_box.label(text="Global Mesh Settings", icon="AUTOMERGE_ON")
        
        row = merge_box.row(align=True)
        row.label(text="Merge Tolerance:")
        row.prop(cs, "mergeTolerance", text="")
        
        help_text = merge_box.column()
        help_text.scale_y = 0.85
        help_text.label(text="Tolerance used for point merging. Relative to bounding box.")
        help_text.label(text="Lower values preserve more detail but may cause mesh issues.")
        
        tools.separator()
        row = tools.row(align=True)
        row.scale_y = 1.5
        row.operator("vnt.generate_snappyhex_dict", text="Generate SnappyHexMesh Dictionary", icon="FILE_TICK")


@persistent
def clean_geometry_items(dummy):
    scene = bpy.context.scene
    items = scene.geometry_items
    for i in range(len(items) - 1, -1, -1):
        if not bpy.data.objects.get(items[i].name):
            items.remove(i)

if clean_geometry_items not in bpy.app.handlers.depsgraph_update_post:
    bpy.app.handlers.depsgraph_update_post.append(clean_geometry_items)

