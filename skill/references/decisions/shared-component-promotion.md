# Decision Record: Promote a Shared Component

## Question

Should repeated project code become a shared component?

## Choose promotion when

- The consumers share the same semantics, lifecycle, failure policy, and compatibility needs.
- A clear owner can maintain the public contract and migration path.
- Sharing reduces total complexity after dependency, release, and support costs are counted.
- Contract tests can protect every supported implementation or consumer boundary.

## Keep implementations local when

- Similar syntax hides different domain meaning or operational policy.
- Consumers need independent release cadence or incompatible dependencies.
- The abstraction is still changing rapidly in one project.
- A shared package would become a generic utility dumping ground.

## Evidence to record

List real consumers, contract tests, ownership, versioning, failure semantics, and the cost of not sharing. Revisit the decision when those assumptions change.
