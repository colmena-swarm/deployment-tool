# COLMENA Deployment Tool Repository

This GitHub repository contains all the files and software necessary to deploy applications on a COLMENA platform. COLMENA (COLaboración entre dispositivos Mediante tecnología de ENjAmbre) aims to ease the development, deployment, operation and maintenance of extremely-high available, reliable and intelligent services running seamlessly across the device-edge-cloud continuum. It leverages a swarm approach organising a dynamic group of autonomous, collaborative nodes following an agile, fully-decentralised, robust, secure and trustworthy open architecture.

## Table of Contents
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)



## Repository Structure
The repository is organized into the following directories and files:
### Directories
- **deployment**: Script to deploy a service.
### Files
- **.gitignore**: Specifies files and directories to be ignored by Git.
- **changeLog**: Change highlights associated with official releases.
- **CODE_OF_CONDUCT.md**: Outlines the expected behavior and guidelines for participants within the project's community. 
- **CONTRIBUTING.md**: Overview of the repository, setup instructions, and basic usage examples.
- **Dockerfile**: File used to create a Docker image for the deployment tool.
- **LICENSE**: License information for the repository.
- **pyproject.toml**: Configuration file necessary for installing the tool.
- **README.md**: Overview of the repository, setup instructions, and basic usage examples.

## Getting Started

### Pre-requisits
 - Create a COLMENA service bundle using the COLMENA Programming Model
 - Clone this repository at <COLMENA_dt_path>
 - Create COLMENA platform on the desired infrastructure

### Running the service
Install dependencies:
```bash
python3 -m pip install .
```

Deploy an application on COLMENA:
``` bash
python3 -m deployment.colmena_deploy \
	--build_path="<path_to_the_service_root>/<service_modulename>/build" \
	--platform="linux/amd64" \
	--user=${DOCKER_USERNAME}
```
Multi-architecture builds (for example: --platform="linux/amd64,linux/arm64) are also supported, 
but configuration of Docker is needed (steps to follow here: https://docs.docker.com/build/building/multi-platform/).

You can add the --skip_build argument if images are already in Dockerhub.

For a full list of the deployment tool parameters:
```bash
python3 -m deployment.colmena_deploy -h
```


### Within a docker instance
1. Build the image locally
	```bash
	docker --debug build -t colmenaswarm/deployment-tool:latest .
	```
2. Execute the image mounting as a volume the build folder of the service
	``` bash
	docker run --rm \
		-v ~/.docker/config.json:/root/.docker/config.json \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v <path_to_the_service_root>/<service_modulename>/build:/app \
		--network=host \
		colmenaswarm/deployment-tool:latest \
		--build_path=/app\
		--platform="linux/amd64" \
		--user=${DOCKER_USERNAME}
	```


## Contributing
Please read our [contribution guidelines](CONTRIBUTING.md) before making a pull request.

## License
The COLMENA programming model is released under the Apache 2.0 license.
Copyright © 2022-2024 Barcelona Supercomputing Center - Centro Nacional de Supercomputación. All rights reserved.
See the [LICENSE](LICENSE) file for more information.


<sub>
	This work is co-financed by the COLMENA project of the UNICO I+D Cloud program that has the Ministry for Digital Transformation and of Civil Service and the EU-Next Generation EU as financing entities, within the framework of the PRTR and the MRR. It has also been supported by the Spanish Government (PID2019-107255GB-C21), MCIN/AEI /10.13039/501100011033 (CEX2021-001148-S), and Generalitat de Catalunya (2021-SGR-00412).
</sub>
<p align="center">
	<img src="https://github.com/colmena-swarm/.github/blob/assets/images/funding_logos/Logos_entidades_OK.png?raw=true" width="600">
</p>
