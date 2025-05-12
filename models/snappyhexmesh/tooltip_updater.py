"""
Tooltip Updater module - Updates property descriptions with detailed tooltips.
This approach allows us to keep detailed tooltips in a separate file but still
use them in the Blender UI via property descriptions.
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
    """Updates property descriptions with detailed tooltips from our tooltips files"""
    
    # Castellated mesh properties
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
    
    # Snap properties
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
    
    # Layer addition properties
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
    
    # Mesh quality properties
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
    """Updates the description of a single property"""
    # Ensure the property exists in scene and in tooltip dictionary
    if hasattr(bpy.types.Scene, prop_name) and prop_name in tooltip_dict:
        prop = getattr(bpy.types.Scene, prop_name)
        # Get property definition
        if hasattr(prop, "__annotations__"):
            # Find the property definition and update its description
            for key, value in prop.__annotations__.items():
                if key == prop_name:
                    # Update description
                    value[1]["description"] = tooltip_dict[prop_name]
                    break
        # For directly defined properties
        elif hasattr(prop, "keywords") and "description" in prop.keywords:
            prop.keywords["description"] = tooltip_dict[prop_name]

def register():
    """Called when the addon is enabled"""
    # Update tooltips after all properties are registered
    update_property_descriptions()

def unregister():
    """Called when the addon is disabled"""
    pass
