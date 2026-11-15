import { generateMockReports } from './generator';
import type { MapReportCollection } from '../types';

/**
 * Fixture: 5,000 mock reports around Greater Tunis.
 * Used for stress-testing pin clustering, spatial queries, and map performance (< 3s load).
 */
export const mockReports5000: MapReportCollection = generateMockReports(5000, 202);