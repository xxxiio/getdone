# Organisation Profile Example

An organisation profile should extend a shared profile and contain only organisation-specific additions or intentional overrides.

```json
"organisation-python": {
  "version": "1.0.0",
  "description": "Organisation Python project state",
  "extends": ["standard"],
  "source": "skill/bootstrap/templates/organisation-python"
}
```

Possible additions include an approved command reference, internal architecture decision template, release checklist, or project-specific acceptance file. Avoid copying the entire standard profile; inheritance keeps shared updates visible and makes overrides explicit.
