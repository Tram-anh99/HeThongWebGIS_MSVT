#!/usr/bin/env python3
"""
Convert Vietnam Admin Boundary Shapefile to GeoJSON
Converts 63Tinh_QuanDao.shp to web-compatible GeoJSON format
"""

import geopandas as gpd
import json
from pathlib import Path

def convert_shapefile_to_geojson():
    """Convert shapefile to simplified GeoJSON"""
    
    # Paths
    base_dir = Path(__file__).parent.parent.parent
    shp_path = base_dir / 'Database/data_space/VNM_adm/63Tinh_QuanDao.shp'
    output_path = base_dir / 'Frontend/public/data/vietnam-provinces.geojson'
    
    print(f"Reading shapefile from: {shp_path}")
    
    # Read shapefile
    gdf = gpd.read_file(shp_path)
    
    print(f"Number of features: {len(gdf)}")
    print(f"Original CRS: {gdf.crs}")
    print(f"Columns: {list(gdf.columns)}")
    
    # Convert to WGS84 (EPSG:4326) for web compatibility
    if gdf.crs != 'EPSG:4326':
        print("Converting to EPSG:4326...")
        gdf = gdf.to_crs(epsg=4326)
    
    # Simplify geometry for better performance
    print("Simplifying geometries...")
    original_size = len(str(gdf.to_json()))
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.01, preserve_topology=True)
    simplified_size = len(str(gdf.to_json()))
    
    print(f"Size reduction: {original_size:,} -> {simplified_size:,} bytes ({100 - simplified_size/original_size*100:.1f}% reduction)")
    
    # Save as GeoJSON
    print(f"Saving to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output_path, driver='GeoJSON')
    
    # Get file size
    file_size = output_path.stat().st_size
    print(f"\n✅ Conversion complete!")
    print(f"Output file: {output_path}")
    print(f"File size: {file_size / 1024:.1f} KB")
    print(f"Features: {len(gdf)}")
    
    # Show sample properties
    if len(gdf) > 0:
        print(f"\nSample feature properties:")
        first_feature = gdf.iloc[0]
        for col in gdf.columns:
            if col != 'geometry':
                print(f"  - {col}: {first_feature[col]}")

if __name__ == '__main__':
    convert_shapefile_to_geojson()
