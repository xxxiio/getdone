# Shared Component Checklist

Before creating a shared component, answer:

1. Which repeated capability does it centralise?
2. Which projects or modules have genuinely compatible semantics?
3. Who owns its public contract and upgrades?
4. What configuration, lifecycle, concurrency, and failure behaviour are guaranteed?
5. Can consumers replace or adapt it?
6. Does sharing reduce total complexity after dependency and release costs?
7. What tests protect compatibility?

Do not share merely because two code fragments look similar. Share stable meaning and policy.
