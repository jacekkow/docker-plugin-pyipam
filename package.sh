#!/bin/bash -x

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
docker plugin disable "${NAME}"
docker plugin rm "${NAME}"
sudo chmod 755 rootfs rootfs/usr/src/app/.local && sudo chmod -R o=g rootfs/usr/src
for VERSION in ${VERSIONS}; do
  sudo docker plugin create "${NAME}:${VERSION}" .
done
sudo du -hs rootfs
for VERSION in ${VERSIONS}; do
  docker plugin enable "${NAME}:${VERSION}" || exit 1
  break
done
