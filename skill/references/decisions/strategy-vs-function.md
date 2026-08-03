# Decision Record: Strategy or Function

## Question

Should a policy variation use a strategy abstraction or a callable/function parameter?

## Prefer a function when

- The policy is stateless and has one small operation.
- The language already treats callables as first-class contracts.
- Lifecycle, configuration, and capability discovery are unnecessary.

## Prefer a strategy type when

- The policy has state, several related operations, or explicit lifecycle.
- Multiple implementations need named capabilities, diagnostics, or configuration.
- The boundary is public and benefits from a documented protocol or trait.

## Avoid

Do not create a class hierarchy solely to make one function replaceable. Do not force a bare callable to carry hidden lifecycle or unrelated operations.
