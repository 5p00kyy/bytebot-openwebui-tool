# Contributing to ByteBot OpenWebUI Tool

Thank you for considering contributing! This guide will help you get started.

## Ways to Contribute

- **Report Bugs** - Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- **Suggest Features** - Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- **Improve Documentation** - Fix typos, clarify instructions, add examples
- **Submit Code** - Bug fixes, new features, performance improvements
- **Share Use Cases** - Add examples to `examples/automation_examples.md`

## Development Setup

### Prerequisites
- Python 3.8+
- ByteBot instance (for testing)
- OpenWebUI (for integration testing)
- Git

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/5p00kyy/bytebot-openwebui-tool.git
cd bytebot-openwebui-tool
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run tests:**
```bash
# Integration tests (requires live ByteBot instance)
python3 tests/test_live_bytebot.py

# Task creation tests
python3 tests/test_task_creation.py
```

## Code Guidelines

### File Structure
```
bytebot-openwebui-tool/
├── tool.py                    # Main implementation
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── CHANGELOG.md               # Version history
├── tests/                     # Test files
└── examples/                  # Usage examples
```

### Coding Standards

**Follow OpenWebUI Tool Architecture:**
- All functions must be async (`async def`)
- Type hints are **required** for all parameters and return values
- Docstrings must use Sphinx-style format
- Use event emitters for progress updates

**Example:**
```python
async def my_function(
    self,
    param1: str,
    param2: int = 10,
    __event_emitter__: Optional[Any] = None
) -> str:
    """
    Brief function description.
    
    :param param1: Description of param1
    :param param2: Description of param2
    :return: Description of return value
    """
    # Implementation
```

**Error Handling:**
- Use comprehensive try/except blocks
- Provide clear, actionable error messages
- Emit error status via event emitters

**Security:**
- Never hardcode API keys or secrets
- Use Valves for configuration
- Sanitize user inputs
- Avoid `eval()` or `exec()`

## Testing

### Before Submitting

1. **Syntax Check:**
```bash
python3 -m py_compile tool.py
```

2. **Test Against Live ByteBot:**
```bash
python3 tests/test_live_bytebot.py
```

3. **Test in OpenWebUI:**
- Import tool.py into OpenWebUI
- Test each function via LLM interaction
- Verify event emitters work correctly

### Writing Tests

Add test cases to `tests/` directory:
```python
import asyncio
from tool import Tools

async def test_new_feature():
    tools = Tools()
    tools.valves.bytebot_url = "http://localhost:9991"
    
    result = await tools.new_function("test_input")
    assert "expected" in result
    print("✓ Test passed")

if __name__ == "__main__":
    asyncio.run(test_new_feature())
```

## Pull Request Process

### 1. Create a Branch
```bash
git checkout -b feature/my-new-feature
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Follow coding standards
- Add tests for new functionality
- Update documentation (README.md, CHANGELOG.md)
- Add examples if applicable

### 3. Commit Messages

Use clear, descriptive commit messages:
```bash
# Good
git commit -m "Add bulk task cancellation feature"
git commit -m "Fix timeout handling in execute_task()"
git commit -m "Update documentation for pagination"

# Bad
git commit -m "Update code"
git commit -m "Fix bug"
```

### 4. Update Version

Follow [Semantic Versioning](https://semver.org/):
- **Patch (1.1.0 → 1.1.1)** - Bug fixes, documentation
- **Minor (1.1.0 → 1.2.0)** - New features, backward compatible
- **Major (1.1.0 → 2.0.0)** - Breaking changes

Update version in:
- `tool.py` metadata docstring
- `CHANGELOG.md`
- README badges (if major/minor)

### 5. Submit Pull Request

1. Push your branch:
```bash
git push origin feature/my-new-feature
```

2. Open PR on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to related issues (Fixes #123)
   - Screenshots/examples if applicable

3. Wait for review and address feedback

## Documentation

### Update These Files

- **README.md** - For user-facing features
- **CHANGELOG.md** - For all changes (required)
- **QUICK_REFERENCE.md** - For new functions
- **examples/automation_examples.md** - For new use cases

### Documentation Style

- Use clear, concise language
- Provide code examples
- Include expected output
- Document edge cases and limitations

## Release Process

**For Maintainers:**

1. Update version in `tool.py`
2. Update `CHANGELOG.md` with changes
3. Commit: `git commit -m "Bump version to X.Y.Z"`
4. Tag: `git tag vX.Y.Z`
5. Push: `git push && git push --tags`
6. Create GitHub release with notes

## Questions?

- **Documentation:** Check [README.md](README.md)
- **Issues:** [GitHub Issues](https://github.com/5p00kyy/bytebot-openwebui-tool/issues)
- **Discussions:** Open a [GitHub Discussion](https://github.com/5p00kyy/bytebot-openwebui-tool/discussions)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and improve
- Assume good intentions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to ByteBot OpenWebUI Tool! 🚀
