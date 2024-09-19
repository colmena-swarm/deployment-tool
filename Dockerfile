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

FROM python:3.14.0a2-slim-bookworm

    ARG BUILD_DATE 2024-12-18

    LABEL org.label-schema.name="Colmena's deployment tool" \
        org.label-schema.description="Tool for deploying services on a COLMENA platform" \
        org.label-schema.build-date="${BUILD_DATE}" \
        org.label-schema.url="http://proyecto-colmena.com" \
        org.label-schema.vcs-url="https://github.com/colmena-swarm/deployment-tool" \
        maintainer="Barcelona Supercomputing Center"

    # Install Docker dependencies
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
            apt-transport-https=2.6.1 \
            ca-certificates=20230311 \
            curl=7.88.1-10+deb12u8 \
            gnupg=2.2.40-1.1 \
            lsb-release=12.0-1 && \
        rm -rf /var/lib/apt/lists/*

    # Add Docker’s official GPG key
    SHELL ["/bin/bash", "-o", "pipefail", "-c"]
    RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Set up the stable repository
    RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list >/dev/null

    
    # Install Docker
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
            docker-ce=5:27.5.1-1~debian.12~bookworm \
            docker-ce-cli=5:27.5.1-1~debian.12~bookworm \
            docker-buildx-plugin=0.20.0-1~debian.12~bookworm && \
        rm -rf /var/lib/apt/lists/* 
    
    COPY pyproject.toml    /colmena/pyproject.toml

    COPY deployment /colmena/
    WORKDIR /colmena
    RUN python3 -m pip install --no-cache-dir .
    ENTRYPOINT [ "python3", "-m", "colmena_deploy" ]