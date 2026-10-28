# Python Store · Learning Project

A store simulation explored through a console interface and a Pygame interface. The exercises cover functions, classes, inventory, shopping carts and JSON persistence.

**Status:** educational application. Authentication is classroom code and is not suitable for real accounts.

## Navigate by concept

| Topic | Source |
| --- | --- |
| Functions, input validation, login and checkout flow | [Console application](test.py) |
| Classes, event handling and graphical UI | [Pygame application](pygame_store.py) |
| JSON reading and atomic file replacement | `DataManager` in [pygame_store.py](pygame_store.py), helpers in [test.py](test.py) |
| Inventory and account persistence | [inventory_data.json](inventory_data.json), [market_data.json](market_data.json) |
| UI styling | [theme.json](theme.json) |
| Earlier solution | [Original console shop](old%20files/LOVA%20SHOP.py) |

## Run locally

Use Python 3.10+ and a disposable working copy of the JSON files. Both applications read and write files relative to the working directory, so run from the repository root. Keep a private backup before experimenting.

```bash
python3 test.py
```

Despite its name, `test.py` starts an interactive console application; it is not an automated test suite. The graphical version is started with `python3 pygame_store.py` and imports both `pygame` and `pygame_gui`. Dependency versions are not pinned and graphical compatibility has not been revalidated in this documentation pass.

The older shop uses a different relative data path; read its `DB_FILE` setting before running it. It remains as a historical solution.

## Learning outcomes and limits

Practice decomposing a checkout flow, validating numbers, modeling state with dictionaries and classes, and persisting data through temporary-file replacement. Plain-text account data and embedded teaching credentials must not be reused for real users. No production deployment or automated test coverage is claimed.

[Python/SQL classwork](https://github.com/LOVA-malamud/LOVA_M) · [Homework archive](https://github.com/LOVA-malamud/ekom_home_work)
