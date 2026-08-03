# Package naming

GetDone is the product name. Install the Python distribution named `getdone-dev`, then
use the `getdone` command and `getdone` Python import package.

```bash
python -m pip install getdone-dev
getdone --version
```

The distribution name differs because `getdone` is already occupied in the global PyPI
namespace. The stable naming contract is:

| Surface | Name |
|---|---|
| Product | GetDone |
| PyPI distribution | `getdone-dev` |
| CLI | `getdone` and `getdone-*` |
| Python import | `getdone` |
| Project state | `.agent/` |

Maintainers must not publish under the unrelated existing `getdone` distribution or an
unavailable separator variant.
