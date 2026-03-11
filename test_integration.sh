#!/bin/bash

set -e -x

NAME=${NAME:-jacekkow/pyipam}
VERSION=${VERSION:-latest}

PLUGIN="${NAME}:${VERSION}"

docker network rm test1 || true
docker network rm test2 || true

docker network create \
  --internal \
  --driver bridge \
  --ipam-driver "${PLUGIN}" \
  --ipv6 \
  --subnet 192.168.255.0/24 \
  --ip-range 192.168.255.128/26 \
  --gateway 192.168.255.254 \
  --subnet 2001:db8::/32 \
  --ip-range 2001:db8:aaaa:bbbb::/64 \
  --gateway 2001:db8:ffff:ffff:ffff:ffff:ffff:ffff \
  test1

ADDRESSES=$(docker run --rm --network test1 \
  alpine \
  /sbin/ip addr show
)
if ! echo "${ADDRESSES}" | grep 192.168.255.129/24; then
	echo "ERROR: invalid IPv4 address assigned"
	exit 1
fi
if ! echo "${ADDRESSES}" | grep 2001:db8:aaaa:bbbb::1/32; then
	echo "ERROR: invalid IPv6 address assigned"
	exit 1
fi


ADDRESSES=$(docker run --rm --network test1 \
  --ip 192.168.255.25 --ip6 2001:db8:dddd:eeee:ffff:1:2:3 \
  alpine \
  /sbin/ip addr show
)
if ! echo "${ADDRESSES}" | grep 192.168.255.25/24; then
	echo "ERROR: invalid IPv4 address assigned"
	exit 1
fi
if ! echo "${ADDRESSES}" | grep 2001:db8:dddd:eeee:ffff:1:2:3/32; then
	echo "ERROR: invalid IPv6 address assigned"
	exit 1
fi

docker network rm test1


docker network create \
  --driver bridge \
  --ipam-driver "${PLUGIN}" \
  --ipv6 \
  --subnet 192.168.255.0/24 \
  --gateway 192.168.255.254 \
  --subnet 2001:db8::/32 \
  --gateway 2001:db8:ffff:ffff:ffff:ffff:ffff:ffff \
  test2

ROUTES=$(docker run --rm --network test2 \
  alpine \
  /sbin/ip route show
)
if ! echo "${ROUTES}" | grep 192.168.255.254; then
	echo "ERROR: invalid IPv4 route"
	exit 1
fi

ROUTES=$(docker run --rm --network test2 \
  alpine \
  /sbin/ip -6 route show
)
if ! echo "${ROUTES}" | grep 2001:db8:ffff:ffff:ffff:ffff:ffff:ffff; then
	echo "ERROR: invalid IPv6 route"
	exit 1
fi

docker network rm test2
