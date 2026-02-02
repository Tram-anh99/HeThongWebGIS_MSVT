# GeoServer Setup Guide for WebGIS MSVT

## Overview
GeoServer is an open-source server for sharing geospatial data. We'll use it to serve heavy OSM layers (roads, buildings) as WMS/WFS tiles instead of importing them directly into PostgreSQL.

## Prerequisites

### 1. Install Java (Required)
GeoServer requires Java 11 or 17.

**Install via Homebrew:**
```bash
# Install OpenJDK 17
brew install openjdk@17

# Link it
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk

# Verify
java -version
```

### 2. Download GeoServer

**Option A: Homebrew (Easiest)**
```bash
# Note: May not have latest version
brew install geoserver
```

**Option B: Download Binary (Recommended)**
1. Visit: https://geoserver.org/download/
2. Download: **Platform Independent Binary**
3. Extract to: `/Users/anllen/Applications/geoserver`

```bash
cd ~/Downloads
wget https://sourceforge.net/projects/geoserver/files/GeoServer/2.24.2/geoserver-2.24.2-bin.zip
unzip geoserver-2.24.2-bin.zip
mv geoserver-2.24.2 /Users/anllen/Applications/geoserver
```

## Installation & Setup

### 1. Start GeoServer

```bash
cd /Users/anllen/Applications/geoserver/bin
./startup.sh
```

GeoServer will start on: **http://localhost:8080/geoserver**

Default credentials:
- **Username**: `admin`
- **Password**: `geoserver`

### 2. Configure PostgreSQL/PostGIS Store

1. Login to GeoServer admin: http://localhost:8080/geoserver/web
2. Go to: **Stores** → **Add new Store**
3. Select: **PostGIS - PostgreSQL/PostGIS Database**
4. Fill in:
   - **Workspace**: Create new "webgis_msvt"
   - **Data Source Name**: "webgis_postgis"
   - **host**: `localhost`
   - **port**: `5432`
   - **database**: `webgis_msvt`
   - **schema**: `public`
   - **user**: `anllen`
   - **password**: (leave empty if using local auth)

5. **Save**

### 3. Publish Layers from PostgreSQL

After creating the store, you can publish layers:

1. Go to: **Layers** → **Add a new layer**
2. Select your PostGIS store
3. Choose tables to publish:
   - `tinh` (36 provinces)
   - `tinh_2025` (34 provinces)
   - `neighboring_countries`
   - `osm_places`
   - `vung_trong` (farms)

4. For each layer:
   - Click **Publish**
   - Set **Native SRS**: `EPSG:4326`
   - Click **Compute from data** for bounding boxes
   - **Save**

### 4. Add OSM Shapefiles as Layers

For OSM data (roads, buildings), add as shapefile stores:

1. **Stores** → **Add new Store**
2. Select: **Shapefile**
3. Fill in:
   - **Data Source Name**: "osm_roads"
   - **Shapefile location**: Browse to:
     `/Users/anllen/LapTrinh/HeThongWebGIS_MSVT/vietnam-latest-free.shp/gis_osm_roads_free_1.shp`

4. Repeat for:
   - `gis_osm_buildings_a_free_1.shp`
   - `gis_osm_landuse_a_free_1.shp`
   - `gis_osm_pois_free_1.shp`

### 5. Configure Layer Styles

For better visualization:

1. **Styles** → **Add a new style**
2. Create SLD styles for:
   - Roads (different colors for highway types)
   - Buildings (gray polygons)
   - Boundaries (colored borders)

Example road style (SLD):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0">
  <NamedLayer>
    <Name>roads</Name>
    <UserStyle>
      <FeatureTypeStyle>
        <Rule>
          <LineSymbolizer>
            <Stroke>
              <CssParameter name="stroke">#888888</CssParameter>
              <CssParameter name="stroke-width">2</CssParameter>
            </Stroke>
          </LineSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
```

## Frontend Integration

### Using WMS in Leaflet

```javascript
// Add GeoServer WMS layer to Leaflet map
const roadsLayer = L.tileLayer.wms('http://localhost:8080/geoserver/webgis_msvt/wms', {
  layers: 'webgis_msvt:osm_roads',
  format: 'image/png',
  transparent: true,
  attribution: 'OSM Data via GeoServer'
});

const buildingsLayer = L.tileLayer.wms('http://localhost:8080/geoserver/webgis_msvt/wms', {
  layers: 'webgis_msvt:osm_buildings',
  format: 'image/png',
  transparent: true
});

// Add to map with layer control
const baseLayers = {};
const overlayLayers = {
  'Roads': roadsLayer,
  'Buildings': buildingsLayer
};

L.control.layers(baseLayers, overlayLayers).addTo(map);
```

### Using WFS for Vector Features

```javascript
// Fetch GeoJSON from GeoServer WFS
const response = await fetch(
  'http://localhost:8080/geoserver/webgis_msvt/ows?' +
  'service=WFS&version=1.0.0&request=GetFeature' +
  '&typeName=webgis_msvt:vung_trong&outputFormat=application/json'
);

const geojson = await response.json();

// Add to Leaflet
L.geoJSON(geojson, {
  onEachFeature: (feature, layer) => {
    layer.bindPopup(feature.properties.ten_vung);
  }
}).addTo(map);
```

## Performance Optimization

### 1. Enable Tile Caching (GeoWebCache)

GeoServer includes GeoWebCache for tile caching:

1. Go to: **Tile Caching** → **Tile Layers**
2. Enable caching for heavy layers (roads, buildings)
3. Set cache directory: `/Users/anllen/Applications/geoserver/data_dir/gwc`

### 2. Configure Memory

Edit `startup.sh`:
```bash
export JAVA_OPTS="-Xms2G -Xmx4G"
```

### 3. Enable Direct Raster Access

For better performance with large datasets:
1. **Settings** → **Global**
2. Enable: **Use GeoServer Specific Pool**

## Testing

### Test WMS Layer

Visit in browser:
```
http://localhost:8080/geoserver/webgis_msvt/wms?
  service=WMS&
  version=1.1.0&
  request=GetMap&
  layers=webgis_msvt:osm_roads&
  bbox=102.0,8.0,110.0,24.0&
  width=768&
  height=768&
  srs=EPSG:4326&
  format=image/png
```

### Test WFS Layer

```
http://localhost:8080/geoserver/webgis_msvt/ows?
  service=WFS&
  version=1.0.0&
  request=GetFeature&
  typeName=webgis_msvt:tinh&
  maxFeatures=10&
  outputFormat=application/json
```

## Troubleshooting

### Port 8080 Already in Use

Change port in `webapps/geoserver/WEB-INF/web.xml` or start script.

### Cannot Connect to PostgreSQL

- Check PostgreSQL is running: `pg_isready`
- Verify connection string and credentials
- Ensure PostGIS extension is enabled

### Layers Not Displaying

- Check SRS/CRS is correct (EPSG:4326)
- Verify bounding box computed correctly
- Check layer preview in GeoServer admin

## Stop GeoServer

```bash
cd /Users/anllen/Applications/geoserver/bin
./shutdown.sh
```

## Auto-Start on Boot (Optional)

Create LaunchAgent:
```bash
nano ~/Library/LaunchAgents/org.geoserver.plist
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>org.geoserver</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/anllen/Applications/geoserver/bin/startup.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Load:
```bash
launchctl load ~/Library/LaunchAgents/org.geoserver.plist
```

## Summary

✅ GeoServer serves heavy OSM layers as WMS/WFS
✅ Frontend loads tiles on-demand (better performance)
✅ No need to import 100MB+ shapefiles to PostgreSQL
✅ Easy layer styling and caching
✅ Supports both raster (WMS) and vector (WFS) outputs
