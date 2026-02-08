# OpenAPI Contract Snapshots

This folder contains versioned OpenAPI contract snapshots for each release.

## Structure
```
docs/api/openapi/
  v1.0.0/
    openapi.json
```

## Generating a Snapshot
Run the export script from the repository root:
```
PYTHONPATH=backend python backend/scripts/export_openapi.py
```

## Notes
- Snapshots are the source of truth for API diffs and contract review.
- Update snapshots whenever API changes are released.
