import { Camera, Map, type StyleSpecification } from '@maplibre/maplibre-react-native';
import { StyleSheet } from 'react-native';

/**
 * Week-1 check (issue #11): proves the native MapLibre library works in the
 * development build. It will be replaced by the component from
 * packages/map-mobile once the map team publishes it.
 */

// OpenStreetMap raster tiles, as chosen in the architecture report.
// Fine for development; heavy public traffic needs another tile source.
const OSM_STYLE: StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '© OpenStreetMap contributors',
    },
  },
  layers: [{ id: 'osm', type: 'raster', source: 'osm' }],
};

// Tunis city centre, as [longitude, latitude].
const TUNIS: [number, number] = [10.1815, 36.8065];

export function MapCheck() {
  return (
    <Map style={styles.map} mapStyle={OSM_STYLE}>
      <Camera initialViewState={{ center: TUNIS, zoom: 12 }} />
    </Map>
  );
}

const styles = StyleSheet.create({
  map: {
    flex: 1,
  },
});
