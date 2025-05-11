"""
SnappyHexMesh tooltips module - Contains detailed descriptions for SnappyHexMesh UI elements.
These will be shown when hovering over UI elements to provide in-depth information to users.
"""

# Castellation tooltips
CASTELLATED_TOOLTIPS = {
    # General settings
    "castellatedMesh": "Enable mesh refinement based on geometry features. When enabled, SnappyHexMesh will perform refinement by splitting cells based on geometry features, refinement regions, etc.",
    
    # Global refinement parameters
    "maxLocalCells": "Maximum number of cells per CPU core during parallel mesh creation. Prevents single processors from running out of memory. Reduce this if you encounter memory issues.",
    "maxGlobalCells": "Upper limit on the total number of cells in the entire mesh. The refinement will stop when reaching this limit, regardless of whether all refinement criteria are met.",
    "minRefinementCells": "Minimum number of cells to be refined. Prevents refinement of very small numbers of cells for efficiency.",
    "maxLoadUnbalance": "Maximum acceptable load imbalance between processors during parallel refinement. Values between 0.0-1.0, with 0.1 being a 10% imbalance.",
    "nCellsBetweenLevels": "Number of transition cells required between different refinement levels. Higher values create smoother transitions but more cells. Default is 2.",
    
    # Feature edge refinement
    "feature_file": "Path to feature edge file (.eMesh) containing explicit edges for refinement. These are typically sharp edges extracted from the geometry.",
    "refinement_mode": "Method used to specify refinement levels:\n• Uniform Level: Same level everywhere\n• Single Distance: One distance-level pair\n• Multiple Distances: Distance-based gradual refinement",
    "feature_level": "Refinement level for feature edges. Higher values create more cells and better capture feature details.",
    "feature_distance": "Distance from feature edge where refinement should be applied. Measured in units of the mesh.",
    "feature_level_at_distance": "Refinement level at the specified distance from the feature.",
    
    # Feature angle settings
    "resolveFeatureAngle": "Angle threshold (in degrees) for implicit feature edge detection. Edges with a larger angle between connected faces will be treated as features. Default is 30°.",
    "planarAngle": "Angle threshold (in degrees) for determining which edges are treated as planar (smooth). If not specified, resolveFeatureAngle will be used.",
    
    # Surface refinement
    "use_gap_level": "Enable additional refinement in narrow gaps between surfaces.",
    "gap_level_increment": "Number of additional refinement levels to add in narrow gaps between surfaces. This helps ensure sufficient cells in tight spaces.",
    "surface_name": "Name identifying the surface in the output mesh and logs.",
    "source_type": "Source of the geometry:\n• Geometry Object: Blender mesh object\n• STL File: Imported STL geometry",
    "min_level": "Minimum refinement level required for this surface. This level is guaranteed throughout the surface.",
    "max_level": "Maximum refinement level allowed for this surface. Higher refinement occurs only at curvature or regions.",
    
    # Zone settings
    "face_zone": "Name for the face zone to be created from this surface. Leave empty for no face zone.",
    "cell_zone": "Name for the cell zone to be created from this surface. Leave empty for no cell zone.",
    "cell_zone_inside": "For enclosed surfaces with cell zones, defines which side is considered 'inside'.",
    
    # Region settings
    "region_name": "Name identifying this region in the refinement specification.",
    "region_mode": "Refinement method:\n• Inside: Refine cells inside the region\n• Distance: Refine cells at specific distances from region",
    "region_level": "Refinement level to apply inside this region.",
    "use_advanced_distance": "Enable multiple distance-level pairs for more gradual transition in refinement.",
    "region_distance": "Distance from region boundary for refinement application.",
    "region_level_at_distance": "Refinement level to apply at the specified distance.",
    
    # Mesh selection
    "locationInMesh": "Coordinates of a point that must be inside the mesh after castellated mesh creation. Used to determine which side of surfaces should be meshed.",
    "allowFreeStandingZoneFaces": "Allow creation of face zones even if they are not bounded by cell zones. Enabled by default.",
    "handleSnapProblems": "Keep cells that might cause snapping problems in later stages. Optional, disabled by default.",
    "useTopologicalSnapDetection": "Use topological test instead of geometric test for detecting cells to be squashed. Optional, enabled by default."
}

# Snap tooltips
SNAP_TOOLTIPS = {
    "snap": "Enable surface snapping phase. Adjusts the mesh to match the surface geometry more closely.",
    "tolerance": "Maximum relative distance for point attraction to surface. Smaller values enforce more accurate surface matching but may cause issues.",
    "nSmoothPatch": "Number of smoothing iterations for surface point locations before finding nearest surface.",
    "nSolveIter": "Number of mesh displacement relaxation iterations. Higher values may improve quality but increase computational time.",
    "nRelaxIter": "Maximum number of snapping relaxation iterations. Reduces mesh distortion but increases computational time.",
    "useFeatureSnap": "Enable snapping to feature edges. Helps maintain sharp edges in the final mesh.",
    "nFeatureSnapIter": "Number of iterations for feature edge snapping. Higher values improve results but increase computational time.",
    "implicitFeatureSnap": "Detect features automatically by sampling the surface. Can detect features that aren't explicitly specified.",
    "explicitFeatureSnap": "Use feature edges specified in castellatedMeshControls section. Precise control over which edges to snap to.",
    "multiRegionFeatureSnap": "Enable feature snapping for multiple surfaces. Important for complex geometry with multiple regions."
}

# Layer addition tooltips
LAYER_TOOLTIPS = {
    "addLayers": "Enable boundary layer addition. Creates layers of cells near wall boundaries for better flow resolution.",
    "relativeSizes": "Interpret layer parameters relative to local cell size instead of absolute values.",
    "thickness_mode": "Method for specifying layer thickness:\n• Expansion + Final Layer: Define expansion ratio and final layer thickness\n• Expansion + First Layer: Define expansion ratio and first layer thickness\n• Overall + First Layer: Define overall thickness and first layer thickness\n• Overall + Final Layer: Define overall thickness and final layer thickness\n• Overall + Expansion: Define overall thickness and expansion ratio",
    "expansionRatio": "Expansion factor between consecutive layers. A value of 1.2 means each layer is 1.2 times thicker than the previous layer.",
    "finalLayerThickness": "Thickness of layer furthest from the wall (outer layer). Used when thickness mode includes 'Final Layer'.",
    "firstLayerThickness": "Thickness of layer closest to the wall (inner layer). Used when thickness mode includes 'First Layer'.",
    "overallThickness": "Total thickness of all layers combined. Used when thickness mode includes 'Overall'.",
    "minThickness": "Minimum thickness allowed for any layer. Layers thinner than this will be removed.",
    
    # Advanced layer settings
    "featureAngle": "Angle threshold for layer termination at feature edges. Layers won't continue around features sharper than this angle.",
    "nGrow": "Number of extra face layers to extrude. Helps with complex geometries to create smoother transitions.",
    "maxFaceThicknessRatio": "Maximum ratio of layer thickness to local cell size. Prevents very thick layers in small cells.",
    "nSmoothSurfaceNormals": "Number of smoothing iterations for surface normals. Helps with layer quality on complex surfaces.",
    "nSmoothThickness": "Number of smoothing iterations for layer thickness. Prevents abrupt changes in layer thickness.",
    "minMedialAxisAngle": "Angle used to identify medial axis features. Affects layer behavior in corners and tight spaces.",
    "maxThicknessToMedialRatio": "Controls layer thickness near medial axis. Reduces growth where thickness to medial distance is large.",
    "nSmoothNormals": "Number of iterations for smoothing mesh motion direction. Improves layer quality but increases computational time.",
    "slipFeatureAngle": "Angle above which boundary layer can slip. Helps with complex geometries with sharp features.",
    "layerRelaxIter": "Maximum number of snapping relaxation iterations for the layer addition phase.",
    "nBufferCellsNoExtrude": "Number of buffer cells with no extrusion. Creates a buffer zone for smoother layer transitions.",
    "nLayerIter": "Maximum number of layer addition iterations. Higher values may improve quality but increase computational time.",
    "nRelaxedIter": "Number of iterations after which the algorithm switches to relaxed mesh quality constraints.",
    "additionalReporting": "Generate detailed reports about problematic face centers during layer addition. Useful for debugging."
}

# Mesh quality tooltips
QUALITY_TOOLTIPS = {
    "includeMeshQualityDict": "Use an external meshQualityDict file for quality settings. Provides more control and reusability.",
    "meshQualityDictPath": "Path to the external meshQualityDict file. Can be relative to the system directory.",
    "maxNonOrtho": "Maximum non-orthogonality allowed (0-180 degrees). Lower values enforce better quality but may prevent mesh completion.",
    "maxBoundarySkewness": "Maximum boundary face skewness allowed. Controls the quality of boundary faces.",
    "maxInternalSkewness": "Maximum internal face skewness allowed. Controls the quality of internal faces.",
    "maxConcave": "Maximum concaveness allowed (0-180 degrees). Controls cell shape quality.",
    "minFlatness": "Minimum face flatness (0-1). Ratio of minimum projected area to actual area.",
    "minVol": "Minimum cell volume allowed. Very small cells might cause numerical issues.",
    "minTetQuality": "Minimum quality of tetrahedral cells (0-1). Controls the quality of tet cells.",
    "relaxedMaxNonOrtho": "Maximum non-orthogonality allowed in relaxed mode. Used during specific phases like layer addition.",
    "nSmoothScale": "Number of error distribution iterations. Used to adjust the mesh to meet quality requirements.",
    "errorReduction": "Factor to scale back displacement at error points (0-1). Controls how aggressively errors are corrected."
}

# Dictionary settings tooltips
DICTIONARY_TOOLTIPS = {
    "writeFlag_scalarLevels": "Write cellLevel field for visualization of refinement levels.",
    "writeFlag_layerSets": "Write cellSets, faceSets of layers for visualization.",
    "writeFlag_layerFields": "Write layer coverage as fields for visualization.",
    "mergeTolerance": "Fraction of overall bounding box for point merging. Controls tolerance for vertex merging."
}
