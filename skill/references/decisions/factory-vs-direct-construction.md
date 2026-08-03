# Decision Record: Factory or Direct Construction

## Question

Should callers construct a concrete object directly or request it through a factory?

## Prefer direct construction when

- One concrete type is stable and its dependencies are already explicit.
- Validation is local to the constructor or named constructor.
- Callers benefit from seeing ownership and lifecycle directly.

## Prefer a factory when

- Selection varies by configuration, protocol, platform, or discovered capability.
- Construction coordinates several dependencies or protects invariants.
- Concrete implementation details should remain outside the caller's layer.

## Avoid

A factory that always forwards every argument to one constructor adds indirection without policy.
