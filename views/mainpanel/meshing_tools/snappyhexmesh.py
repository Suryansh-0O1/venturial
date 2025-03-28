import bpy
import os
import json
from bpy.app.handlers import persistent

# Import operators from their new locations
from venturial.models.snappyhexmesh.geometry_operators import VNT_OT_create_new_geometry, VNT_OT_delete_geometry
from venturial.models.snappyhexmesh.file_operators import VNT_OT_export_stl_geometry
from venturial.models.snappyhexmesh.dictionary_operators import VNT_OT_generate_snappyhex_dict

class snappyhexmesh_menu:
    def layout(self, tools, context):
        cs = context.scene
        
        # Check which tab is selected and call the appropriate method
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
            # Default to geometry tab if none selected
            self.geometry_tab(tools, context)
    
    def geometry_tab(self, tools, context):
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
        
        # Geometry section
        row = tools.row(align=True)
        row.column(align=True).label(text="User Defined Geometry")
        row = tools.row(align=True)
        row.column(align=True).template_list("UI_UL_list", "geometry_items", cs, "geometry_items", cs, "geometry_items_index", rows=3)
        col_button = row.column(align=True)
        col_button.operator("vnt.create_new_geometry", text="", icon="ADD")
        col_button.operator("vnt.delete_geometry", text="", icon="REMOVE")
        #----------------------------------------------------------------------------------------------

    def castellated_tab(self, tools, context):
        cs = context.scene
        box = tools.box()
        box.label(text="Castellation Options")
        
        # Main enable switch
        row = box.row()
        row.prop(cs, "castellatedMesh", text="Enable Castellated Mesh")
        
        if not cs.castellatedMesh:
            return
            
        # General Refinement Parameters
        ref_box = tools.box()
        ref_box.label(text="Refinement Parameters", icon="SETTINGS")
        
        # Cell Limits
        col = ref_box.column(align=True)
        row = col.row()
        row.label(text="Max Local Cells:")
        row.prop(cs, "maxLocalCells", text="")
        
        row = col.row()
        row.label(text="Max Global Cells:")
        row.prop(cs, "maxGlobalCells", text="")
        
        row = col.row()
        row.label(text="Min Refinement Cells:")
        row.prop(cs, "minRefinementCells", text="")
        
        # Load Balance
        row = col.row()
        row.label(text="Max Load Unbalance:")
        row.prop(cs, "maxLoadUnbalance", text="")
        
        # Buffer Layers
        row = col.row()
        row.label(text="Cells Between Levels:")
        row.prop(cs, "nCellsBetweenLevels", text="")
        
        # Feature Edge Refinement
        feature_box = tools.box()
        feature_box.label(text="Feature Edge Refinement", icon="EDGESEL")
        
        # Feature list with browse button
        row = feature_box.row()
        col = row.column()
        col.template_list("CAST_UL_features_list", "", cs, "cast_features", 
                          cs, "cast_features_index", rows=2)
        
        col_buttons = row.column(align=True)
        col_buttons.operator("vnt.add_feature", text="", icon="ADD")
        col_buttons.operator("vnt.remove_feature", text="", icon="REMOVE")
        
        # Add file browser button for the selected feature
        if len(cs.cast_features) > 0 and cs.cast_features_index >= 0:
            feature = cs.cast_features[cs.cast_features_index]
            row = feature_box.row()
            row.prop(feature, "file", text="File Path")
            
            # Add browse button
            browse_op = row.operator("vnt.browse_feature_file", text="", icon="FILE_FOLDER")
            browse_op.feature_index = cs.cast_features_index
            
            # Add options for the selected feature
            box = feature_box.box()
            row = box.row()
            row.prop(feature, "use_levels", text="Use Distance-based Levels")
            
            if feature.use_levels:
                row = box.row()
                row.prop(feature, "distance", text="Distance")
                row.prop(feature, "level_at_distance", text="Level")
            else:
                row = box.row()
                row.prop(feature, "level", text="Level")
        
        # Surface Refinement
        surface_box = tools.box()
        surface_box.label(text="Surface Refinement", icon="SURFACE_DATA")
        
        # Refinement surfaces list with browse button
        row = surface_box.row()
        col = row.column()
        col.template_list("CAST_UL_refinement_surfaces", "", cs, "cast_refinement_surfaces", 
                          cs, "cast_refinement_surfaces_index", rows=2)
        
        col_buttons = row.column(align=True)
        col_buttons.operator("vnt.add_refinement_surface", text="", icon="ADD")
        col_buttons.operator("vnt.remove_refinement_surface", text="", icon="REMOVE")
        
        # Add options for the selected surface
        if len(cs.cast_refinement_surfaces) > 0 and cs.cast_refinement_surfaces_index >= 0:
            surface = cs.cast_refinement_surfaces[cs.cast_refinement_surfaces_index]
            
            row = surface_box.row()
            row.prop(surface, "name", text="Surface Name")
            
            # Add browse button
            browse_op = row.operator("vnt.browse_surface_file", text="", icon="FILE_FOLDER")
            browse_op.surface_index = cs.cast_refinement_surfaces_index
            
            row = surface_box.row()
            row.prop(surface, "min_level", text="Min Level")
            row.prop(surface, "max_level", text="Max Level")
            
            # Region settings
            row = surface_box.row()
            row.label(text="Regions:")
            row.operator("vnt.add_surface_region", text="", icon="ADD")
            if len(surface.regions) > 0 and surface.regions_index >= 0:
                row.operator("vnt.remove_surface_region", text="", icon="REMOVE")
            
            # Show regions if there are any
            if len(surface.regions) > 0:
                for i, region in enumerate(surface.regions):
                    box = surface_box.box()
                    row = box.row()
                    row.prop(region, "name", text=f"Region {i+1}")
                    row = box.row()
                    row.prop(region, "min_level", text="Min Level")
                    row.prop(region, "max_level", text="Max Level")
        
        # Region Refinement
        region_box = tools.box()
        region_box.label(text="Region Refinement", icon="MESH_CUBE")
        
        row = region_box.row()
        row.template_list("CAST_UL_refinement_regions", "", cs, "cast_refinement_regions", 
                          cs, "cast_refinement_regions_index", rows=2)
        
        col = row.column(align=True)
        col.operator("vnt.add_refinement_region", text="", icon="ADD")
        col.operator("vnt.remove_refinement_region", text="", icon="REMOVE")
        
        # Add options for the selected region
        if len(cs.cast_refinement_regions) > 0 and cs.cast_refinement_regions_index >= 0:
            region = cs.cast_refinement_regions[cs.cast_refinement_regions_index]
            
            row = region_box.row()
            row.prop(region, "name", text="Name")
            row.prop(region, "mode", text="Mode")
            
            if region.mode == 'distance':
                box = region_box.box()
                row = box.row()
                row.prop(region, "distance", text="Distance")
                row.prop(region, "level_at_distance", text="Level at Distance")
            else:
                box = region_box.box()
                row = box.row()
                row.prop(region, "level", text="Level")
    
    def snap_tab(self, tools, context):
        cs = context.scene
        box = tools.box()
        box.label(text="Snap Settings")
        
        # Enable/disable snap
        row = box.row()
        row.prop(cs, "snap", text="Enable Snap")
        
        # Only show settings if enabled
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
            
            # Patch smoothing
            row = col.row()
            row.label(text="Patch Smoothing Iterations")
            row.prop(cs, "nSmoothPatch", text="")
            
            # Mesh displacement relaxation
            row = col.row()
            row.label(text="Solve Iterations")
            row.prop(cs, "nSolveIter", text="")
            
            # Maximum relaxation
            row = col.row()
            row.label(text="Relax Iterations")
            row.prop(cs, "nRelaxIter", text="")
            
            # Feature snapping settings
            feature_box = tools.box()
            feature_box.label(text="Feature Snapping", icon="OUTLINER_OB_CURVE")
            
            # Enable feature snapping
            row = feature_box.row()
            row.prop(cs, "useFeatureSnap", text="Enable Feature Snapping")
            
            # Only show feature settings if enabled
            if cs.useFeatureSnap:
                col = feature_box.column(align=True)
                
                # Feature snap iterations
                row = col.row()
                row.label(text="Feature Snap Iterations")
                row.prop(cs, "nFeatureSnapIter", text="")
                
                # Feature detection options
                row = col.row()
                row.label(text="Feature Detection:")
                
                box_detect = feature_box.box()
                col_detect = box_detect.column()
                
                col_detect.prop(cs, "implicitFeatureSnap", text="Implicit Feature Snap")
                col_detect.prop(cs, "explicitFeatureSnap", text="Explicit Feature Snap")
                col_detect.prop(cs, "multiRegionFeatureSnap", text="Multi-region Feature Snap")
                
                if cs.implicitFeatureSnap and cs.explicitFeatureSnap:
                    box_detect.label(text="Warning: Using both implicit and explicit feature snapping", icon="ERROR")
                    
            # Add advanced settings toggle if needed
            row = tools.row()
            row.label(text="Note: These settings will be written to snapControls dictionary")

    def layercontrol_tab(self, tools, context):
        cs = context.scene
        box = tools.box()
        box.label(text="Layer Addition Settings")
        
        # Enable/disable layers
        row = box.row()
        row.prop(cs, "addLayers", text="Enable Layer Addition")
        
        # Only show settings if enabled
        if cs.addLayers:
            # Basic settings
            basic_box = tools.box()
            basic_box.label(text="Basic Layer Settings", icon="MATCLOTH")
            
            # Relative sizes
            row = basic_box.row()
            row.prop(cs, "relativeSizes", text="Use Relative Sizes")
            
            # Thickness mode selection
            row = basic_box.row()
            row.label(text="Thickness Specification Method:")
            row = basic_box.row()
            row.prop(cs, "thickness_mode", text="")
            
            # Show relevant thickness parameters based on the selected mode
            thickness_box = basic_box.box()
            mode = cs.thickness_mode
            
            if 'expansion' in mode:
                row = thickness_box.row()
                row.prop(cs, "expansionRatio", text="Expansion Ratio")
            
            if 'first' in mode:
                row = thickness_box.row()
                row.prop(cs, "firstLayerThickness", text="First Layer Thickness")
            
            if 'final' in mode:
                row = thickness_box.row()
                row.prop(cs, "finalLayerThickness", text="Final Layer Thickness")
            
            if 'overall' in mode:
                row = thickness_box.row()
                row.prop(cs, "overallThickness", text="Overall Thickness")
            
            # Minimum thickness
            row = basic_box.row()
            row.prop(cs, "minThickness", text="Minimum Thickness")
            
            # Patch settings for layers
            patch_box = tools.box()
            patch_box.label(text="Layer Patches", icon="OUTLINER_OB_SURFACE")
            
            row = patch_box.row()
            row.template_list("LAYER_UL_patches_list", "", cs, "layer_patches", 
                              cs, "layer_patches_index", rows=2)
            
            col = row.column(align=True)
            col.operator("vnt.add_layer_patch", text="", icon="ADD")
            col.operator("vnt.remove_layer_patch", text="", icon="REMOVE")
            
            # Show settings for selected patch
            if len(cs.layer_patches) > 0 and cs.layer_patches_index >= 0:
                patch = cs.layer_patches[cs.layer_patches_index]
                box = patch_box.box()
                
                row = box.row()
                row.prop(patch, "name", text="Patch Name")
                
                row = box.row()
                row.prop(patch, "nSurfaceLayers", text="Surface Layers")
                
                row = box.row()
                row.prop(patch, "custom_expansion", text="Custom Expansion Settings")
                
                if patch.custom_expansion:
                    col = box.column()
                    col.prop(patch, "expansionRatio", text="Expansion Ratio")
                    col.prop(patch, "finalLayerThickness", text="Final Layer Thickness")
                    col.prop(patch, "minThickness", text="Minimum Thickness")
            
            # Advanced settings (collapsible)
            advanced_box = tools.box()
            advanced_box.label(text="Advanced Settings", icon="SETTINGS")
            
            # Feature angle control
            row = advanced_box.row()
            row.label(text="Feature Analysis:")
            
            feature_box = advanced_box.box()
            col = feature_box.column(align=True)
            col.prop(cs, "featureAngle", text="Feature Angle")
            col.prop(cs, "maxFaceThicknessRatio", text="Max Face Thickness Ratio")
            col.prop(cs, "nGrow", text="Grow Layers")
            
            # Surface normal control
            row = advanced_box.row()
            row.label(text="Patch Displacement:")
            
            normal_box = advanced_box.box()
            col = normal_box.column(align=True)
            col.prop(cs, "nSmoothSurfaceNormals", text="Smooth Surface Normals")
            col.prop(cs, "nSmoothThickness", text="Smooth Thickness")
            
            # Medial axis settings
            row = advanced_box.row()
            row.label(text="Medial Axis Analysis:")
            
            medial_box = advanced_box.box()
            col = medial_box.column(align=True)
            col.prop(cs, "minMedialAxisAngle", text="Min Medial Axis Angle")
            col.prop(cs, "maxThicknessToMedialRatio", text="Max Thickness to Medial Ratio")
            col.prop(cs, "nSmoothNormals", text="Smooth Normals")
            
            # Mesh shrinking settings
            row = advanced_box.row()
            row.label(text="Mesh Shrinking:")
            
            shrink_box = advanced_box.box()
            col = shrink_box.column(align=True)
            col.prop(cs, "slipFeatureAngle", text="Slip Feature Angle")
            col.prop(cs, "layerRelaxIter", text="Relax Iterations")
            col.prop(cs, "nBufferCellsNoExtrude", text="Buffer Cells No Extrude")
            col.prop(cs, "nLayerIter", text="Max Layer Iterations")
            col.prop(cs, "nRelaxedIter", text="Relaxed Quality Iterations")
            col.prop(cs, "additionalReporting", text="Additional Reporting")
            
            # Note that these settings will be written to addLayersControls dictionary
            row = tools.row()
            row.label(text="Note: These settings will be written to addLayersControls dictionary")

    def meshquality_tab(self, tools, context):
        cs = context.scene
        box = tools.box()
        box.label(text="Mesh Quality Settings")
        
        # Main include file option
        include_box = tools.box()
        include_box.label(text="Mesh Quality Dictionary", icon="FILE_TEXT")
        row = include_box.row()
        row.prop(cs, "includeMeshQualityDict", text="Include External Mesh Quality Dictionary")
        
        if cs.includeMeshQualityDict:
            # Path to mesh quality dictionary
            row = include_box.row()
            row.prop(cs, "meshQualityDictPath", text="Path")
            row.operator("vnt.select_mesh_quality_dict", text="", icon="FILE_FOLDER")
        else:
            # Basic mesh quality settings (if not using external file)
            quality_box = tools.box()
            quality_box.label(text="Basic Mesh Quality Settings", icon="SETTINGS")
            
            col = quality_box.column(align=True)
            col.prop(cs, "maxNonOrtho", text="Max Non-Orthogonality")
            col.prop(cs, "maxBoundarySkewness", text="Max Boundary Skewness")
            col.prop(cs, "maxInternalSkewness", text="Max Internal Skewness")
            
            col = quality_box.column(align=True)
            col.prop(cs, "maxConcave", text="Max Concaveness")
            col.prop(cs, "minFlatness", text="Min Flatness")
            col.prop(cs, "minVol", text="Min Volume")
            
            col = quality_box.column(align=True)
            col.prop(cs, "minTetQuality", text="Min Tet Quality")
        
        # Relaxed settings section
        relaxed_box = tools.box()
        relaxed_box.label(text="Relaxed Quality Settings", icon="MOD_SMOOTH")
        
        row = relaxed_box.row()
        row.label(text="Used during specific phases like layer addition")
        
        row = relaxed_box.row()
        row.prop(cs, "relaxedMaxNonOrtho", text="Relaxed Max Non-Orthogonality")
        
        # Advanced settings
        advanced_box = tools.box()
        advanced_box.label(text="Advanced Settings", icon="PREFERENCES")
        
        col = advanced_box.column(align=True)
        col.prop(cs, "nSmoothScale", text="Error Distribution Iterations")
        col.prop(cs, "errorReduction", text="Error Reduction Factor")
        
        # Note about mesh quality dict
        row = tools.row()
        row.label(text="Note: These settings will be written to meshQualityControls dictionary")

    def dictionary_tab(self, tools, context):
        cs = context.scene
        box = tools.box()
        box.label(text="Dictionary Controls")
        
        # Dictionary actions
        row = box.row(align=True)
        row.operator("vnt.generate_snappyhex_dict", text="Generate Dictionary")

@persistent
def clean_geometry_items(dummy):
    scene = bpy.context.scene
    items = scene.geometry_items
    for i in range(len(items) - 1, -1, -1):
        if not bpy.data.objects.get(items[i].name):
            items.remove(i)

if clean_geometry_items not in bpy.app.handlers.depsgraph_update_post:
    bpy.app.handlers.depsgraph_update_post.append(clean_geometry_items)

