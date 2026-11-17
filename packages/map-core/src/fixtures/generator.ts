import type { Category, MapReportCollection, MapReportFeature, ReportStatus } from '../types';
import { CATEGORIES, REPORT_STATUSES } from '../types';

/**
 * Simple pseudo-random number generator for reproducible fixtures
 */
function seededRandom(seed: number): () => number {
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}

/**
 * Generates deterministic GeoJSON mock reports clustered around Greater Tunis.
 */
export function generateMockReports(count: number, seed = 42): MapReportCollection {
  const rand = seededRandom(seed);

  // Tunis center bounds: Lat ~ 36.75 - 36.88, Lon ~ 10.10 - 10.30
  const minLat = 36.75;
  const maxLat = 36.88;
  const minLon = 10.10;
  const maxLon = 10.30;

  const features: MapReportFeature[] = [];

  for (let i = 1; i <= count; i++) {
    const lat = Number((minLat + rand() * (maxLat - minLat)).toFixed(6));
    const lon = Number((minLon + rand() * (maxLon - minLon)).toFixed(6));
    const category: Category = CATEGORIES[Math.floor(rand() * CATEGORIES.length)];
    const status: ReportStatus = REPORT_STATUSES[Math.floor(rand() * REPORT_STATUSES.length)];
    const confirmations = Math.floor(rand() * 12);

    const featureId = `mock-report-${i.toString().padStart(count >= 1000 ? 5 : 3, '0')}`;

    features.push({
      type: 'Feature',
      id: featureId,
      geometry: {
        type: 'Point',
        coordinates: [lon, lat],
      },
      properties: {
        id: featureId,
        category,
        status,
        created_at: new Date(Date.now() - Math.floor(rand() * 86400000 * 14)).toISOString(),
        confirmations_count: confirmations,
      },
    });
  }

  return {
    type: 'FeatureCollection',
    features,
  };
}