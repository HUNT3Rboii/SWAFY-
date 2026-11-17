import type { Category, ReportStatus, MapViewport } from './types';

/**
 * Default Tunis City Centre View
 * Longitude: 10.1815, Latitude: 36.8065 (GeoJSON standard order: [lon, lat])
 */
export const TUNIS_CENTER: [longitude: number, latitude: number] = [10.1815, 36.8065];

export const DEFAULT_ZOOM = 12;

export const DEFAULT_VIEWPORT: MapViewport = {
  center: TUNIS_CENTER,
  zoom: DEFAULT_ZOOM,
};

/**
 * OpenStreetMap Tile Server URL.
 * Note: Free public OSM tile servers restrict heavy automated use.
 * For production, configure a custom tile provider via environment variable.
 */
/**
 * Safe declaration for universal environment access (Node, Web, Mobile)
 */
declare const process: { env?: Record<string, string | undefined> } | undefined;

/**
 * OpenStreetMap Tile Server URL.
 * Note: Free public OSM tile servers restrict heavy automated use.
 * For production, configure a custom tile provider via environment variable.
 */
export const DEFAULT_TILE_URL =
  (typeof process !== 'undefined' && process.env?.MAP_TILE_URL) ||
  'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  
/**
 * Category Visual Configuration (Colours & Icon names)
 */
export interface CategoryStyle {
  color: string;
  label: string;
  iconName: string; // Compatible with Lucide / Expo vector icons
}

export const CATEGORY_STYLES: Record<Category, CategoryStyle> = {
  pothole: {
    color: '#D97706', // Amber-600
    label: 'Pothole',
    iconName: 'alert-triangle',
  },
  trash: {
    color: '#059669', // Emerald-600
    label: 'Trash & Waste',
    iconName: 'trash-2',
  },
  graffiti: {
    color: '#7C3AED', // Violet-600
    label: 'Graffiti',
    iconName: 'palette',
  },
  broken_light: {
    color: '#DC2626', // Red-600
    label: 'Broken Streetlight',
    iconName: 'zap-off',
  },
  other: {
    color: '#4B5563', // Gray-600
    label: 'Other',
    iconName: 'help-circle',
  },
};

/**
 * Status Visual Configuration
 */
export interface StatusStyle {
  color: string;
  label: string;
  badgeBg: string;
}

export const STATUS_STYLES: Record<ReportStatus, StatusStyle> = {
  submitted: {
    color: '#2563EB', // Blue-600
    badgeBg: '#DBEAFE',
    label: 'Submitted',
  },
  verified: {
    color: '#D97706', // Amber-600
    badgeBg: '#FEF3C7',
    label: 'Verified',
  },
  in_progress: {
    color: '#4F46E5', // Indigo-600
    badgeBg: '#E0E7FF',
    label: 'In Progress',
  },
  resolved: {
    color: '#16A34A', // Green-600
    badgeBg: '#DCFCE7',
    label: 'Resolved',
  },
};