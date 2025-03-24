"""Pytest configuration and shared fixtures."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_service_definition():
    """Sample service definition for testing."""
    return {
        "id": {"value": "test-service"},
        "dockerRoleDefinitions": [
            {
                "id": "worker",
                "imageId": "worker-image"
            },
            {
                "id": "manager",
                "imageId": "manager-image"
            }
        ],
        "dockerContextDefinitions": [
            {
                "id": "shared-context",
                "imageId": "shared-context-image"
            }
        ]
    }


@pytest.fixture
def sample_service_json_file(temp_dir, sample_service_definition):
    """Create a sample service_description.json file."""
    service_file = temp_dir / "service_description.json"
    with open(service_file, 'w') as f:
        json.dump(sample_service_definition, f)
    return service_file


@pytest.fixture
def mock_zenoh_session():
    """Mock Zenoh session for testing."""
    session = Mock()
    session.put = Mock()
    return session


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing Docker commands."""
    with patch('deployment.build_image.subprocess') as mock_sub:
        mock_sub.check_output.return_value = b"Success"
        yield mock_sub


@pytest.fixture
def mock_zenoh_open():
    """Mock zenoh.open for testing."""
    with patch('deployment.colmena_deploy.zenoh.open') as mock_open:
        yield mock_open


@pytest.fixture
def mock_os_environ():
    """Mock os.environ for testing."""
    with patch.dict('os.environ', {}, clear=True) as mock_env:
        yield mock_env
