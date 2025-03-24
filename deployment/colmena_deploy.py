#!/usr/bin/env python3
#
#  Copyright 2002-2025 Barcelona Supercomputing Center (www.bsc.es)
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
from typing import Dict, Any

import zenoh
from .build_image import Image, build_container_images


def deploy_service(_args, build_path: str, platform: str, user: str, skip_build: bool):
    with open(f"{build_path}/service_description.json") as f:
        service_definition = json.load(f)

    images = []
    for role in service_definition["dockerRoleDefinitions"]:
        tag = user + "/" + role["imageId"]
        id = role["id"]
        path =  f"{build_path}/{id}"
        image = Image(tag=tag, id=id, path=path)
        images.append(image)

        # add the Dockerhub username to the service definition
        role["imageId"] = tag

    for context in service_definition["dockerContextDefinitions"]:
        tag = user + "/" + context["imageId"]
        id = context["id"]
        path = f"{build_path}/context/{id}"
        image = Image(tag=tag, id=id, path=path)
        images.append(image)

        # add the Dockerhub username to the service definition
        context["imageId"] = tag

    if not skip_build:
        build_container_images(images, platform, _args.local_debug)
        print("Built and published images")
    else:
        print("Skipped building images")
    publish_service_definition(_args, service_definition)

def publish_service_definition(_args, service_definition: Dict[str, Any]):
    """Publish service definition to zenoh, keyexpr: colmena_service_definitions

        Parameters:
            - _args: deployment arguments
            - service_definition: json service definition"""
    service_name = service_definition["id"]["value"]
    print(f"publishing service definition for {service_name} to Zenoh")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    zenoh_config_path = os.path.join(script_dir, 'zenoh_config.json5')
    zenoh_session = zenoh.open(zenoh.Config.from_file(zenoh_config_path))
    zenoh_session.put(f"colmena_service_definitions/{service_name}", json.dumps(service_definition))

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
    parser.add_argument("--skip_build", action="store_true", help="Skip building Docker images")
    parser.add_argument("--local_debug", action="store_true", help="Build and load image into local store")
    args = parser.parse_args()

    deploy_service(args, args.build_path, args.platform, args.user, args.skip_build)
