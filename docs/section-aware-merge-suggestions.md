# Section-Aware Markdown Merge Suggestions

Modified project-owned templates are never eligible for automatic replacement. The update and migration commands can instead produce a read-only structural comparison between the project file and the currently rendered shared template.

## Commands

Human-readable section details are opt-in:

```bash
getdone-check-updates \
  --project-root /path/to/project \
  --sections

getdone-migrate \
  --project-root /path/to/project \
  --sections \
  --no-diff
```

JSON output always includes a `merge_suggestion` field. It is an object for modified managed Markdown files and `null` for other update classifications:

```bash
getdone-check-updates \
  --project-root /path/to/project \
  --json
```

The object follows [`../skill/schemas/section-merge-suggestion.schema.json`](../skill/schemas/section-merge-suggestion.schema.json).

## Reported evidence

The analyser reports:

- headings found only in the available template;
- headings found only in project-owned content;
- heading text or level changes;
- direct content changes beneath matched headings;
- relative-order changes among matched headings;
- probable heading renames when same-level section content has at least `0.80` similarity.

Repeated headings are matched by direct-content similarity before stable document order. This lets two repeated sections exchange position without being misreported as unrelated additions and removals.

ATX headings from level one through six are supported. Heading-like lines inside fenced code blocks are ignored. Setext headings are not currently interpreted as section boundaries.

## Safety boundary

This analysis is intentionally two-way. A generated digest proves whether a project file changed, but it does not preserve the complete historical template body needed for a true three-way merge.

Therefore:

- suggestions describe evidence rather than authorising edits;
- probable renames carry confidence values;
- modified files remain in the `review` category;
- `--apply-replacements` cannot write a modified file;
- neither `--sections` nor JSON output changes project content.

A human or agent may use the report to prepare an explicit project-owned merge, followed by normal project validation.
