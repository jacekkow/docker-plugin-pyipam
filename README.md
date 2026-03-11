# pyIPAM - Docker Plugin for IPAM

Simple IPAM plugin for Docker Engine that correctly handles IPv6 addresses
(see https://github.com/docker/for-linux/issues/931 for bug details).

It should be a drop-in replacement for "default" IPAM module.

![Build status](https://github.com/jacekkow/docker-plugin-pyipam/workflows/Release/badge.svg)

## Installation

Plugin is packaged as [Docker Engine-managed plugin](https://docs.docker.com/engine/extend/).
Check out [plugin page on Docker Hub](https://hub.docker.com/p/jacekkow/pyipam).

To install it simply run:

```bash
docker plugin install jacekkow/pyipam
```

Then you can use it in newly-created networks:

```bash
docker network create --ipam-driver jacekkow/pyipam:latest new-network
```

Check out [`test_integration.sh`](test_integration.sh) for more examples.

## Options

To use options, add `--ipam-opt option=value` as an argument of `docker network create`:

```bash
docker network create --ipam-driver jacekkow/pyipam:latest --ipam-opt ptp=1 new-network
```

Available options:

`ptp=1`

When set addresses with netmask /32 (IPv4) or /128 (IPv6) are handed out.
In this mode all IP addresses are handed out from the subnet,
including ones that would be "network address" and "broadcast address"!

`validate=0`

Do not validate duplicate IP address assignment. This IPAM plugin would
then happily hand out already-used addresses if such were manually specified.
This option does not affect automatic assignments.
Note that this module does not track how many times the IP was handed out,
hence if two containers have the same IP and one of them stops,
IP will be marked as free!

## Manual packaging

In order to test this module in development environment, you can build it
by following [Docker Engine documentation](https://docs.docker.com/engine/extend/#developing-a-plugin).

You can also use `package.sh` helper script which will perform
all the steps (including installation) automatically.
