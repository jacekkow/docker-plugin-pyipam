# pyIPAM - Docker Plugin for IPAM

Simple IPAM plugin for Docker Engine that correctly handles IPv6 addresses
(see https://github.com/docker/for-linux/issues/931 for bug details).

It should be a drop-in replacement for "default" IPAM module.

## Installation

Plugin is packaged as [Docker Engine-managed plugin](https://docs.docker.com/engine/extend/).

To install it simply run:

```bash
docker plugin install jacekkow/pyipam
```

Then you can use it in newly-created networks:

```bash
docker network create --ipam-driver jacekkow/pyipam new-network
```

Check out [`test_integration.sh`](test_integration.sh) for more examples.

## Manual packaging

In order to test this module in development environment, you can build it
by following [Docker Engine documentation](https://docs.docker.com/engine/extend/#developing-a-plugin).

You can also use `package.sh` helper script which will perform
all the steps (including installation) automatically.


