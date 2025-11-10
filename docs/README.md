# V2Ray Client Documentation

This directory contains the Sphinx documentation for the V2Ray Client project.

## Building the Documentation

### Prerequisites

Install Sphinx and the required theme:

```bash
pip install -r requirements.txt
```

Or if using the project's virtual environment:

```bash
./venv/bin/pip install -r docs/requirements.txt
```

### Build HTML Documentation

```bash
cd docs
make html
```

The generated HTML documentation will be in `docs/_build/html/`.

### View Documentation

Open the documentation in your browser:

```bash
# Linux
xdg-open _build/html/index.html

# macOS
open _build/html/index.html
```

### Other Formats

Sphinx can generate documentation in various formats:

```bash
# PDF (requires LaTeX)
make latexpdf

# EPUB
make epub

# Plain text
make text

# Man pages
make man
```

### Clean Build Files

To remove all generated files:

```bash
make clean
```

## Documentation Structure

- `index.rst` - Main documentation index
- `installation.rst` - Installation guide
- `usage.rst` - Usage guide
- `api/` - API reference documentation
  - `modules.rst` - Module index
  - `main.rst` - Main module documentation
  - `v2ray_manager.rst` - V2Ray manager documentation
  - `subscription_manager.rst` - Subscription manager documentation
  - `server_updater.rst` - Server updater documentation
  - `ui.rst` - UI package documentation

## Writing Documentation

### Docstring Format

The project uses Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    Longer description with more details about what the function does,
    how it works, and any important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
        
    Example:
        >>> example_function("test", 42)
        True
    """
    pass
```

### Adding New Pages

1. Create a new `.rst` file in the appropriate directory
2. Add it to the `toctree` directive in the parent file
3. Rebuild the documentation

### Sphinx Directives

Common directives used in the documentation:

- `.. automodule::` - Automatically document a module
- `.. autoclass::` - Automatically document a class
- `.. autofunction::` - Automatically document a function
- `.. code-block::` - Include code examples
- `.. note::` - Add a note box
- `.. warning::` - Add a warning box

## Continuous Integration

The documentation can be automatically built and deployed using CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Build documentation
  run: |
    pip install -r docs/requirements.txt
    cd docs
    make html
```

## Contributing

When adding new features or modules:

1. Add comprehensive docstrings to all classes and functions
2. Update or create relevant `.rst` files in `docs/api/`
3. Add usage examples where appropriate
4. Build and review the documentation locally before committing

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Google Style Python Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
