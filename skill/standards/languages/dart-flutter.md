---
id: standard.language.dart-flutter
version: 1.2.0
status: stable
---
# Dart and Flutter Standard

## Apply by impact

Apply only rule groups activated by the current task or change-impact record. Do not invent
evidence for untouched surfaces; when a required gate asks about one, record why it is not
applicable.

## Rules
### Design and boundaries
- Separate widgets, presentation state, domain logic, data sources, and platform adapters when they change independently.
- Prefer focused widgets, immutable models, composition, and explicit dependency injection over global service lookup.
### Types and data
- Use sound null safety, sealed classes/enums, typed value objects, and exhaustive pattern matching. Avoid dynamic maps crossing domain boundaries.
- Validate decoded JSON and platform-channel payloads before creating trusted domain values.
### Errors and resources
- Model expected failures explicitly; preserve stack traces when translating exceptions. Do not hide errors in broad catches.
- Dispose controllers, subscriptions, focus nodes, animations, isolates, and native resources according to ownership.
### Concurrency and state
- Keep state ownership explicit and transitions immutable. Guard stale async results, cancellation, mounted context, and duplicate submissions.
- Use isolates only for measured CPU work; avoid blocking the UI isolate and uncontrolled streams.
### Testing
- Use unit tests for domain logic, widget tests for interaction, golden tests for stable visuals, and integration/platform tests for real boundaries.
- Cover loading, empty, error, accessibility, localisation, navigation, restoration, and lifecycle states where relevant.
### Performance
- Measure frame, rebuild, layout, image, memory, and startup cost. Use `const`, keys, builders, repaint boundaries, and caching only where evidence supports them.
### Security
- Protect secure storage, deep links, WebViews, platform channels, certificates, logs, and local persistence. Never embed secrets in the client bundle.
### Public API documentation
- Add `///` Dart documentation comments to changed public libraries, classes, mixins, extensions, widgets, functions, methods, and non-obvious public properties.
- Document parameters, returns, thrown errors, side effects, state ownership, disposal, nullability, accessibility, platform behaviour, and examples when not evident from types.
- Do not use comments that merely repeat declarations. Private helpers/widgets need comments when lifecycle, state, or interaction contracts are non-obvious.
### Tooling and delivery
- Follow project Flutter/Dart versions, lints, state-management, routing, code generation, flavour, signing, and platform support choices.
- Regenerate derived code deterministically and validate release builds for affected platforms.
## Review triggers
Review missing Dart API comments, monolithic `build` methods, mixed I/O in widgets, unclear state
ownership, missing disposal, stale async updates, navigation/context misuse, platform leakage,
accessibility gaps, uncontrolled rebuilds, and UI behaviour tested only manually.
## Required response
Update API comments and generated references, extract cohesive widgets/controllers, move side
effects to owned boundaries, make state transitions explicit, and add unit, widget tests, golden,
integration, accessibility, or platform tests according to risk.
## Exceptions
A locally complex widget may remain when extraction would obscure one cohesive interaction and
focused widget tests protect it. Generated, vendored, compatibility-only, or framework-generated
symbols may use narrowly configured exclusions.
## Evidence
Record `dart format --output=none --set-exit-if-changed .`, `dart analyze`, `flutter test`, widget
tests, golden-update rationale, integration tests, build, accessibility, performance, and platform
checks that apply. Record `dart doc` or equivalent API-reference build and documentation warnings.
