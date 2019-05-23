# -*- coding: utf-8 -*-
#! python3
"""
Data processing for modeling seabeach amaranth habitat
Author: Emily Sturdivant, Ben Gutierrez
email: esturdivant@usgs.gov; bgutierrez@usgs.gov
"""
import os
import arcpy
import time
import pandas as pd


"""
FUNCTIONS
"""

def RasterToLandPerimeter(in_raster, out_polygon, threshold,
    agg_dist='30 METERS', min_area='300 SquareMeters',
    min_hole_sz='300 SquareMeters', manualadditions=None):
    """
    Raster to Polygon: DEM => Reclass => MHW line
    """
    r2p = os.path.join(arcpy.env.scratchGDB, out_polygon+'_r2p_temp')
    r2p_union = os.path.join(arcpy.env.scratchGDB, out_polygon+'_r2p_union_temp')

    # Reclassify the DEM: 1 = land above threshold; the rest is nodata
    rastertemp = arcpy.sa.Con(arcpy.sa.Raster(in_raster)>threshold, 1, None)  # temporary layer classified from threshold
    # Convert the reclass raster to a polygon
    arcpy.RasterToPolygon_conversion(rastertemp, r2p)  # polygon outlining the area above MHW
    if manualadditions: # Manually digitized any large areas missed by the lidar
        arcpy.Union_analysis([manualadditions,r2p], r2p_union, gaps='NO_GAPS')
        arcpy.AggregatePolygons_cartography(r2p_union, out_polygon, agg_dist, min_area, min_hole_sz)
    else:
        arcpy.AggregatePolygons_cartography(r2p, out_polygon, agg_dist, min_area, min_hole_sz)
    print('Aggregation distance: {}\nMinimum area: {}\nMinimum hole size: {}'.format(agg_dist, min_area, min_hole_sz))
    return(out_polygon)

def CombineShorelinePolygons(bndMTL: str, bndMHW: str, inletLines: str,
    ShorelinePts: str, bndpoly: str, SA_bounds: str='', verbose: bool=True):
    """
    Use MTL and MHW contour polygons to create shoreline polygon.
    'Shoreline' = MHW on oceanside and MTL on bayside
    """
    start = time.clock()
    # Inlet lines must intersect the MHW polygon
    symdiff = os.path.join(arcpy.env.scratchGDB, 'shore_1symdiff')
    split = os.path.join(arcpy.env.scratchGDB, 'shore_2split')
    join = os.path.join(arcpy.env.scratchGDB, 'shore_3_oceanMTL')
    erase = os.path.join(arcpy.env.scratchGDB, 'shore_4_bayMTL')
    union_2 = os.path.join(arcpy.env.scratchGDB, 'shore_5union')

    # Create layer (symdiff) of land between MTL and MHW and split by inlets
    print("...delineating land between MTL and MHW elevations...")
    arcpy.Delete_management(symdiff) # delete if already exists
    arcpy.SymDiff_analysis(bndMTL, bndMHW, symdiff)

    # Split symdiff at inlets (and SA_bounds)
    print("...removing the MHW-MTL areas on the oceanside...")
    if len(SA_bounds) > 0:
        arcpy.FeatureToPolygon_management([symdiff, inletLines, SA_bounds], split) # Split MTL features at inlets and study area bounds
    else:
        arcpy.FeatureToPolygon_management([symdiff, inletLines], split) # Split MTL features at inlets
    # Isolate polygons touching shoreline points and erase from symdiff
    arcpy.SpatialJoin_analysis(split, ShorelinePts, split+'_join', "#","KEEP_COMMON", match_option="COMPLETELY_CONTAINS")
    arcpy.Erase_analysis(symdiff, split+'_join', erase)

    # Merge bayside MHW-MTL with above-MHW polygon
    arcpy.Union_analysis([erase, bndMHW], union_2)
    arcpy.Dissolve_management(union_2, bndpoly, multi_part='SINGLE_PART') # Dissolve all features in union_2 to single part polygons
    print('''User input required! Select extra features in {} for deletion.\nRecommended technique: select the polygon/s to keep and then Switch Selection.\n'''.format(os.path.basename(bndpoly)))
    return(bndpoly)

def DEMtoFullShorelinePoly(elevGrid, MTL, MHW, inletLines, ShorelinePts, SA_bounds='', suffix=''):
    """Delinate the full shoreline polygon from the DEM.
    Creates the MTL and MHW contour polygons and then combines them."""
    bndMTL = 'bndpoly_mtl' + suffix
    bndMHW = 'bndpoly_mhw' + suffix
    bndpoly = 'bndpoly' + suffix
    print("Creating the MTL contour polgon from the DEM...")
    RasterToLandPerimeter(elevGrid, bndMTL, MTL, agg_dist='10', min_area='300', min_hole_sz='300')  # Polygon of MTL contour
    print("Creating the MHW contour polgon from the DEM...")
    RasterToLandPerimeter(elevGrid, bndMHW, MHW, agg_dist='10', min_area='300', min_hole_sz='300')  # Polygon of MHW contour
    print("Combining the two polygons...")
    bndpoly = CombineShorelinePolygons(bndMTL, bndMHW, inletLines, ShorelinePts, bndpoly, SA_bounds)
    #DeleteTempFiles()
    return(bndpoly)

def NewBNDpoly(old_boundary, modifying_feature, new_bndpoly='boundary_poly', vertexdist='25 METERS', snapdist='25 METERS', verbose=True):
    """Snaps the boundary polygon to the shoreline points anywhere they don't
    already match and as long as as they are within 25 m of each other."""
    # boundary = input line or polygon of boundary to be modified by newline
    typeFC = arcpy.Describe(old_boundary).shapeType
    if typeFC == "Line" or typeFC =='Polyline':
        arcpy.FeatureToPolygon_management(old_boundary, new_bndpoly, '1 METER')
    else:
        if len(os.path.split(new_bndpoly)[0]):
            path = os.path.split(new_bndpoly)[0]
        else:
            path = arcpy.env.workspace
        arcpy.FeatureClassToFeatureClass_conversion(old_boundary, path, os.path.basename(new_bndpoly))
    typeFC = arcpy.Describe(modifying_feature).shapeType
    if typeFC == "Line" or typeFC == "Polyline":
        arcpy.Densify_edit(modifying_feature, 'DISTANCE', vertexdist)
    # elif typeFC == "Point" or typeFC == "Multipoint":
    #     arcpy.PointsToLine_management(modifying_feature, modifying_feature+'_line')
    #     modifying_feature = modifying_feature+'_line'
    #     arcpy.Densify_edit(modifying_feature, 'DISTANCE', vertexdist)
    arcpy.Densify_edit(new_bndpoly, 'DISTANCE', vertexdist)
    #arcpy.Densify_edit(modifying_feature,'DISTANCE',vertexdist)
    arcpy.Snap_edit(new_bndpoly,[[modifying_feature, 'VERTEX',snapdist]]) # Takes a while
    if verbose:
        print("Created: {} ... Should be in your home geodatabase.".format(os.path.basename(new_bndpoly)))
    return new_bndpoly # string name of new polygon

"""
INPUTS
"""
# Files
home = r'\\Mac\stor\Projects\SA_DataProcessing\GDBs'
proj_dir = r'\\Mac\stor\Projects\SA_DataProcessing'
DEM
DLpts
DHpts
SLpts
veg_polys =
plants_xls = r'\\Mac\stor\Projects\SA_DataProcessing\WILD_AMPU_COMBO_01to18.xlsx'


# Parameters
year = 2008
MHW = 0.34
MLW = -0.13
MTL = (MHW + MLW)/2
gridsz = 5

"""
"""
# arcpy.env.workspace = home
# arcpy.env.scratchWorkspace = proj_dir
arcpy.env.overwriteOutput = True 						# Overwrite output?
arcpy.CheckOutExtension("Spatial") 						# Checkout Spatial Analysis extension


"""
SHORELINE
"""
# Create full barrier shoreline
bndpoly = DEMtoFullShorelinePoly(elevGrid_5m, MTL, MHW, inletLines, ShorelinePts)
print('Select features from {} that should not be included in the final shoreline polygon. '.format(bndpoly))
# Snap the boundary polygon to the SL points anywhere they don't already match and as long as as they are within 25 m of each other.
NewBNDpoly(bndpoly, ShorelinePts, barrierBoundary, '25 METERS', '50 METERS')

"""
RASTERS
"""
# Set extent environment to the input DEM
arcpy.env.workspace = home
arcpy.env.extent = DEM
arcpy.env.extent = bndpoly

# Resample to desired analysis size
DEMres = '{}_{}m'.format(DEM, gridsz)
arcpy.Resample_management(DEM, DEMres, gridsz, 'BILINEAR')

# Set Snap Raster environment. All subsequent rasters will align to these cells.
arcpy.env.snapRaster = DEMres

# Make rasters from Elevation
aspect = '{}_aspect'.format(DEMres)
arcpy.Aspect_3d(DEMres, aspect)

slope = '{}_slope'.format(DEMres)
arcpy.Slope_3d(DEMres, slope, 'PERCENT_RISE')

# Make distance rasters
# Distance to dune toes
distDL = os.path.join(home, 'y{}_distDL'.format(year))
outDistDL = arcpy.sa.EucDistance(DLpts, cell_size=gridsz)
outDistDL.save(distDL)
# Distance to dune crests
distDH = os.path.join(home, 'y{}_distDH'.format(year))
outDistDH = arcpy.sa.EucDistance(DHpts, cell_size=gridsz)
outDistDH.save(distDH)
# Distance to shoreline
distSL = os.path.join(home, 'y{}_distSL'.format(year))
outDistSL = arcpy.sa.EucDistance(SLpts, cell_size=gridsz)
outDistSL.save(distSL)

# Make vegetation raster
vegRaster = os.path.join(home, 'y{}_vegtation'.format(year))
arcpy.PolygonToRaster_conversion(veg_polys, value_field=, vegRaster)

"""
Training set
"""
plants_xls
`pd.read_excel(plants_xls)`
