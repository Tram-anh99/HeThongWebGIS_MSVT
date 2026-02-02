#!/usr/bin/env python3
"""
Extract province centroids from GeoJSON
Generates provinceCoordinates.js for frontend use
"""
import json
from pathlib import Path

def calculate_polygon_centroid(coords):
    """Calculate centroid of a polygon using coordinate averaging"""
    if not coords or not coords[0]:
        return None
    
    # coords[0] is the exterior ring
    ring = coords[0]
    x_sum = sum(point[0] for point in ring)
    y_sum = sum(point[1] for point in ring)
    n = len(ring)
    
    return [round(y_sum / n, 4), round(x_sum / n, 4)]  # [lat, lng]

def calculate_multipolygon_centroid(coords):
    """Calculate centroid of a multipolygon"""
    all_points = []
    for polygon in coords:
        if polygon and polygon[0]:
            all_points.extend(polygon[0])
    
    if not all_points:
        return None
    
    x_sum = sum(point[0] for point in all_points)
    y_sum = sum(point[1] for point in all_points)
    n = len(all_points)
    
    return [round(y_sum / n, 4), round(x_sum / n, 4)]  # [lat, lng]

def extract_province_coords(geojson_path):
    """Extract province name → coordinates mapping from GeoJSON"""
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    province_coords = {}
    
    for feature in data['features']:
        name = feature['properties'].get('NAME_1')
        if not name:
            continue
        
        geom = feature['geometry']
        geom_type = geom['type']
        coords = geom['coordinates']
        
        if geom_type == 'Polygon':
            centroid = calculate_polygon_centroid(coords)
        elif geom_type == 'MultiPolygon':
            centroid = calculate_multipolygon_centroid(coords)
        else:
            print(f"Warning: Unknown geometry type {geom_type} for {name}")
            continue
        
        if centroid:
            province_coords[name] = centroid
    
    return province_coords

def generate_js_file(province_coords, output_path):
    """Generate JavaScript file with province coordinates"""
    js_content = """/**
 * Province Coordinates Mapping
 * Auto-generated from 63tinh-quandao.geojson
 * Contains centroids of 65 Vietnam provinces and islands
 */

export const PROVINCE_COORDS = """
    
    js_content += json.dumps(province_coords, ensure_ascii=False, indent=2)
    js_content += """

/**
 * Get coordinates for a province name
 * @param {string} provinceName - Name of province (e.g., "Hà Nội")
 * @returns {[number, number]} [latitude, longitude] or Vietnam center if not found
 */
export function getProvinceCoords(provinceName) {
  // Try exact match first
  if (PROVINCE_COORDS[provinceName]) {
    return PROVINCE_COORDS[provinceName]
  }
  
  // Try case-insensitive match
  const normalizedName = provinceName.trim()
  for (const [key, value] of Object.entries(PROVINCE_COORDS)) {
    if (key.toLowerCase() === normalizedName.toLowerCase()) {
      return value
    }
  }
  
  // Default to Vietnam center
  console.warn(`Province "${provinceName}" not found, using Vietnam center`)
  return [14.0583, 108.2772]
}
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)

if __name__ == '__main__':
    geojson_path = Path('Frontend/public/data/63tinh-quandao.geojson')
    output_path = Path('Frontend/src/utils/provinceCoordinates.js')
    
    # Create utils directory if not exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Reading GeoJSON from: {geojson_path}")
    province_coords = extract_province_coords(geojson_path)
    
    print(f"Extracted {len(province_coords)} provinces")
    print("Sample coordinates:")
    for i, (name, coords) in enumerate(list(province_coords.items())[:5]):
        print(f"  {name}: {coords}")
    
    generate_js_file(province_coords, output_path)
    print(f"\nGenerated: {output_path}")
    print("✓ Province coordinates ready for use!")
