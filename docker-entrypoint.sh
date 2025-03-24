#!/bin/bash
set -e

# Register QEMU emulators for multi-arch builds
docker run --rm --privileged tonistiigi/binfmt --install all || true

# Initialize buildx builder if not already present
if ! docker buildx inspect mybuilder >/dev/null 2>&1; then
    docker buildx create --use --name mybuilder
    docker buildx inspect --bootstrap
fi

# Run your deployment tool
exec python3 -m deployment.colmena_deploy "$@"
