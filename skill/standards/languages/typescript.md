---
id: standard.language.typescript
version: 1.1.0
status: stable
---
# TypeScript Standard

## Apply by impact

Apply only rule groups activated by the current task or change-impact record. Do not invent
evidence for untouched surfaces; when a required gate asks about one, record why it is not
applicable.

## Rules
### Design and boundaries
- Keep domain logic independent from UI, framework, transport, persistence, and runtime adapters. Prefer composition and explicit dependency injection.
- Define small module APIs; avoid barrel files or shared utility modules that create hidden cycles and broad ownership.
### Types and data
- Enable `strict` mode. Prefer discriminated unions, branded IDs, readonly data, generics, and exhaustive `never` checks over flags, enums-as-strings, and type assertions.
- Treat external input as `unknown`, validate it once at the boundary, and avoid `any`; localise unavoidable escapes with a reason.
### Errors and resources
- Use explicit error types/results for expected failures and preserve `cause` when translating exceptions. Never silently swallow rejected promises.
- Own subscriptions, streams, timers, sockets, abort controllers, file handles, and transactions explicitly.
### Concurrency and state
- Await or intentionally supervise every promise. Use `AbortSignal`, bounded concurrency, idempotency, and race protection for async workflows.
- Minimise mutable shared state; make UI/store state transitions explicit and serialisable where practical.
### Testing
- Cover domain behaviour, parsing/validation, error paths, async cancellation/races, serialization, and framework boundaries.
- Prefer deterministic fakes and contract tests; avoid snapshots as the sole evidence for behavioural logic.
### Performance
- Measure bundle size, render/recompute cost, allocations, network waterfalls, and event-loop blocking. Avoid accidental quadratic transforms and unnecessary object churn.
### Security
- Prevent injection, prototype pollution, unsafe HTML, path traversal, SSRF, insecure deserialization, secret exposure, and dependency/supply-chain risk.
- Keep server-only secrets and capabilities out of browser bundles; validate authorization at the server boundary.
### Public API documentation
- Add meaningful TSDoc/JSDoc comments to changed public exported modules, types, interfaces, classes, functions, methods, and extension points.
- Document errors, side effects, ownership, cancellation, units, valid ranges, runtime requirements, and examples when not evident from types.
- Do not use comments that merely restate signatures. Internal code needs comments when invariants, algorithms, or runtime/type-system gaps are non-obvious.
### Tooling and delivery
- Follow project package manager, lockfile, module target, runtime/browser support, lint, formatter, test, build, and publishing configuration.
- Validate `tsc --noEmit`, clean install, build, tests, package exports/types, tree shaking, and supported runtimes when affected.
## Review triggers
Review missing API comments, `any`, unsafe assertions, non-exhaustive unions, circular imports,
framework logic in domain modules, unhandled promises, stale closures/races, broad stores, unsafe
HTML/dynamic execution, duplicate dependencies, and packages that expose mismatched runtime/types.
## Required response
Strengthen types and validation, remove or isolate assertions, separate domain and adapters, make
async lifecycle explicit, update TSDoc/JSDoc and examples, add focused tests, and validate the
built package or application in supported runtimes.
## Exceptions
Dynamic interoperability may use `unknown`, runtime validation, or narrowly scoped `any` when the
boundary cannot be typed more precisely. Generated, vendored, compatibility-only, or
framework-generated APIs may use narrowly configured exclusions.
## Evidence
Record formatter, ESLint, `tsc --noEmit`, unit/integration/end-to-end test, coverage, build, bundle,
security audit, clean-install, package-export, and runtime/browser results that apply. Record
TSDoc/API Extractor/TypeDoc or equivalent generated documentation checks when applicable.
