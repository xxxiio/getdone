# Bootstrap Migrations

Record breaking or semantically important profile and template migrations here.

A migration record should describe source and target versions, affected templates, safe automated actions, manual merge requirements, rollback considerations, and validation steps.

The migration CLI is dry-run by default:

```bash
getdone-migrate --project-root /path/to/project
```

Safe additions and verified-unmodified replacements require separate authorisation:

```bash
getdone-migrate \
  --project-root /path/to/project \
  --apply-additions

getdone-migrate \
  --project-root /path/to/project \
  --apply-replacements
```

Modified, untracked, mismatched, invalid, or ahead files are never written by the migration command. Modified managed Markdown files can be inspected structurally without writes:

```bash
getdone-migrate \
  --project-root /path/to/project \
  --sections \
  --no-diff
```

## Recorded migrations

- `0.2.0-to-0.3.0.md`: profile inheritance and explicit migration application.
- `0.3.0-to-0.4.0.md`: read-only section-aware Markdown evidence.
- `0.4.0-to-0.5.0.md`: distribution and adapter adoption with no bootstrap body changes.
