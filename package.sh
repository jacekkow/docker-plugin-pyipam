#!/bin/bash

set -e -x

NAME=${NAME:-jacekkow/pyipam}
VERSIONS=${VERSIONS:-latest}

DIR=$(dirname "$0")

cd "${DIR}" || exit 1
sudo rm -Rf rootfs
docker build -t "${NAME}" . || exit 1
id=$(docker create "${NAME}" true)
sudo mkdir -p rootfs
docker export "${id}" | sudo tar -x -C rootfs
docker rm -vf "${id}"
docker plugin disable "${NAME}" || true
docker plugin rm "${NAME}" || true
sudo chmod 755 rootfs && sudo chmod -R o=g rootfs/usr/src
if [ `echo ${VERSIONS} | wc -w` -gt 1 ]; then
  for VERSION in ${VERSIONS}; do
    sudo docker plugin create "${NAME}:${VERSION}" .
    docker plugin push "${NAME}:${VERSION}"
    docker plugin rm "${NAME}:${VERSION}"
  done
else
  sudo docker plugin create "${NAME}:${VERSIONS}" .
  docker plugin enable "${NAME}:${VERSIONS}"
fi
