import os
import bpy

def write_header():
    """Generate the header for the snappyHexMesh dictionary"""
    # Keep the standard OpenFOAM header as is
    header = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  4.x                                   |
|   \\\\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\\\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      snappyHexMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

"""
    return header

def write_mesh_controls(scene):
    """Write the basic mesh controls section"""
    mesh_controls = f"""// Steps to run
castellatedMesh {str(scene.castellatedMesh).lower()};
snap            {str(scene.snap).lower()};
addLayers       {str(scene.addLayers).lower()};

"""
    return mesh_controls

def write_geometry_section(scene):
    """Generate the geometry section of the dictionary"""
    geometry_section = """// Geometry
geometry
{
"""
    
    # Add geometry items
    for index, item in enumerate(scene.geometry_items):
        obj = bpy.data.objects.get(item.name)
        if not obj:
            continue
            
        if obj.type == 'MESH':
            if hasattr(obj, 'data') and hasattr(obj.data, 'primitives'):
                # This is likely a primitive like a box, sphere, etc.
                if "cube" in obj.name.lower() or "box" in obj.name.lower():
                    # Handle box geometry
                    bounds = obj.bound_box
                    min_x = min(p[0] for p in bounds) + obj.location.x - obj.scale.x
                    min_y = min(p[1] for p in bounds) + obj.location.y - obj.scale.y
                    min_z = min(p[2] for p in bounds) + obj.location.z - obj.scale.z
                    max_x = max(p[0] for p in bounds) + obj.location.x + obj.scale.x
                    max_y = max(p[1] for p in bounds) + obj.location.y + obj.scale.y
                    max_z = max(p[2] for p in bounds) + obj.location.z + obj.scale.z
                    
                    geometry_section += f"""    {obj.name}
    {{
        type searchableBox;
        min ({min_x} {min_y} {min_z});
        max ({max_x} {max_y} {max_z});
    }}

"""
                elif "sphere" in obj.name.lower():
                    # Handle sphere geometry
                    radius = obj.scale.x  # Assuming uniform scale
                    geometry_section += f"""    {obj.name}
    {{
        type searchableSphere;
        centre ({obj.location.x} {obj.location.y} {obj.location.z});
        radius {radius};
    }}

"""
            else:
                # Assume this is an STL file
                geometry_section += f"""    {obj.name}
    {{
        type triSurfaceMesh;
    }}

"""
    
    geometry_section += "};\n\n"
    return geometry_section

def write_castellated_controls(scene):
    """Generate the castellatedMeshControls section"""
    castellated_section = """// Castellated mesh settings
castellatedMeshControls
{
    // Refinement parameters
    maxLocalCells """ + str(scene.maxLocalCells) + """;
    maxGlobalCells """ + str(scene.maxGlobalCells) + """;
    minRefinementCells """ + str(scene.minRefinementCells) + """;
    maxLoadUnbalance """ + str(scene.maxLoadUnbalance) + """;
    nCellsBetweenLevels """ + str(scene.nCellsBetweenLevels) + """;

    // Feature refinement
    features
    (
"""
    
    # Add features
    for feature in scene.cast_features:
        if feature.file:
            feature_entry = f"        {{\n            file \"{os.path.basename(feature.file)}\";\n"
            
            if feature.use_levels:
                feature_entry += f"            levels (({feature.distance} {feature.level_at_distance}));\n"
            else:
                feature_entry += f"            level {feature.level};\n"
                
            feature_entry += "        }\n"
            castellated_section += feature_entry
    
    castellated_section += """    );

    // Surface refinement
    refinementSurfaces
    {
"""
    
    # Add refinement surfaces
    for surface in scene.cast_refinement_surfaces:
        surface_entry = f"        {surface.name}\n        {{\n"
        surface_entry += f"            level ({surface.min_level} {surface.max_level});\n"
        
        # Add regions if any
        if len(surface.regions) > 0:
            surface_entry += "\n            regions\n            {\n"
            for region in surface.regions:
                surface_entry += f"                {region.name}\n                {{\n"
                surface_entry += f"                    level ({region.min_level} {region.max_level});\n"
                surface_entry += "                }\n"
            surface_entry += "            }\n"
        
        # Add patch info if used
        if surface.use_patch_info:
            patch_info = surface.patch_info
            surface_entry += "\n            patchInfo\n            {\n"
            surface_entry += f"                type {patch_info.type};\n"
            surface_entry += f"                inGroups ({patch_info.in_group});\n"
            surface_entry += "            }\n"
        
        # Add gap level if used
        if surface.use_gap_level:
            surface_entry += f"\n            gapLevelIncrement {surface.gap_level_increment};\n"
        
        # Add perpendicular angle if used
        if surface.use_perpendicular_angle:
            surface_entry += f"            perpendicularAngle {surface.perpendicular_angle};\n"
        
        surface_entry += "        }\n"
        castellated_section += surface_entry
    
    castellated_section += """    }

    resolveFeatureAngle """ + str(scene.resolveFeatureAngle if hasattr(scene, 'resolveFeatureAngle') else 30) + """;
    planarAngle """ + str(scene.planarAngle if hasattr(scene, 'planarAngle') else 30) + """;

    // Region refinement
    refinementRegions
    {
"""
    
    # Add refinement regions
    for region in scene.cast_refinement_regions:
        region_entry = f"        {region.name}\n        {{\n"
        region_entry += f"            mode {region.mode};\n"
        
        if region.mode == 'distance':
            region_entry += f"            levels (({region.distance} {region.level_at_distance}));\n"
        else: # inside or outside
            region_entry += f"            levels (({1.0} {region.level}));\n"
        
        region_entry += "        }\n"
        castellated_section += region_entry
    
    castellated_section += """    }

    locationInMesh (""" + f"{scene.locationInMeshX} {scene.locationInMeshY} {scene.locationInMeshZ}" + """);
    allowFreeStandingZoneFaces """ + str(scene.allowFreeStandingZoneFaces).lower() + """;
}

"""
    return castellated_section

def write_snap_controls(scene):
    """Generate the snapControls section"""
    snap_section = """// Snapping settings
snapControls
{
    nSmoothPatch """ + str(scene.nSmoothPatch) + """;
    tolerance """ + str(scene.tolerance) + """;
    nSolveIter """ + str(scene.nSolveIter) + """;
    nRelaxIter """ + str(scene.nRelaxIter) + """;
"""

    if scene.useFeatureSnap:
        snap_section += f"""
    // Feature snapping
    nFeatureSnapIter {scene.nFeatureSnapIter};
    implicitFeatureSnap {str(scene.implicitFeatureSnap).lower()};
    explicitFeatureSnap {str(scene.explicitFeatureSnap).lower()};
    multiRegionFeatureSnap {str(scene.multiRegionFeatureSnap).lower()};
"""

    snap_section += """}

"""
    return snap_section

def write_layer_controls(scene):
    """Generate the addLayersControls section"""
    if not scene.addLayers:
        return ""
        
    layer_section = """// Layer addition settings
addLayersControls
{
    relativeSizes """ + str(scene.relativeSizes).lower() + """;
"""
    
    # Add the thickness specification based on the selected mode
    mode = scene.thickness_mode
    if 'expansion' in mode and 'final' in mode:
        layer_section += f"""
    expansionRatio {scene.expansionRatio};
    finalLayerThickness {scene.finalLayerThickness};
"""
    elif 'expansion' in mode and 'first' in mode:
        layer_section += f"""
    expansionRatio {scene.expansionRatio};
    firstLayerThickness {scene.firstLayerThickness};
"""
    elif 'overall' in mode and 'first' in mode:
        layer_section += f"""
    thickness {scene.overallThickness};
    firstLayerThickness {scene.firstLayerThickness};
"""
    elif 'overall' in mode and 'final' in mode:
        layer_section += f"""
    thickness {scene.overallThickness};
    finalLayerThickness {scene.finalLayerThickness};
"""
    elif 'overall' in mode and 'expansion' in mode:
        layer_section += f"""
    thickness {scene.overallThickness};
    expansionRatio {scene.expansionRatio};
"""

    layer_section += f"""
    minThickness {scene.minThickness};

    // Layer per patch settings
    layers
    {{
"""
    
    # Add layer patches
    for patch in scene.layer_patches:
        layer_section += f"        {patch.name}\n        {{\n"
        layer_section += f"            nSurfaceLayers {patch.nSurfaceLayers};\n"
        
        if patch.custom_expansion:
            layer_section += f"""
            expansionRatio      {patch.expansionRatio};
            finalLayerThickness {patch.finalLayerThickness};
            minThickness        {patch.minThickness};"""
        
        layer_section += "\n        }\n"
    
    layer_section += f"""    }}

    nGrow {scene.nGrow};
    
    // Feature handling
    featureAngle {scene.featureAngle};
    maxFaceThicknessRatio {scene.maxFaceThicknessRatio};
    
    // Surface normals
    nSmoothSurfaceNormals {scene.nSmoothSurfaceNormals};
    nSmoothThickness {scene.nSmoothThickness};
    
    // Medial axis
    minMedialAxisAngle {scene.minMedialAxisAngle};
    maxThicknessToMedialRatio {scene.maxThicknessToMedialRatio};
    nSmoothNormals {scene.nSmoothNormals};
    
    // Mesh shrinking
    slipFeatureAngle {scene.slipFeatureAngle};
    nRelaxIter {scene.layerRelaxIter};
    nBufferCellsNoExtrude {scene.nBufferCellsNoExtrude};
    nLayerIter {scene.nLayerIter};
    nRelaxedIter {scene.nRelaxedIter};
"""
    
    if scene.additionalReporting:
        layer_section += "    additionalReporting true;\n"
    
    layer_section += "}\n\n"
    return layer_section

def write_quality_controls(scene):
    """Generate the meshQualityControls section"""
    quality_section = """// Mesh quality controls
meshQualityControls
{
"""

    if scene.includeMeshQualityDict:
        quality_section += f"""    #include "{scene.meshQualityDictPath}"

"""
    else:
        quality_section += f"""    maxNonOrtho {scene.maxNonOrtho};
    maxBoundarySkewness {scene.maxBoundarySkewness};
    maxInternalSkewness {scene.maxInternalSkewness};
    maxConcave {scene.maxConcave};
    minVol {scene.minVol};
    minTetQuality {scene.minTetQuality};
    minArea -1;
    minTwist 0.02;
    minDeterminant 0.001;
    minFlatness {scene.minFlatness};
    minWeight 0.05;
    minVolRatio 0.01;
    minTriangleTwist -1;
"""

    quality_section += f"""
    // Relaxed quality criteria
    relaxed
    {{
        maxNonOrtho {scene.relaxedMaxNonOrtho};
    }}

    // Error control
    nSmoothScale {scene.nSmoothScale};
    errorReduction {scene.errorReduction};
}}

mergeTolerance 1e-6;

// ************************************************************************* //
"""
    return quality_section

def generate_snappy_dict(scene):
    """Generate the complete snappyHexMesh dictionary"""
    dictionary = write_header()
    dictionary += write_mesh_controls(scene)
    dictionary += write_geometry_section(scene)
    
    if scene.castellatedMesh:
        dictionary += write_castellated_controls(scene)
    
    if scene.snap:
        dictionary += write_snap_controls(scene)
    
    if scene.addLayers:
        dictionary += write_layer_controls(scene)
    
    dictionary += write_quality_controls(scene)
    
    return dictionary

def write_snappy_dict_to_file(scene, filepath):
    """Write the generated dictionary to a file"""
    dictionary = generate_snappy_dict(scene)
    
    try:
        with open(filepath, 'w') as f:
            f.write(dictionary)
        return True
    except Exception as e:
        print(f"Error writing snappyHexMeshDict: {e}")
        return False
