# Public Release Readiness

Structural completeness is necessary but not sufficient for a public release.

A public `v1.0.0` requires evidence for all of the following:

- Product and development-content boundaries validate from the exact release tag.
- Wheel and product-only skill pack install and operate independently.
- Supported bootstrap profiles initialise and migrate without destructive replacement of project-owned content.
- Context routing meets the committed accuracy, recall, document-count, and token-budget gates.
- Controlled project records reject unsupported states and accept realistic project records.
- Internal rollout covers multiple repositories, languages, task classes, and supported agent adapters.
- At least one fresh-user or independent-agent adoption run follows only the published usage guide.
- Remote CI passes on a publishable repository remote for the exact release commit.
- Release artefacts, checksums, changelog, migration documentation, licences, and security policy are complete.
- The release tag is signed when the project’s release policy requires signing.
- No known blocking data-loss, security, migration, packaging, or contract-compatibility issue remains.

Do not infer public readiness from local tests alone. Record failed or unavailable release checks explicitly and keep the release candidate status until the checklist is complete.
