"""
SnappyHexMesh subdictionary writers module

This module contains functions to generate individual subdictionaries for SnappyHexMesh.
These functions are used both for preview generation in the UI and for the final dictionary output,
ensuring consistency between what users see in previews and the actual generated dictionary.
"""

import os
import bpy

def _fmt(val):
    """Format floats to fixed precision for dictionary output."""
    return f"{val:.6f}" if isinstance(val, float) else str(val)

def generate_geometry_subdictionary(scene):
    """Generate the geometry subdictionary"""
    lines = []
    lines.append("geometry")
    lines.append("{")
    
    # If no geometry at all
    if not scene.geometry_items and not scene.stl_file_name:
        lines.append("    // No geometry defined")
    
    # Always show imported STL if present
    if scene.stl_file_name:
        # Use the full STL filename directly as the dictionary key
        lines.append(f"    {scene.stl_file_name}")
        lines.append("    {")
        lines.append("        type triSurfaceMesh;")
        
        # Use custom name if provided, otherwise fall back to basename without extension
        if scene.stl_custom_name:
            lines.append(f"        name {scene.stl_custom_name};")
        else:
            base_name = os.path.splitext(os.path.basename(scene.stl_file_name))[0]
            lines.append(f"        name {base_name};")
        
        # Add regions section if we have STL regions defined
        if len(scene.stl_regions) > 0:
            lines.append("")
            lines.append("        regions")
            lines.append("        {")
            
            # Add each enabled region
            for region in scene.stl_regions:
                if region.enabled:
                    lines.append(f"            {region.original_name}")
                    lines.append("            {")
                    # Use custom name if provided, otherwise use original name
                    name_to_use = region.custom_name if region.custom_name else region.original_name
                    lines.append(f"                name {name_to_use};")
                    lines.append("            }")
            
            lines.append("        }")
        
        lines.append("    }")

    # Process all primitive geometry items
    for item in scene.geometry_items:
        # Use stored properties for primitives
        if item.geometry_type == "searchableBox":
            min_x, min_y, min_z = item.box_min
            max_x, max_y, max_z = item.box_max
            lines.append(f"    {item.name}")
            lines.append("    {")
            lines.append("        type searchableBox;")
            lines.append(f"        min ({_fmt(min_x)} {_fmt(min_y)} {_fmt(min_z)});")
            lines.append(f"        max ({_fmt(max_x)} {_fmt(max_y)} {_fmt(max_z)});")
            lines.append("    }")
            continue

        if item.geometry_type == "searchableSphere":
            cx, cy, cz = item.sphere_center
            r = item.sphere_radius
            lines.append(f"    {item.name}")
            lines.append("    {")
            lines.append("        type searchableSphere;")
            lines.append(f"        centre ({_fmt(cx)} {_fmt(cy)} {_fmt(cz)});")
            lines.append(f"        radius {_fmt(r)};")
            lines.append("    }")
            continue

        # Fallback: generic mesh via its object name
        obj = bpy.data.objects.get(item.name)
        if not obj or obj.type != 'MESH':
            continue
        lines.append(f"    {obj.name}")
        lines.append("    {")
        lines.append("        type triSurfaceMesh;")
        lines.append("    }")
    
    lines.append("};")
    return lines

def generate_castellated_subdictionary(scene):
    """Generate the castellatedMeshControls subdictionary"""
    lines = []
    lines.append("castellatedMeshControls")
    lines.append("{")
    
    # Basic parameters
    lines.append("    // Basic parameters")
    lines.append(f"    maxLocalCells {scene.maxLocalCells};")
    lines.append(f"    maxGlobalCells {scene.maxGlobalCells};")
    lines.append(f"    minRefinementCells {scene.minRefinementCells};")
    lines.append(f"    maxLoadUnbalance {_fmt(scene.maxLoadUnbalance)};")
    lines.append(f"    nCellsBetweenLevels {scene.nCellsBetweenLevels};")
    
    # Features section
    if len(scene.cast_features) > 0:
        lines.append("")
        lines.append("    // Feature refinement")
        lines.append("    features")
        lines.append("    (")
        
        for feature in scene.cast_features:
            if feature.file:
                lines.append("        {")
                lines.append(f"            file \"{os.path.basename(feature.file)}\";")
                
                if feature.refinement_mode == 'single_distance':
                    lines.append(f"            levels (({_fmt(feature.distance)} {feature.level_at_distance}));")
                elif feature.refinement_mode == 'multi_distance':
                    if len(feature.distance_level_pairs) > 0:
                        pairs_text = " ".join([f"({p.distance} {p.level})" for p in feature.distance_level_pairs])
                        lines.append(f"            levels ({pairs_text});")
                    else:
                        lines.append("            levels ();")
                else:  # 'uniform' mode
                    lines.append(f"            level {feature.level};")
                    
                lines.append("        }")
        
        lines.append("    );")
    
    # Refinement surfaces
    if len(scene.cast_refinement_surfaces) > 0:
        lines.append("")
        lines.append("    // Surface refinement")
        lines.append("    refinementSurfaces")
        lines.append("    {")
        
        for surface in scene.cast_refinement_surfaces:
            if surface.source_type == 'geometry' and surface.geometry_object:
                surface_name = surface.geometry_object
            else:
                surface_name = surface.name
                
            lines.append(f"        {surface_name}")
            lines.append("        {")
            lines.append(f"            level ({surface.min_level} {surface.max_level});")
            
            if hasattr(surface, 'face_zone') and surface.face_zone:
                lines.append(f"            faceZone {surface.face_zone};")
            
            if hasattr(surface, 'cell_zone') and surface.cell_zone:
                lines.append(f"            cellZone {surface.cell_zone};")
                
                if hasattr(surface, 'cell_zone_inside'):
                    lines.append(f"            cellZoneInside {surface.cell_zone_inside};")
            
            if surface.regions:
                lines.append("")
                lines.append("            regions")
                lines.append("            {")
                for region in surface.regions:
                    lines.append(f"                {region.name}")
                    lines.append("                {")
                    lines.append(f"                    level ({region.min_level} {region.max_level});")
                    if region.use_patch_info:
                        pi = region.patch_info
                        lines.append("                    patchInfo")
                        lines.append("                    {")
                        lines.append(f"                        type {pi.patch_type};")
                        lines.append(f"                        inGroups ({pi.in_group});")
                        lines.append("                    }")
                    lines.append("                }")
                lines.append("            }")
            lines.append("        }")
        
        lines.append("    }")
    
    # Refinement regions
    if len(scene.cast_refinement_regions) > 0:
        lines.append("")
        lines.append("    // Region refinement")
        lines.append("    refinementRegions")
        lines.append("    {")
        
        for region in scene.cast_refinement_regions:
            lines.append(f"        {region.name}")
            lines.append("        {")
            lines.append(f"            mode {region.mode};")
            
            if region.mode == 'distance':
                lines.append(f"            levels (({region.distance} {region.level_at_distance}));")
            else:  # inside or outside
                lines.append(f"            levels (({1.0} {region.level}));")
            
            lines.append("        }")
        
        lines.append("    }")
    
    # Location in mesh
    lines.append("")
    lines.append("    // Mesh selection")
    lines.append(f"    locationInMesh ({scene.locationInMeshX} {scene.locationInMeshY} {scene.locationInMeshZ});")
    lines.append(f"    allowFreeStandingZoneFaces {str(scene.allowFreeStandingZoneFaces).lower()};")
    
    # Feature angle settings
    lines.append("")
    lines.append("    // Feature handling")
    lines.append(f"    resolveFeatureAngle {scene.resolveFeatureAngle};")
    lines.append(f"    planarAngle {scene.planarAngle};")
    
    # Advanced options
    if scene.handleSnapProblems or scene.useTopologicalSnapDetection:
        lines.append("")
        lines.append("    // Advanced options")
        if scene.handleSnapProblems:
            lines.append(f"    handleSnapProblems {str(scene.handleSnapProblems).lower()};")
        if scene.useTopologicalSnapDetection:
            lines.append(f"    useTopologicalSnapDetection {str(scene.useTopologicalSnapDetection).lower()};")
    
    lines.append("}")
    return lines

def generate_snap_subdictionary(scene):
    """Generate the snapControls subdictionary"""
    lines = []
    lines.append("snapControls")
    lines.append("{")
    lines.append(f"    nSmoothPatch {scene.nSmoothPatch};")
    lines.append(f"    tolerance {_fmt(scene.tolerance)};")
    lines.append(f"    nSolveIter {scene.nSolveIter};")
    lines.append(f"    nRelaxIter {scene.nRelaxIter};")
    
    if scene.useFeatureSnap:
        lines.append("")
        lines.append("    // Feature snapping")
        lines.append(f"    nFeatureSnapIter {scene.nFeatureSnapIter};")
        lines.append(f"    implicitFeatureSnap {str(scene.implicitFeatureSnap).lower()};")
        lines.append(f"    explicitFeatureSnap {str(scene.explicitFeatureSnap).lower()};")
        lines.append(f"    multiRegionFeatureSnap {str(scene.multiRegionFeatureSnap).lower()};")
    
    lines.append("}")
    return lines

def generate_layer_subdictionary(scene):
    """Generate the addLayersControls subdictionary"""
    if not scene.addLayers:
        return []
        
    lines = []
    lines.append("addLayersControls")
    lines.append("{")
    lines.append(f"    relativeSizes {str(scene.relativeSizes).lower()};")
    
    # Add the thickness specification based on the selected mode
    mode = scene.thickness_mode
    if 'expansion' in mode and 'final' in mode:
        lines.append(f"    expansionRatio {_fmt(scene.expansionRatio)};")
        lines.append(f"    finalLayerThickness {_fmt(scene.finalLayerThickness)};")
    elif 'expansion' in mode and 'first' in mode:
        lines.append(f"    expansionRatio {_fmt(scene.expansionRatio)};")
        lines.append(f"    firstLayerThickness {_fmt(scene.firstLayerThickness)};")
    elif 'overall' in mode and 'first' in mode:
        lines.append(f"    thickness {_fmt(scene.overallThickness)};")
        lines.append(f"    firstLayerThickness {_fmt(scene.firstLayerThickness)};")
    elif 'overall' in mode and 'final' in mode:
        lines.append(f"    thickness {_fmt(scene.overallThickness)};")
        lines.append(f"    finalLayerThickness {_fmt(scene.finalLayerThickness)};")
    elif 'overall' in mode and 'expansion' in mode:
        lines.append(f"    thickness {_fmt(scene.overallThickness)};")
        lines.append(f"    expansionRatio {_fmt(scene.expansionRatio)};")

    lines.append(f"    minThickness {_fmt(scene.minThickness)};")
    
    # Layer per patch settings
    if len(scene.layer_patches) > 0:
        lines.append("")
        lines.append("    // Layer per patch settings")
        lines.append("    layers")
        lines.append("    {")
        
        for patch in scene.layer_patches:
            lines.append(f'        "{patch.name}"')
            lines.append("        {")
            lines.append(f"            nSurfaceLayers {patch.nSurfaceLayers};")
            
            if patch.custom_expansion:
                lines.append(f"            expansionRatio      {_fmt(patch.expansionRatio)};")
                lines.append(f"            finalLayerThickness {_fmt(patch.finalLayerThickness)};")
                lines.append(f"            minThickness        {_fmt(patch.minThickness)};")
            
            lines.append("        }")
        
        lines.append("    }")
    
    lines.append("")
    lines.append(f"    nGrow {scene.nGrow};")
    lines.append("")
    lines.append("    // Feature handling")
    lines.append(f"    featureAngle {scene.featureAngle};")
    lines.append(f"    maxFaceThicknessRatio {scene.maxFaceThicknessRatio};")
    lines.append("")
    lines.append("    // Surface normals")
    lines.append(f"    nSmoothSurfaceNormals {scene.nSmoothSurfaceNormals};")
    lines.append(f"    nSmoothThickness {scene.nSmoothThickness};")
    lines.append("")
    lines.append("    // Medial axis")
    lines.append(f"    minMedialAxisAngle {scene.minMedialAxisAngle};")
    lines.append(f"    maxThicknessToMedialRatio {scene.maxThicknessToMedialRatio};")
    lines.append(f"    nSmoothNormals {scene.nSmoothNormals};")
    lines.append("")
    lines.append("    // Mesh shrinking")
    lines.append(f"    slipFeatureAngle {scene.slipFeatureAngle};")
    lines.append(f"    nRelaxIter {scene.layerRelaxIter};")
    lines.append(f"    nBufferCellsNoExtrude {scene.nBufferCellsNoExtrude};")
    lines.append(f"    nLayerIter {scene.nLayerIter};")
    lines.append(f"    nRelaxedIter {scene.nRelaxedIter};")
    
    if scene.additionalReporting:
        lines.append(f"    additionalReporting {str(scene.additionalReporting).lower()};")
    
    if scene.detectExtrusionIsland:
        lines.append(f"    detectExtrusionIsland {str(scene.detectExtrusionIsland).lower()};")
    
    lines.append("}")
    return lines

def generate_quality_subdictionary(scene):
    """Generate the meshQualityControls subdictionary"""
    lines = []
    lines.append("meshQualityControls")
    lines.append("{")

    mesh_quality = scene.mesh_quality
    
    # When including external dictionary
    if mesh_quality.includeMeshQualityDict:
        lines.append(f'    #include "{os.path.basename(mesh_quality.meshQualityDictPath)}";')
        
        # Always include error control parameters
        lines.append("")
        lines.append("    // Error control")
        lines.append(f"    nSmoothScale {_fmt(mesh_quality.nSmoothScale)};")
        lines.append(f"    errorReduction {_fmt(mesh_quality.errorReduction)};")
    else:
        # Standard quality constraints
        lines.append(f"    maxNonOrtho {_fmt(mesh_quality.maxNonOrtho)};")
        lines.append(f"    maxBoundarySkewness {_fmt(mesh_quality.maxBoundarySkewness)};")
        lines.append(f"    maxInternalSkewness {_fmt(mesh_quality.maxInternalSkewness)};")
        lines.append(f"    maxConcave {_fmt(mesh_quality.maxConcave)};")
        lines.append(f"    minVol {_fmt(mesh_quality.minVol)};")
        lines.append(f"    minTetQuality {_fmt(mesh_quality.minTetQuality)};")
        lines.append(f"    minArea {_fmt(mesh_quality.minArea)};")
        lines.append(f"    minTwist {_fmt(mesh_quality.minTwist)};")
        lines.append(f"    minDeterminant {_fmt(mesh_quality.minDeterminant)};")
        lines.append(f"    minFlatness {_fmt(mesh_quality.minFlatness)};")
        lines.append(f"    minWeight {_fmt(mesh_quality.minFaceWeight)};")
        lines.append(f"    minVolRatio {_fmt(mesh_quality.minVolRatio)};")
        lines.append(f"    minTriangleTwist {_fmt(mesh_quality.minTriangleTwist)};")
        
        # Relaxed quality criteria
        relaxed = scene.relaxed_mesh_quality
        relaxed_settings = []
        if hasattr(relaxed, 'use_maxNonOrtho') and relaxed.use_maxNonOrtho:
            relaxed_settings.append(f"        maxNonOrtho {_fmt(relaxed.maxNonOrtho)};")
        if hasattr(relaxed, 'use_maxBoundarySkewness') and relaxed.use_maxBoundarySkewness:
            relaxed_settings.append(f"        maxBoundarySkewness {_fmt(relaxed.maxBoundarySkewness)};")
        if hasattr(relaxed, 'use_maxInternalSkewness') and relaxed.use_maxInternalSkewness:
            relaxed_settings.append(f"        maxInternalSkewness {_fmt(relaxed.maxInternalSkewness)};")
        if hasattr(relaxed, 'use_maxConcave') and relaxed.use_maxConcave:
            relaxed_settings.append(f"        maxConcave {_fmt(relaxed.maxConcave)};")
        if hasattr(relaxed, 'use_minFlatness') and relaxed.use_minFlatness:
            relaxed_settings.append(f"        minFlatness {_fmt(relaxed.minFlatness)};")
        if hasattr(relaxed, 'use_minVol') and relaxed.use_minVol:
            relaxed_settings.append(f"        minVol {_fmt(relaxed.minVol)};")
        if hasattr(relaxed, 'use_minTetQuality') and relaxed.use_minTetQuality:
            relaxed_settings.append(f"        minTetQuality {_fmt(relaxed.minTetQuality)};")
        if hasattr(relaxed, 'use_minArea') and relaxed.use_minArea:
            relaxed_settings.append(f"        minArea {_fmt(relaxed.minArea)};")
        if hasattr(relaxed, 'use_minTwist') and relaxed.use_minTwist:
            relaxed_settings.append(f"        minTwist {_fmt(relaxed.minTwist)};")
        if hasattr(relaxed, 'use_minDeterminant') and relaxed.use_minDeterminant:
            relaxed_settings.append(f"        minDeterminant {_fmt(relaxed.minDeterminant)};")
        if hasattr(relaxed, 'use_minFaceWeight') and relaxed.use_minFaceWeight:
            relaxed_settings.append(f"        minWeight {_fmt(relaxed.minFaceWeight)};")
        if hasattr(relaxed, 'use_minVolRatio') and relaxed.use_minVolRatio:
            relaxed_settings.append(f"        minVolRatio {_fmt(relaxed.minVolRatio)};")
        if hasattr(relaxed, 'use_minTriangleTwist') and relaxed.use_minTriangleTwist:
            relaxed_settings.append(f"        minTriangleTwist {_fmt(relaxed.minTriangleTwist)};")
        
        if relaxed_settings:
            lines.append("")
            lines.append("    // Relaxed quality criteria")
            lines.append("    relaxed")
            lines.append("    {")
            lines.extend(relaxed_settings)
            lines.append("    }")
        
        # Error control
        lines.append("")
        lines.append("    // Error control")
        lines.append(f"    nSmoothScale {_fmt(mesh_quality.nSmoothScale)};")
        lines.append(f"    errorReduction {_fmt(mesh_quality.errorReduction)};")

    lines.append("}")
    return lines

def generate_dictionary_controls_subdictionary(scene):
    """Generate the writeFlags and other dictionary control settings"""
    lines = []
    
    # Add debug flags if enabled
    if hasattr(scene, 'use_debug_flags') and scene.use_debug_flags:
        debug_flags = []
        if hasattr(scene, 'debugFlag_mesh') and scene.debugFlag_mesh:
            debug_flags.append("    mesh            // write intermediate meshes")
        if hasattr(scene, 'debugFlag_intersections') and scene.debugFlag_intersections:
            debug_flags.append("    intersections   // write current mesh intersections as .obj files")
        if hasattr(scene, 'debugFlag_featureSeeds') and scene.debugFlag_featureSeeds:
            debug_flags.append("    featureSeeds    // write information about explicit feature edge refinement")
        if hasattr(scene, 'debugFlag_attraction') and scene.debugFlag_attraction:
            debug_flags.append("    attraction      // write attraction as .obj files")
        if hasattr(scene, 'debugFlag_layerInfo') and scene.debugFlag_layerInfo:
            debug_flags.append("    layerInfo       // write information about layers")
        
        if debug_flags:
            lines.append("// Debug flags")
            lines.append("debugFlags")
            lines.append("(")
            lines.extend(debug_flags)
            lines.append(");")
            lines.append("")
    
    # Write flags
    write_flags = []
    if hasattr(scene, 'writeFlag_scalarLevels') and scene.writeFlag_scalarLevels:
        write_flags.append("    scalarLevels    // write volScalarField with cellLevel for postprocessing")
    if hasattr(scene, 'writeFlag_layerSets') and scene.writeFlag_layerSets:
        write_flags.append("    layerSets       // write cellSets, faceSets of faces in layer")
    if hasattr(scene, 'writeFlag_layerFields') and scene.writeFlag_layerFields:
        write_flags.append("    layerFields     // write volScalarField for layer coverage")
    
    if write_flags:
        lines.append("// Write flags")
        lines.append("writeFlags")
        lines.append("(")
        lines.extend(write_flags)
        lines.append(");")
    else:
        # Empty write flags section
        lines.append("// Write flags")
        lines.append("writeFlags")
        lines.append("{")
        lines.append("};")
    
    lines.append("")
    
    # Always include merge tolerance
    if hasattr(scene, 'mergeTolerance'):
        lines.append(f"mergeTolerance {scene.mergeTolerance};")
    
    return lines

def format_lines_for_preview(lines):
    """Format lines for UI preview display"""
    return lines

def format_lines_for_dictionary(lines):
    """Format lines for final dictionary file output"""
    return "\n".join(lines) + "\n\n"
