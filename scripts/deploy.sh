#!/usr/bin/env bash

set -e;

image_tag="latest";
image_full_name="devartis/djangodocker:$image_tag";

echo "Building image '$image_full_name'";
docker build . -f "$image_full_name";

echo "Authenticating";
echo "$DOCKER_PASS" | docker login -u="$DOCKER_USERNAME" --password-stdin;

echo "Pushing image '$image_full_name'";
docker push "$image_full_name";
echo "Push finished!";

exit 0;