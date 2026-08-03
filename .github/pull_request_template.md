## Summary

<!-- What changed and why? Keep this outcome-focused. -->

## Change impact

- [ ] Public API
- [ ] Persisted data or project-owned records
- [ ] Configuration
- [ ] Dependencies
- [ ] Security boundary
- [ ] Concurrency
- [ ] Performance-sensitive behaviour
- [ ] User interface
- [ ] Deployment, packaging, or release automation
- [ ] Documentation only

## Contract and compatibility

- [ ] Existing canonical IDs and aliases remain valid, or migration/deprecation is documented.
- [ ] Template/profile/schema versions were changed where required.
- [ ] Generated indexes and documentation were regenerated.
- [ ] No mutable consuming-project state was added to the shared skill pack.
- [ ] The recurring context cost is unchanged or justified with benchmark evidence.

## Validation evidence

<!-- Replace or remove commands that do not apply. Explain every skipped required check. -->

```bash
python development/scripts/validate_repository.py --repository-root .
python development/scripts/validate_frontmatter.py --repository-root .
python -m development.tools.validate_skill_content --repository-root .
python development/scripts/generate_indexes.py --repository-root .
python development/scripts/generate_docs.py --repository-root .
python -m unittest discover -s tests
python -m compileall getdone tooling tests
git diff --check
```

## Documentation and migration

- [ ] User-facing behaviour is documented.
- [ ] Public API documentation comments are accurate.
- [ ] Migration guidance is included when project-owned state or public contracts change.
- [ ] No documentation change is required; reason: <!-- explain -->

## Scope and follow-up

- **Out of scope:**
- **Known limitations or risks:**
- **Next deterministic step:**
