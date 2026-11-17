import type { Feature, FeatureCollection, Point } from 'geojson';

/**
 * Frozen Categories from docs/contracts/enums.md
 */
export type Category =
  | 'pothole'
  | 'trash'
  | 'graffiti'
  | 'broken_light'
  | 'other';

export const CATEGORIES: readonly Category[] = [
  'pothole',
  'trash',
  'graffiti',
  'broken_light',
  'other',
] as const;

/**
 * Frozen Report Statuses from docs/contracts/enums.md
 */
export type ReportStatus =
  | 'submitted'
  | 'verified'
  | 'in_progress'
  | 'resolved';

export const REPORT_STATUSES: readonly ReportStatus[] = [
  'submitted',
  'verified',
  'in_progress',
  'resolved',
] as const;

/**
 * Properties embedded in GeoJSON report features.
 * Aligns with docs/contracts/openapi.yaml #/components/schemas/ReportFeature
 */
export interface MapReportProperties {
  id: string;
  category: Category;
  status: ReportStatus;
  created_at: string;
  confirmations_count?: number;
}

/**
 * GeoJSON Point Feature representing a Civic Report pin on the map
 */
export type MapReportFeature = Feature<Point, MapReportProperties>;

/**
 * GeoJSON FeatureCollection returned by GET /map/reports
 */
export type MapReportCollection = FeatureCollection<Point, MapReportProperties>;

/**
 * Bounding box as [west, south, east, north] (minLon, minLat, maxLon, maxLat)
 */
export type BBox = [west: number, south: number, east: number, north: number];

/**
 * Filter options for map pins
 */
export interface MapFilters {
  category?: Category[];
  status?: ReportStatus[];
}

/**
 * Map view center coordinates and zoom level
 */
export interface MapViewport {
  center: [longitude: number, latitude: number];
  zoom: number;
}

/**
 * UNIFIED MAP PROPS CONTRACT
 * This interface is implemented by both packages/map-mobile and packages/map-web.
 * Rule from Issue #18: Components receive data through props and never call the API directly.
 */
export interface MapComponentProps {
  /** GeoJSON reports to display as pins/clusters */
  reports: MapReportCollection;
  /** Currently selected report ID, or null */
  selectedId?: string | null;
  /** Callback triggered when a user taps a pin */
  onSelect?: (id: string | null) => void;
  /** Callback triggered when the map viewport moves/zooms */
  onBoundsChange?: (bbox: BBox) => void;
  /** Active category and status filters */
  filters?: MapFilters;
  /** Optional custom tile server URL (falls back to DEFAULT_TILE_URL) */
  tileUrl?: string;
  /** Initial viewport (center & zoom) */
  initialViewport?: MapViewport;
}