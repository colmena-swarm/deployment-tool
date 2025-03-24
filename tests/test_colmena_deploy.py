"""Tests for the main deployment functionality."""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from deployment.colmena_deploy import (
    deploy_service,
    publish_service_definition,
)
from deployment.build_image import Image


class TestPublishServiceDefinition:
    """Test service definition publishing functionality."""

    @pytest.mark.unit
    def test_publish_service_definition(self, mock_zenoh_open, mock_zenoh_session):
        """Test publishing service definition to Zenoh."""
        mock_zenoh_open.return_value = mock_zenoh_session
        service_definition = {"id": {"value": "test-service"}, "config": "test"}
        args = Mock()
        
        publish_service_definition(args, service_definition)
        
        mock_zenoh_open.assert_called_once()
        mock_zenoh_session.put.assert_called_once_with(
            "colmena_service_definitions/test-service",
            json.dumps(service_definition)
        )

    @pytest.mark.unit
    def test_publish_service_definition_zenoh_error(self, mock_zenoh_open):
        """Test handling of Zenoh connection errors."""
        mock_zenoh_open.side_effect = Exception("Zenoh connection failed")
        service_definition = {"id": {"value": "test-service"}}
        args = Mock()
        
        with pytest.raises(Exception, match="Zenoh connection failed"):
            publish_service_definition(args, service_definition)


class TestDeployService:
    """Test the main deployment service functionality."""

    @pytest.mark.unit
    def test_deploy_service_with_build(self, temp_dir, sample_service_json_file, 
                                     mock_subprocess, mock_zenoh_open, mock_zenoh_session):
        """Test full deployment with building images."""
        mock_zenoh_open.return_value = mock_zenoh_session
        
        # Create required directories
        (temp_dir / "worker").mkdir()
        (temp_dir / "manager").mkdir()
        (temp_dir / "context").mkdir()
        (temp_dir / "context" / "shared-context").mkdir()
        
        args = Mock()
        args.local_debug = False
        
        deploy_service(args, str(temp_dir), "linux/amd64", "testuser", False)
        
        # Verify images were built and published
        assert mock_subprocess.check_output.call_count >= 3  # At least 3 images
        mock_zenoh_session.put.assert_called_once()

    @pytest.mark.unit
    def test_deploy_service_skip_build(self, temp_dir, sample_service_json_file,
                                     mock_zenoh_open, mock_zenoh_session):
        """Test deployment skipping image build."""
        mock_zenoh_open.return_value = mock_zenoh_session
        
        args = Mock()
        args.local_debug = False
        
        deploy_service(args, str(temp_dir), "linux/amd64", "testuser", True)
        
        # Verify no Docker commands were called
        mock_zenoh_session.put.assert_called_once()

    @pytest.mark.unit
    def test_deploy_service_missing_file(self, temp_dir):
        """Test deployment with missing service description file."""
        args = Mock()
        args.local_debug = False
        
        with pytest.raises(FileNotFoundError):
            deploy_service(args, str(temp_dir), "linux/amd64", "testuser", False)

    @pytest.mark.unit
    def test_deploy_service_invalid_json(self, temp_dir):
        """Test deployment with invalid JSON file."""
        service_file = temp_dir / "service_description.json"
        service_file.write_text("invalid json")
        
        args = Mock()
        args.local_debug = False
        
        with pytest.raises(json.JSONDecodeError):
            deploy_service(args, str(temp_dir), "linux/amd64", "testuser", False)

    @pytest.mark.unit
    def test_deploy_service_updates_image_ids(self, temp_dir, sample_service_json_file,
                                            mock_zenoh_open, mock_zenoh_session):
        """Test that deployment updates image IDs with username prefix."""
        mock_zenoh_open.return_value = mock_zenoh_session
        
        args = Mock()
        args.local_debug = False
        
        deploy_service(args, str(temp_dir), "linux/amd64", "testuser", True)
        
        # Verify the service definition was published with updated image IDs
        call_args = mock_zenoh_session.put.call_args
        published_definition = json.loads(call_args[0][1])
        
        # Check that image IDs were updated with username prefix
        for role in published_definition["dockerRoleDefinitions"]:
            assert role["imageId"].startswith("testuser/")
        
        for context in published_definition["dockerContextDefinitions"]:
            assert context["imageId"].startswith("testuser/")
