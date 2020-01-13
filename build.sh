#!/bin/bash

find . -type f -name '.DS_Store' -delete

BUILD_DATE="$(date '+%Y%m%d')"

BASE="rainchei/k8s-yaml-processor"

TAG="${GIT_COMMIT:-$(git describe --long --dirty --abbrev=10 --tags --always)}-${BUILD_DATE}"

# you must commit changes first
git diff --cached --exit-code || exit 1
git diff --exit-code || exit 2

DOCKER_BUILDKIT=1 docker build --pull -t "${BASE}:${TAG}" .

STATUS=$?

# If build was successful, then push to docker registry
if [ $STATUS -eq 0 ]; then
  docker push "${BASE}:${TAG}"
else
  exit $STATUS
fi

echo "${BASE}:${TAG}"



