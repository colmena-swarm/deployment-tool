#!/usr/bin/python
#
#  Copyright 2002-2024 Barcelona Supercomputing Center (www.bsc.es)
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

# -*- coding: utf-8 -*-

import json
import os
import subprocess
from typing import List, Dict

import zenoh


def build_container_images(
    path: str, tags: Dict[str, str], roles: List[str], platform: str
) -> Dict:
    """
    Uploads images to DockerHub.

    Parameters:
        path: path to the build folder.
        tags: dict with container imageIds, the keys are the role names.
        roles: list of role names.
        platform: architecture param in docker buildx.
    """
    for role_name in roles:
        role_path = f"{path}/{role_name}"
        build_container_image(role_path, tags[role_name], platform)
    return tags


def build_container_image(path: str, tag: str, platform: str):
    """
    Build container image using docker buildx.

    Parameters:
        - path: path to the Dockerfile.
        - tag: imageId to include to Dockerhub.
        - platform: architecture param in docker buildx.
    """
    os.environ["DOCKER_BUILDKIT"] = str(1)
    docker_build_command = (
        f"docker buildx build --platform {platform} --tag {tag} -f {path}/Dockerfile --rm=true "
        f"--no-cache={True} --load {path}"
    )
    subprocess.check_output(docker_build_command, shell=True)  # security issue


def publish_container_images(tags: Dict[str, str]):
    """Publishes images to DockerHub.

    Parameters:
        - tags: dict of image_ids with role_name as key.
    """
    for tag in tags.values():
        publish_image(tag)


def publish_image(tag: str):
    """Publishes image to DockerHub.

    Parameters:
        - tag: image_id.
    """
    os.environ["DOCKER_BUILDKIT"] = str(1)
    docker_build_command = f"docker image push {tag}"
    subprocess.check_output(docker_build_command, shell=True)


def deploy_service(_args, build_path: str, platform: str, user: str):
    """Deploys a service by building the container images and publishing the service.

    Parameters:
        - _args: deployment arguments
        - build_path: path to the build folder
        - platform: image architectures"""

    with open(f"{build_path}/service_description.json") as f:
        service_definition = json.load(f)

    role_definitions = service_definition["dockerRoleDefinitions"]
    tags = {}
    roles = []
    for role in role_definitions:
        role_name = role["id"]
        roles.append(role_name)
        role["imageId"] = user + "/" + role["imageId"]
        tags[role_name] = role["imageId"]

    build_container_images(build_path, tags, roles, platform)
    publish_container_images(tags)
    publish_service_definition(_args, service_definition)


def publish_service_definition(_args, service_definition: str):
    """Publish service definition to zenoh, keyexpr: colmena_service_definitions

        Parameters:
            - _args: deployment arguments
            - service_definition: json service definition"""
    print("publishing service definition to Zenoh")
    zenoh_session = zenoh.open(zenoh.Config.from_file("zenoh_config.json5"))
    zenoh_session.put("colmena_service_definitions", service_definition)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pretty-print",
        help="pretty print colmena service description",
        action="store_true",
    )
    parser.add_argument("--build_path", required=True, help="Path to build folder")
    parser.add_argument("--platform", help="Docker buildx architectures")
    parser.add_argument("--host", help="Deployment host")
    parser.add_argument("--port", help="Deployment port")
    parser.add_argument("--user", required=True, help="DockerHub username")
    args = parser.parse_args()

    deploy_service(args, args.build_path, args.platform, args.user)
