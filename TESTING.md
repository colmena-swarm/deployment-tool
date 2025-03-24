# Testing Guide for COLMENA Deployment Tool

This document provides comprehensive information about testing the COLMENA deployment tool.

## Overview

The testing framework includes:
- **Unit Tests**: Test individual functions and classes in isolation
- **Integration Tests**: Test the interaction between components
- **CLI Tests**: Test command-line interface functionality
- **Coverage Reporting**: Track test coverage metrics

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and shared fixtures
└── fixtures/
    └── sample_service_description.json  # Test data
```

## Running Tests

### Prerequisites

Install the package with test dependencies:
```bash
pip install -e ".[test]"
```

### Basic Test Commands

```bash
# Run all tests
pytest

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests with coverage
pytest --cov=deployment --cov-report=html

### Using Make Commands

```bash
# Install development dependencies
make install-dev

# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests with coverage report
make test-coverage

# Run fast tests only
make test-fast

# Clean up generated files
make clean
```

## Coverage

The project uses `pytest-cov` for coverage reporting:

- **HTML Report**: Generated in `htmlcov/` directory
- **XML Report**: Generated as `coverage.xml` for CI
- **Terminal Report**: Shows coverage summary in terminal

Coverage targets:
- Aim for >80% line coverage
- Focus on critical deployment logic
- Exclude test files and configuration files

## Writing New Tests

### Unit Test Example

```python
@pytest.mark.unit
def test_new_function():
    """Test description."""
    # Arrange
    input_data = "test"
    
    # Act
    result = new_function(input_data)
    
    # Assert
    assert result == "expected_output"
```

### Integration Test Example

```python
@pytest.mark.integration
def test_full_workflow():
    """Test complete workflow."""
    # Test with real file system operations
    # May require external dependencies
```

### Using Fixtures

```python
def test_with_fixtures(temp_dir, sample_service_definition):
    """Test using provided fixtures."""
    # Use temp_dir for file operations
    # Use sample_service_definition for test data
```

## Mocking External Dependencies

The tests mock external dependencies to ensure:
- Tests run without Docker daemon
- Tests run without Zenoh network
- Tests are fast and reliable
- Tests are isolated from external systems

### Common Mocks

```python
# Mock subprocess calls
with patch('deployment.colmena_deploy.subprocess') as mock_subprocess:
    mock_subprocess.check_output.return_value = b"Success"

# Mock Zenoh connection
with patch('deployment.colmena_deploy.zenoh.open') as mock_zenoh_open:
    mock_zenoh_session = Mock()
    mock_zenoh_open.return_value = mock_zenoh_session
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the package is installed in development mode
2. **Missing Dependencies**: Install test dependencies with `pip install -e ".[test]"`
3. **Permission Errors**: Some tests may require write permissions for temporary files
4. **Network Issues**: Integration tests may fail if external services are unavailable

### Debug Mode

Run tests with verbose output:
```bash
pytest -v -s
```

Run specific test with debugging:
```bash
pytest tests/test_colmena_deploy.py::TestImage::test_image_creation -v -s
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Use clear, descriptive test names
3. **Arrange-Act-Assert**: Structure tests clearly
4. **Mock External Dependencies**: Don't rely on external services
5. **Test Edge Cases**: Include error conditions and boundary cases
6. **Documentation**: Add docstrings to test functions
7. **Coverage**: Aim for high coverage of critical paths

## Future Enhancements

Potential improvements to the testing framework:
- Add property-based testing with `hypothesis`
- Add performance benchmarks
- Add Docker-based integration tests
- Add Zenoh network integration tests
- Add security testing for subprocess calls
- Add end-to-end testing with real service deployments
