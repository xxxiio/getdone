# v1 Rollout Matrix

The executable source is `development/rollout/cases.json`; the committed result is
`development/rollout/results/1.0.0.json`.

| Case | Workflow | Ecosystem | Adapter path | Context | Result |
|---|---|---|---|---:|---|
| Python slug feature | Feature/TDD | Python | Codex bootstrap-managed `AGENTS.md` | 6 docs / ~2,756 tokens | Passed |
| Empty-window regression | Bug fix | C++20 | Claude project file | 6 docs / ~2,790 tokens | Passed |
| Invoice decomposition | Refactoring | Python | Cursor project rule | 6 docs / ~2,748 tokens | Passed |

Every case performs a clean project copy, baseline test, standard-profile bootstrap,
composition verification, adapter installation, deterministic context selection,
solution application, completed tests, controlled-record validation, and strict
project validation. The shared product is checked to ensure no live `.agent/` state is created.

## Interpretation

The matrix demonstrates executable adoption across three task classes, two language
ecosystems, and three adapter delivery paths after content consolidation. It does not
claim independent vendor-model execution; adapter contracts and generated project files
were exercised locally.

## Reproduce

```bash
python -m development.tools.rollout_validation --repository-root . --check
```

The C++ case requires `g++` with C++20 support.
