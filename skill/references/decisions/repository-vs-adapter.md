# Decision Record: Repository or Adapter

## Question

Should an infrastructure boundary be modelled as a repository or a general adapter?

## Prefer a repository when

- The contract is about loading, saving, querying, or transacting domain aggregates and values.
- Operations should be expressed in domain language rather than protocol calls.

## Prefer an adapter when

- The boundary translates any external protocol, service, device, or legacy interface.
- Persistence is incidental rather than the organising concept.

## Avoid

Do not call every external wrapper a repository. Do not expose database-shaped generic CRUD when the domain needs narrower operations.
