# @swafy/map-core

Shared map types, constants, contracts, and fixtures for SWAFY.

## What is inside
- **Types & Enums:** `Category`, `ReportStatus`, `MapReportFeature`, `MapReportCollection`, `BBox`.
- **Component Contract:** `MapComponentProps` — the unified props interface for both mobile and web map components.
- **Styling Constants:** `CATEGORY_STYLES`, `STATUS_STYLES`, `TUNIS_CENTER`, `DEFAULT_TILE_URL`.
- **Fixtures:**
  - `mockReports200`: 200 realistic mock reports around Tunis for everyday development.
  - `mockReports5000`: 5,000 points for clustering and performance testing.

## Example Usage in Mobile or Dashboard
```typescript
import { 
  mockReports200, 
  CATEGORY_STYLES, 
  type MapComponentProps 
} from '@swafy/map-core';

// Use mockReports200 directly as your initial map props
<MapComponent reports={mockReports200} />