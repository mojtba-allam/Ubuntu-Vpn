# Python Virtual Environment Commands

This project uses a Python virtual environment located at `./venv/`.

## Important Commands

Always use the virtual environment binaries for Python operations:

- **pytest**: `./venv/bin/pytest`
- **pip**: `./venv/bin/pip`
- **python**: `./venv/bin/python` or `./venv/bin/python3`

## Examples

Run tests:
```bash
./venv/bin/pytest tests/test_file.py -v
```

Install packages:
```bash
./venv/bin/pip install package-name
```

Install from requirements:
```bash
./venv/bin/pip install -r requirements.txt
```

## Note

Do NOT use system-level `python`, `pip`, or `pytest` commands. Always use the virtual environment binaries to ensure correct dependencies and isolation.
