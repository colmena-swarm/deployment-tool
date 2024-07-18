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


def build_docker_images(
    path: str, tags: Dict[str, str], roles: List[str], platform: str
) -> Dict:
    """
    Uploads images to DockerHub.

    Parameters:
        path: path to the build folder.
        tags: dict with docker imageIds, the keys are the role names.
        roles: list of role names.
        platform: architecture param in docker buildx.
    """
    for role_name in roles:
        role_path = f"{path}/{role_name}"
        build_docker_image(role_path, tags[role_name], platform)
        publish_image(tags[role_name])
    return tags


def build_docker_image(path: str, tag: str, platform: str) -> str:
    """
    Build docker image using docker buildx.

    Parameters:
        - path: path to the Dockerfile.
        - tag: imageId to include to Dockerhub.
        - platform: architecture param in docker buildx.
    """
    os.environ["DOCKER_BUILDKIT"] = str(1)
    docker_build_command = (
        f"docker buildx build --tag {tag} -f {path}/Dockerfile --rm=true "
        f"--no-cache={True} --load {path}"
    )
    subprocess.check_output(docker_build_command, shell=True)  # security issue


def publish_images(tags: Dict[str, str]):
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


def dcp_host(args) -> str:
    """Gets DCP host from args."""
    if args.host:
        return args.host
    else:
        default = "localhost"
        print(f"DCP host not set, defaulting to {default}")
        return default


def dcp_port(args) -> int:
    """Gets DCP port from args."""
    if args.port:
        return args.port
    else:
        default = 5555
        print(f"DCP port not set, defaulting to {str(default)}")
        return default


def deploy_service(_args, build_path: str, platform: str):
    """Deploys a service by building the docker images and publishing the service.

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
        tags[role_name] = role["imageId"]
    build_docker_images(build_path, tags, roles, platform)
    publish_service(_args, tags, service_definition)


def publish_service(_args, tags: Dict[str, str], service_definition: str):
    """Publishes a service by publishing images to DockerHub and the service definition to DCP.

    Parameters:
        - _args: deployment arguments
        - tags: dict with imageIds and role_name as key
        - service_definition: parser service definition
    """
    publish_images(tags)
    dcp_host_port = dcp_host(_args) + ":" + str(dcp_port(_args))
    result = subprocess.check_output(
        [
            "grpcurl",
            "--plaintext",
            "-d",
            json.dumps(service_definition),
            dcp_host_port,
            "ColmenaPlatform/AddService",
        ]
    )
    dict_result = json.loads(result)
    print(dict_result)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pretty-print",
        help="pretty print colmena service description",
        action="store_true",
    )
    parser.add_argument("--build_path", help="Path to build folder")
    parser.add_argument("--platform", help="Docker buildx architectures")
    parser.add_argument("--host", help="DCP host for deployment")
    parser.add_argument("--port", help="DCP port for deployment")
    args = parser.parse_args()

    deploy_service(args, args.build_path, args.platform)
