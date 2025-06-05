"""
Tooltip Updater Module

This module is responsible for synchronizing detailed tooltips from separate tooltip
definition files with Blender property descriptions. It allows for centralized management
of detailed documentation that appears in the Blender UI.

The module updates property descriptions at addon registration time, ensuring that
users have access to comprehensive information about each parameter directly in the UI.
"""

import bpy
from venturial.models.snappyhexmesh.tooltips import (
    CASTELLATED_TOOLTIPS,
    SNAP_TOOLTIPS,
    LAYER_TOOLTIPS,
    QUALITY_TOOLTIPS,
    DICTIONARY_TOOLTIPS
)


def update_property_descriptions():
    """
    Updates all property descriptions with detailed tooltips from tooltip dictionaries.
    
    This function processes all SnappyHexMesh properties by category and applies
    the corresponding tooltip text to each property's description field in Blender.
    """
    
    # Castellated mesh properties
    _update_castellated_properties()
    
    # Snap properties
    _update_snap_properties()
    
    # Layer addition properties
    _update_layer_properties()
    
    # Mesh quality properties
    _update_quality_properties()


def _update_castellated_properties():
    """Update all castellated mesh property descriptions."""
    update_property("castellatedMesh", CASTELLATED_TOOLTIPS)
    update_property("maxLocalCells", CASTELLATED_TOOLTIPS)
    update_property("maxGlobalCells", CASTELLATED_TOOLTIPS)
    update_property("minRefinementCells", CASTELLATED_TOOLTIPS)
    update_property("maxLoadUnbalance", CASTELLATED_TOOLTIPS)
    update_property("nCellsBetweenLevels", CASTELLATED_TOOLTIPS)
    update_property("resolveFeatureAngle", CASTELLATED_TOOLTIPS)
    update_property("planarAngle", CASTELLATED_TOOLTIPS)
    update_property("locationInMeshX", CASTELLATED_TOOLTIPS["locationInMesh"])
    update_property("locationInMeshY", CASTELLATED_TOOLTIPS["locationInMesh"])
    update_property("locationInMeshZ", CASTELLATED_TOOLTIPS["locationInMesh"])
    update_property("allowFreeStandingZoneFaces", CASTELLATED_TOOLTIPS)
    update_property("handleSnapProblems", CASTELLATED_TOOLTIPS)
    update_property("useTopologicalSnapDetection", CASTELLATED_TOOLTIPS)
    update_property("use_gap_level", CASTELLATED_TOOLTIPS)
    update_property("gap_level_increment", CASTELLATED_TOOLTIPS)


def _update_snap_properties():
    """Update all snap control property descriptions."""
    update_property("snap", SNAP_TOOLTIPS)
    update_property("tolerance", SNAP_TOOLTIPS)
    update_property("nSmoothPatch", SNAP_TOOLTIPS)
    update_property("nSolveIter", SNAP_TOOLTIPS)
    update_property("nRelaxIter", SNAP_TOOLTIPS)
    update_property("useFeatureSnap", SNAP_TOOLTIPS)
    update_property("nFeatureSnapIter", SNAP_TOOLTIPS)
    update_property("implicitFeatureSnap", SNAP_TOOLTIPS)
    update_property("explicitFeatureSnap", SNAP_TOOLTIPS)
    update_property("multiRegionFeatureSnap", SNAP_TOOLTIPS)


def _update_layer_properties():
    """Update all layer addition property descriptions."""
    update_property("addLayers", LAYER_TOOLTIPS)
    update_property("relativeSizes", LAYER_TOOLTIPS)
    update_property("thickness_mode", LAYER_TOOLTIPS)
    update_property("expansionRatio", LAYER_TOOLTIPS)
    update_property("finalLayerThickness", LAYER_TOOLTIPS)
    update_property("firstLayerThickness", LAYER_TOOLTIPS)
    update_property("overallThickness", LAYER_TOOLTIPS)
    update_property("minThickness", LAYER_TOOLTIPS)
    update_property("featureAngle", LAYER_TOOLTIPS)
    update_property("nGrow", LAYER_TOOLTIPS)
    update_property("maxFaceThicknessRatio", LAYER_TOOLTIPS)
    update_property("nSmoothSurfaceNormals", LAYER_TOOLTIPS)
    update_property("nSmoothThickness", LAYER_TOOLTIPS)
    update_property("minMedialAxisAngle", LAYER_TOOLTIPS)
    update_property("maxThicknessToMedialRatio", LAYER_TOOLTIPS)
    update_property("nSmoothNormals", LAYER_TOOLTIPS)
    update_property("slipFeatureAngle", LAYER_TOOLTIPS)
    update_property("layerRelaxIter", LAYER_TOOLTIPS)
    update_property("nBufferCellsNoExtrude", LAYER_TOOLTIPS)
    update_property("nLayerIter", LAYER_TOOLTIPS)
    update_property("nRelaxedIter", LAYER_TOOLTIPS)
    update_property("additionalReporting", LAYER_TOOLTIPS)
    update_property("detectExtrusionIsland", LAYER_TOOLTIPS)


def _update_quality_properties():
    """Update all mesh quality property descriptions."""
    update_property("includeMeshQualityDict", QUALITY_TOOLTIPS)
    update_property("meshQualityDictPath", QUALITY_TOOLTIPS)
    update_property("maxNonOrtho", QUALITY_TOOLTIPS)
    update_property("maxBoundarySkewness", QUALITY_TOOLTIPS)
    update_property("maxInternalSkewness", QUALITY_TOOLTIPS)
    update_property("maxConcave", QUALITY_TOOLTIPS)
    update_property("minFlatness", QUALITY_TOOLTIPS)
    update_property("minVol", QUALITY_TOOLTIPS)
    update_property("minTetQuality", QUALITY_TOOLTIPS)
    update_property("relaxedMaxNonOrtho", QUALITY_TOOLTIPS)
    update_property("nSmoothScale", QUALITY_TOOLTIPS)
    update_property("errorReduction", QUALITY_TOOLTIPS)


def update_property(prop_name, tooltip_dict):
    """
    Updates the description of a single property with its tooltip text.
    
    Args:
        prop_name (str): The name of the property to update
        tooltip_dict (dict): Dictionary containing tooltip texts keyed by property name
    
    Returns:
        bool: True if the property was successfully updated, False otherwise
    """
    # Validate inputs
    if not prop_name or not isinstance(tooltip_dict, dict):
        return False
        
    # Check if property exists in Scene and in tooltip dictionary
    if not hasattr(bpy.types.Scene, prop_name):
        return False
        
    # Get tooltip text
    tooltip_text = None
    if prop_name in tooltip_dict:
        tooltip_text = tooltip_dict[prop_name]
    else:
        return False
    
    prop = getattr(bpy.types.Scene, prop_name)
    
    try:
        if hasattr(prop, "__annotations__"):
            for key, value in prop.__annotations__.items():
                if key == prop_name:
                    value[1]["description"] = tooltip_text
                    return True
                    
        elif hasattr(prop, "keywords") and "description" in prop.keywords:
            prop.keywords["description"] = tooltip_text
            return True
            
    except (KeyError, AttributeError, TypeError) as e:
        import logging
        logging.debug(f"Failed to update tooltip for {prop_name}: {str(e)}")
        
    return False


def register():
    """
    Called when the addon is enabled.
    
    Updates all tooltips after properties are registered.
    """
    update_property_descriptions()


def unregister():
    """
    Called when the addon is disabled.
    
    No special action needed for tooltips when unregistering.
    """
    pass
