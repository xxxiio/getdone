# Product, package, import, and command names

GetDone uses different names for different distribution surfaces. This is intentional.

| Surface | Canonical name | Example |
|---|---|---|
| Product and documentation | **GetDone** | “GetDone project records” |
| Source repository | `getdone` | repository or checkout directory |
| PyPI distribution | `getdone-dev` | `python -m pip install getdone-dev` |
| Python import package | `getdone` | `import getdone` |
| Primary command | `getdone` | `getdone doctor` |
| Standalone commands | `getdone-*` | `getdone-validate-project` |
| Project-owned state | `.agent/` | `.agent/current/task.md` |

## Why the PyPI distribution differs

The `getdone` distribution name is already occupied on PyPI, and the alternate separator
variant is unavailable for this project. Python distribution names share a global namespace,
while an installed command and import package may use a different name. Therefore this
project publishes as `getdone-dev` while retaining GetDone as the product name and
`getdone` as the command and import namespace.

Do not attempt to publish this project under the existing `getdone` PyPI name, depend on
ownership transfer, or use confusing punctuation variants. Treat `getdone-dev` as the
stable 1.x distribution identity.

## Installation and verification

```bash
python -m pip install getdone-dev
getdone --version
python -c "import getdone; print(getdone.__name__)"
```

Package metadata, release workflows, documentation, and support requests must use the
correct name for the relevant surface. A user-facing sentence may say “install GetDone,”
but the command must say `pip install getdone-dev`.
