import bpy
import os
import json
from bpy.app.handlers import persistent
from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper

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
        #----------------------------------------------------------------------------------------------
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
        #----------------------------------------------------------------------------------------------
        
        # Mesh Options section
        #----------------------------------------------------------------------------------------------
        box = tools.box()
        box.label(text="Mesh Options")
        row = box.row(align=True)
        row.prop(cs, "castellatedMesh", text="Castellated Mesh")
        row.prop(cs, "snap", text="Snap")
        row.prop(cs, "addLayers", text="Add Layers")
        #----------------------------------------------------------------------------------------------
        
        # Geometry section
        #----------------------------------------------------------------------------------------------
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
        row.operator("vnt.export_stl_geometry", text="Export STL Geometry")
        row.operator("vnt.generate_snappyhex_dict", text="Generate Dictionary")
        
        # Dictionary preview
        box_dict = tools.box()
        box_dict.label(text="Generated Dictionary Preview")
        
        # Add a preview of the dictionary (partial)
        if hasattr(cs, 'snappy_dict_preview') and cs.snappy_dict_preview:
            preview_lines = cs.snappy_dict_preview.split('\n')
            for i, line in enumerate(preview_lines):
                if i < 20:  # Show only first 20 lines
                    box_dict.label(text=line)
            
            if len(preview_lines) > 20:
                box_dict.label(text="... (preview truncated)")
                
            # Show total line count
            box_dict.label(text=f"Total lines: {len(preview_lines)}")
        else:
            box_dict.label(text="Click 'Generate Dictionary' to preview the dictionary.")

class VNT_OT_create_new_geometry(Operator):
    """Create new geometry"""
    bl_idname = "vnt.create_new_geometry"
    bl_label = "Create New Geometry"

    geometry_type: bpy.props.EnumProperty(
        name="Type",
        description="Select Geometry Type",
        items=[
            ("searchableBox", "Box", ""),
            ("searchableSphere", "Sphere", ""),
        ],
        default="searchableBox"
    )
    geometry_name: bpy.props.StringProperty( 
        name="Name",
        description="Enter the geometry name",
        default=""
    )
    min_x: bpy.props.FloatProperty(name="Min X", default=0.0)
    min_y: bpy.props.FloatProperty(name="Min Y", default=0.0)
    min_z: bpy.props.FloatProperty(name="Min Z", default=0.0)
    max_x: bpy.props.FloatProperty(name="Max X", default=1.0)
    max_y: bpy.props.FloatProperty(name="Max Y", default=1.0)
    max_z: bpy.props.FloatProperty(name="Max Z", default=1.0)
    centre_x: bpy.props.FloatProperty(name="Centre X", default=0.0)
    centre_y: bpy.props.FloatProperty(name="Centre Y", default=0.0)
    centre_z: bpy.props.FloatProperty(name="Centre Z", default=0.0)
    radius: bpy.props.FloatProperty(name="Radius", default=1.0)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        layout.row().label(text="Name")
        layout.row().prop(self, "geometry_name", text="")
        row = layout.row()
        row.label(text="Type")
        row.prop(self, "geometry_type", text="")
        if self.geometry_type == "searchableBox":
            layout.label(text="Box Settings:")
            row = layout.row()
            row.prop(self, "min_x", text="Min X")
            row.prop(self, "max_x", text="Max X")
            row = layout.row()
            row.prop(self, "min_y", text="Min Y")
            row.prop(self, "max_y", text="Max Y")
            row = layout.row()
            row.prop(self, "min_z", text="Min Z")
            row.prop(self, "max_z", text="Max Z")
        elif self.geometry_type == "searchableSphere":
            layout.label(text="Sphere Settings:")
            row = layout.row()
            row.prop(self, "centre_x", text="Centre X")
            row.prop(self, "centre_y", text="Centre Y")
            row.prop(self, "centre_z", text="Centre Z")
            layout.prop(self, "radius", text="Radius")

    def execute(self, context):
        cs = context.scene
        if self.geometry_type == "searchableBox":
            width  = self.max_x - self.min_x
            height = self.max_y - self.min_y
            depth  = self.max_z - self.min_z
            center = ((self.min_x + self.max_x) / 2,
                      (self.min_y + self.max_y) / 2,
                      (self.min_z + self.max_z) / 2)
            bpy.ops.mesh.primitive_cube_add(location=center)
            cube = context.active_object
            cube.scale = (width / 2, height / 2, depth / 2)
        elif self.geometry_type == "searchableSphere":
            loc = (self.centre_x, self.centre_y, self.centre_z)
            bpy.ops.mesh.primitive_uv_sphere_add(radius=self.radius, location=loc)
        obj = context.active_object
        if self.geometry_name:
            obj.name = self.geometry_name
        else:
            obj.name = f"{self.geometry_type}_{len(cs.geometry_items)}"
        col = bpy.data.collections.get("User Defined Geometry")
        if not col:
            col = bpy.data.collections.new("User Defined Geometry")
            context.scene.collection.children.link(col)
        if obj.name not in col.objects:
            col.objects.link(obj)
        if obj.name in context.scene.collection.objects:
            context.scene.collection.objects.unlink(obj)
        new_item = cs.geometry_items.add()
        new_item.name = obj.name
        self.report({'INFO'}, f"Created geometry of type {self.geometry_type}")
        return {'FINISHED'}

class VNT_OT_delete_geometry(Operator):
    """Delete geometry"""
    bl_idname = "vnt.delete_geometry"
    bl_label = "Delete Geometry"

    def execute(self, context):
        cs = context.scene
        index = cs.geometry_items_index
        if index < 0 or index >= len(cs.geometry_items):
            self.report({'WARNING'}, "Please select geometry to delete")
            return {'CANCELLED'}
        geom_name = cs.geometry_items[index].name
        obj = bpy.data.objects.get(geom_name)
        if not obj:
            cs.geometry_items.remove(index)
            cs.geometry_items_index = min(index, len(cs.geometry_items) - 1)
            self.report({'WARNING'}, f"Object {geom_name} not found, removed from list")
            return {'FINISHED'}
        for col in obj.users_collection:
            col.objects.unlink(obj)
        bpy.data.objects.remove(obj)
        cs.geometry_items.remove(index)
        cs.geometry_items_index = min(index, len(cs.geometry_items) - 1)
        self.report({'INFO'}, f"Deleted geometry: {geom_name}")
        return {'FINISHED'}

class VNT_OT_export_stl_geometry(Operator, ExportHelper):
    bl_idname = "vnt.export_stl_geometry"
    bl_label = "Export STL Geometry"
    
    filename_ext = ".stl"
    filter_glob: bpy.props.StringProperty(default="*.stl", options={'HIDDEN'})
    
    def execute(self, context):
        if not context.selected_objects:
            self.report({'ERROR'}, "No objects selected for export")
            return {'CANCELLED'}
        
        bpy.ops.export_mesh.stl(
            filepath=self.filepath,
            check_existing=True,
            filter_glob="*.stl",
            use_selection=True,
            global_scale=1.0,
            use_scene_unit=False,
            ascii=False,
            use_mesh_modifiers=True,
            batch_mode='OFF'
        )
        context.scene.stl_file = self.filepath
        context.scene.stl_file_name = os.path.basename(self.filepath)
        
        self.report({'INFO'}, f"Exported STL to {self.filepath}")
        return {'FINISHED'}

class VNT_OT_generate_snappyhex_dict(Operator, ExportHelper):
    """Generate and save a snappyHexMeshDict file"""
    bl_idname = "vnt.generate_snappyhex_dict"
    bl_label = "Generate snappyHexMeshDict"
    
    filename_ext = ""
    filter_glob: bpy.props.StringProperty(default="*", options={'HIDDEN'})
    
    def execute(self, context):
        from venturial.models.snappyhexmesh.snappydict_writer import generate_snappy_dict, write_snappy_dict_to_file
        
        # Generate dictionary and save to preview
        dictionary = generate_snappy_dict(context.scene)
        context.scene.snappy_dict_preview = dictionary
        
        if self.filepath:
            # Make sure directory exists
            directory = os.path.dirname(self.filepath)
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                except Exception as e:
                    self.report({'ERROR'}, f"Failed to create directory: {e}")
                    return {'CANCELLED'}
            
            # Ensure the filepath ends with 'snappyHexMeshDict'
            target_path = self.filepath
            if not os.path.basename(target_path) or '.' in os.path.basename(target_path):
                target_path = os.path.join(target_path, 'snappyHexMeshDict')
            
            # Write to file
            success = write_snappy_dict_to_file(context.scene, target_path)
            if success:
                self.report({'INFO'}, f"Dictionary saved to {target_path}")
            else:
                self.report({'ERROR'}, f"Failed to write dictionary to {target_path}")
                return {'CANCELLED'}
        
        return {'FINISHED'}

@persistent
def clean_geometry_items(dummy):
    scene = bpy.context.scene
    items = scene.geometry_items
    for i in range(len(items) - 1, -1, -1):
        if not bpy.data.objects.get(items[i].name):
            items.remove(i)

if clean_geometry_items not in bpy.app.handlers.depsgraph_update_post:
    bpy.app.handlers.depsgraph_update_post.append(clean_geometry_items)

