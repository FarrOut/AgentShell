# AgentShell Test Suite

## Running Tests

### Quick Start

```bash
# Install in development mode with dependencies
pipx install -e . --force

# Run all tests
python3 -m unittest discover -s tests -p 'test_*.py' -v

# Run specific test file
python3 -m unittest tests.test_safety_checker -v

# Run specific test
python3 -m unittest tests.test_safety_checker.TestSafetyChecker.test_safe_read_commands -v
```

### Test Categories

**Unit Tests** (no external dependencies):
- `test_safety_checker.py` - Bash script safety analysis
- `test_script_extraction.py` - LLM response parsing
- `test_session.py` - Session management
- `test_ollama_client.py` - Ollama client (mocked)

**Integration Tests** (require Ollama):
- `test_integration.py` - Full workflow tests

### Test Coverage

Run with coverage:
```bash
pip install coverage
coverage run -m unittest discover -s tests
coverage report
coverage html  # Generate HTML report
```

## Writing Tests

### Test Structure
```python
import unittest
from agentshell.module import function

class TestFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_something(self):
        """Test description."""
        result = function()
        self.assertEqual(result, expected)
```

### Best Practices
- One test file per module
- Descriptive test names
- Use `subTest` for parameterized tests
- Mock external dependencies
- Skip tests that require unavailable resources

## Current Test Status

✅ Safety Checker - 20+ tests
✅ Script Extraction - 10+ tests  
✅ Session Management - 10+ tests
✅ Ollama Client - 15+ tests
✅ Integration - 5+ tests

**Total: 60+ tests**
