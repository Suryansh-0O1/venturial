import os
import bpy
from .dictionary_writers import (
    generate_geometry_subdictionary,
    generate_castellated_subdictionary,
    generate_snap_subdictionary,
    generate_layer_subdictionary,
    generate_quality_subdictionary,
    generate_dictionary_controls_subdictionary
)

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

def format_lines_for_dictionary(lines):
    """Format lines for final dictionary file output"""
    return "\n".join(lines) + "\n\n"

def generate_snappy_dict(scene):
    """Generate the complete snappyHexMesh dictionary using subdictionary writers"""
    full_dict = write_header()
    full_dict += write_mesh_controls(scene)
    
    # Use the same functions that generate previews
    if scene.castellatedMesh or len(scene.geometry_items) > 0 or scene.stl_file_name:
        geometry_lines = generate_geometry_subdictionary(scene)
        full_dict += format_lines_for_dictionary(geometry_lines)
    
    if scene.castellatedMesh:
        castellated_lines = generate_castellated_subdictionary(scene)
        full_dict += format_lines_for_dictionary(castellated_lines)
    
    if scene.snap:
        snap_lines = generate_snap_subdictionary(scene)
        full_dict += format_lines_for_dictionary(snap_lines)
    
    if scene.addLayers:
        layer_lines = generate_layer_subdictionary(scene)
        if layer_lines:  # Only add if layers are actually enabled
            full_dict += format_lines_for_dictionary(layer_lines)
    
    # Always include mesh quality controls
    quality_lines = generate_quality_subdictionary(scene)
    full_dict += format_lines_for_dictionary(quality_lines)
    
    # Dictionary controls
    dict_control_lines = generate_dictionary_controls_subdictionary(scene)
    full_dict += format_lines_for_dictionary(dict_control_lines)
    
    full_dict += "// ************************************************************************* //\n"
    
    return full_dict

def write_snappy_dict_to_file(scene, filepath):
    """Write the generated snappyHexMesh dictionary to a file"""
    try:
        with open(filepath, 'w') as f:
            f.write(generate_snappy_dict(scene))
        return True
    except Exception as e:
        print(f"Error writing snappyHexMeshDict: {e}")
        return False
