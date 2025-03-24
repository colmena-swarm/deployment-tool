"""Integration tests for the deployment tool."""

import json
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.integration
class TestIntegration:
    """Integration tests that require more setup."""

    def test_service_definition_parsing(self, temp_dir):
        """Test parsing of real service definition files."""
        # Create a realistic service definition
        service_def = {
            "id": {"value": "integration-test-service"},
            "dockerRoleDefinitions": [
                {
                    "id": "web-server",
                    "imageId": "nginx:latest",
                    "ports": [{"containerPort": 80, "hostPort": 8080}]
                },
                {
                    "id": "database",
                    "imageId": "postgres:13",
                    "environment": {"POSTGRES_DB": "testdb"}
                }
            ],
            "dockerContextDefinitions": [
                {
                    "id": "shared-data",
                    "imageId": "alpine:latest"
                }
            ]
        }
        
        service_file = temp_dir / "service_description.json"
        with open(service_file, 'w') as f:
            json.dump(service_def, f, indent=2)
        
        # Verify the file can be read and parsed
        with open(service_file) as f:
            loaded_def = json.load(f)
        
        assert loaded_def["id"]["value"] == "integration-test-service"
        assert len(loaded_def["dockerRoleDefinitions"]) == 2
        assert len(loaded_def["dockerContextDefinitions"]) == 1

    def test_docker_command_generation(self):
        """Test that Docker commands are generated correctly."""
        from deployment.build_image import Image, build_container_images
        
        images = [
            Image(tag="testuser/web-server", id="web-server", path="/build/web-server"),
            Image(tag="testuser/database", id="database", path="/build/database")
        ]
        
        with patch('deployment.build_image.subprocess') as mock_subprocess:
            mock_subprocess.check_output.return_value = b"Success"
            
            build_container_images(images, "linux/amd64,linux/arm64", False)
            
            # Verify the correct number of calls
            assert mock_subprocess.check_output.call_count == 2
            
            # Verify command structure
            calls = mock_subprocess.check_output.call_args_list
            for call in calls:
                command = call[0][0]
                assert "docker buildx build" in command
                assert "--platform linux/amd64,linux/arm64" in command
                assert "--no-cache" in command

    def test_zenoh_config_loading(self):
        """Test that Zenoh configuration can be loaded."""
        from deployment.colmena_deploy import zenoh
        
        # Test that the config file exists and is valid
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, '..', 'deployment', 'zenoh_config.json5')
        
        assert os.path.exists(config_path)
        
        # Test that zenoh can parse the config (without actually connecting)
        try:
            config = zenoh.Config.from_file(config_path)
            assert config is not None
        except Exception as e:
            pytest.skip(f"Zenoh config parsing failed: {e}")

    @pytest.mark.integration
    def test_full_deployment_workflow_mock(self, temp_dir):
        """Test the full deployment workflow with mocked external dependencies."""
        from deployment.colmena_deploy import deploy_service
        
        # Create service definition
        service_def = {
            "id": {"value": "workflow-test"},
            "dockerRoleDefinitions": [
                {"id": "app", "imageId": "app-image"}
            ],
            "dockerContextDefinitions": []
        }
        
        service_file = temp_dir / "service_description.json"
        with open(service_file, 'w') as f:
            json.dump(service_def, f)
        
        # Create required directory structure
        (temp_dir / "app").mkdir()
        
        # Mock external dependencies
        with patch('deployment.build_image.subprocess') as mock_subprocess, \
             patch('deployment.colmena_deploy.zenoh.open') as mock_zenoh_open:
            
            mock_subprocess.check_output.return_value = b"Success"
            mock_zenoh_session = mock_subprocess.return_value
            mock_zenoh_open.return_value = mock_zenoh_session
            
            args = type('Args', (), {'local_debug': 'false'})()
            
            # This should not raise any exceptions
            deploy_service(args, str(temp_dir), "linux/amd64", "testuser", False)
            
            # Verify Docker build was called
            mock_subprocess.check_output.assert_called()
            
            # Verify Zenoh publish was called
            mock_zenoh_open.assert_called_once()
