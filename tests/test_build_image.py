"""Tests for the build_image module."""

import os
from unittest.mock import Mock, patch

import pytest

from deployment.build_image import (
    Image,
    build_container_images,
    publish_container_images,
)


class TestImage:
    """Test the Image dataclass."""

    def test_image_creation(self):
        """Test Image object creation."""
        image = Image(tag="test/tag", id="test-id", path="/test/path")
        assert image.tag == "test/tag"
        assert image.id == "test-id"
        assert image.path == "/test/path"


class TestBuildContainerImages:
    """Test container image building functionality."""

    @pytest.mark.unit
    def test_build_container_images_single(self, mock_subprocess, mock_os_environ):
        """Test building a single container image."""
        images = [Image(tag="test/image", id="test", path="/test/path")]
        
        build_container_images(images, "linux/amd64", False)
        
        mock_subprocess.check_output.assert_called_once()
        call_args = mock_subprocess.check_output.call_args[0][0]
        assert "docker buildx build" in call_args
        assert "--platform linux/amd64" in call_args
        assert "--load" not in call_args
        assert "-t test/image" in call_args
        assert "--no-cache" in call_args
        assert mock_os_environ["DOCKER_BUILDKIT"] == "1"

    @pytest.mark.unit
    def test_build_container_images_single_local_debug(self, mock_subprocess, mock_os_environ):
        """Test building a single container image."""
        images = [Image(tag="test/image", id="test", path="/test/path")]
        
        build_container_images(images, "linux/amd64", True)
        
        mock_subprocess.check_output.assert_called_once()
        call_args = mock_subprocess.check_output.call_args[0][0]
        assert "docker buildx build" in call_args
        assert "--load" in call_args
        assert "-t test/image" in call_args
        assert "--no-cache" in call_args
        assert "--platform linux/amd64" not in call_args
        assert mock_os_environ["DOCKER_BUILDKIT"] == "1"

    @pytest.mark.unit
    def test_build_container_images_multiple(self, mock_subprocess, mock_os_environ):
        """Test building multiple container images."""
        images = [
            Image(tag="test/image1", id="test1", path="/test/path1"),
            Image(tag="test/image2", id="test2", path="/test/path2")
        ]
        
        build_container_images(images, "linux/amd64", False)
        
        assert mock_subprocess.check_output.call_count == 2

    @pytest.mark.unit
    def test_build_container_images_subprocess_error(self, mock_subprocess):
        """Test handling of subprocess errors during build."""
        mock_subprocess.check_output.side_effect = Exception("Build failed")
        images = [Image(tag="test/image", id="test", path="/test/path")]
        
        with pytest.raises(Exception, match="Build failed"):
            build_container_images(images, "linux/amd64", False)


class TestPublishContainerImages:
    """Test container image publishing functionality."""

    @pytest.mark.unit
    def test_publish_container_images_single(self, mock_subprocess, mock_os_environ):
        """Test publishing a single container image."""
        images = [Image(tag="test/image", id="test", path="/test/path")]
        
        publish_container_images(images)
        
        mock_subprocess.check_output.assert_called_once()
        call_args = mock_subprocess.check_output.call_args[0][0]
        assert call_args == "docker image push test/image"
        assert mock_os_environ["DOCKER_BUILDKIT"] == "1"

    @pytest.mark.unit
    def test_publish_container_images_multiple(self, mock_subprocess):
        """Test publishing multiple container images."""
        images = [
            Image(tag="test/image1", id="test1", path="/test/path1"),
            Image(tag="test/image2", id="test2", path="/test/path2")
        ]
        
        publish_container_images(images)
        
        assert mock_subprocess.check_output.call_count == 2

    @pytest.mark.unit
    def test_publish_container_images_subprocess_error(self, mock_subprocess):
        """Test handling of subprocess errors during publish."""
        mock_subprocess.check_output.side_effect = Exception("Push failed")
        images = [Image(tag="test/image", id="test", path="/test/path")]
        
        with pytest.raises(Exception, match="Push failed"):
            publish_container_images(images)
