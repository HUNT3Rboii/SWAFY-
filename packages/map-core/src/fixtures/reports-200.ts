import { generateMockReports } from './generator';
import type { MapReportCollection } from '../types';

/**
 * Fixture: ~200 mock reports around Tunis for everyday Mobile & Dashboard development.
 * Approved for UI testing by Feiruz (mobile) and Youssef (dashboard).
 */
export const mockReports200: MapReportCollection = generateMockReports(200, 101);