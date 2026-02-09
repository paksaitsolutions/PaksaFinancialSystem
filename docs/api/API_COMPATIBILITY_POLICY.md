# API Backward-Compatibility Policy

## Purpose
This policy defines how the Paksa Financial System maintains backward compatibility for public API contracts and how breaking changes are introduced.

## Versioning Strategy
- **Current major version:** `v1`
- **Major versions** are reserved for breaking changes.
- **Minor releases** may add fields, endpoints, and non-breaking capabilities.
- **Patch releases** are for bug fixes and documentation updates.

## What Is Considered Backward Compatible
- Adding new endpoints.
- Adding optional response fields.
- Adding optional request fields with defaults.
- Expanding enum values without removing existing values.
- Increasing limits that do not change default behaviors.

## What Is Considered a Breaking Change
- Removing endpoints or fields.
- Renaming fields or changing field types.
- Changing required request fields.
- Narrowing validation constraints.
- Changing response envelope semantics.

## Deprecation Process
1. **Announce** deprecations in release notes and update `docs/api/DEPRECATION_CALENDAR.md`.
2. **Deprecate** in code with explicit warnings (when possible) and documentation.
3. **Observe** a minimum deprecation window of **90 days**.
4. **Remove** only in a **major** version release.

## Contract Snapshots
Every release publishes a versioned OpenAPI snapshot under `docs/api/openapi/` to support diffing and consumer validation.

## Support Channels
API contract concerns should be raised via the platform engineering channel or GitHub issues labeled `api-contract`.
