# Migration ownership and workflow

The BE-2 issue explicitly reserves migration authoring for **Atallah**. This directory therefore contains the Alembic environment and template, but intentionally contains no revision authored by another contributor.

The SQLAlchemy models in `src/swafy_api/models/` are the metadata source for Atallah's initial revision. Before creating tables, the revision must enable PostGIS:

```python
op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
```

The initial revision must create the native enums and tables represented in model metadata, and must create `ix_reports_location_gist` using PostgreSQL's GiST access method. Confirm the generated revision includes the PostGIS extension, geometry type, foreign keys, uniqueness constraints, and indexes; Alembic autogenerate does not manage every extension operation automatically.

Once the owner has committed the initial revision:

```powershell
# From apps/api, with the API environment loaded
alembic upgrade head
alembic current
alembic check
```

Do not use `Base.metadata.create_all()` in production. Tests may create/drop their isolated test schema.
