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

import os
import subprocess
from dataclasses import dataclass
from typing import List


@dataclass
class Image:
    tag: str
    id: str
    path: str


def build_container_images(images: List[Image], platform: str, local_debug: bool):
    """Build Docker container images for the given list of images.
    
    Args:
        images: List of Image objects containing tag, id, and path
        platform: Docker buildx platform specification (e.g., "linux/amd64")
        local_debug: Debug flag (currently unused but kept for compatibility)
    """
    for each in images:
        print(f"building {each.tag} with path {each.path}")
        os.environ["DOCKER_BUILDKIT"] = str(1)
        docker_build_command = docker_build_command_string(each, platform, local_debug)
        subprocess.check_output(docker_build_command, shell=True)  # security issue

def docker_build_command_string(image: Image, platform: str, local_debug: bool):
    args = [
        "docker", "buildx", "build",
        "--no-cache",
        "-t", image.tag,
        "-f", f"{image.path}/Dockerfile",
    ]
    if local_debug:
        args.append("--load")
    if not local_debug:
        args.append("--platform")
        args.append(platform)
        args.append("--push")

    args.append(image.path)
    return " ".join(args)
