import ipaddress
import random

from docker_plugin_api.Plugin import InputValidationException


def random_hex(len=4):
    return ''.join(random.choice('0123456789abcdef') for _ in range(len))


class Pool:
    def __init__(self, pool: str = None, options: dict = None, subPool: str = None, v6: bool = None):
        if pool == '':
            pool = None
        if options is None:
            options = {}
        if subPool == '':
            subPool = None

        if pool is None and subPool is not None:
            raise InputValidationException('Trying to allocate subPool without pool')
        if pool is None and v6 is None:
            raise InputValidationException('Trying to get random pool without specifying IP version (v6 field)')

        if pool is None:
            if subPool is not None:
                raise InputValidationException('Trying to allocate subPool without pool')
            elif v6 is None:
                raise InputValidationException('Trying to get random pool without specifying IP version (v6 field)')

            if v6:
                pool = 'fd00:{}:{}:{}::/64'.format(random_hex(), random_hex(), random_hex())
            else:
                pool = '172.{}.{}.0/24'.format(random.randrange(16, 32), random.randrange(0, 256))

        self.pool = ipaddress.ip_network(pool, strict=False)
        if subPool is not None:
            self.subpool = ipaddress.ip_network(subPool, strict=False)
        else:
            self.subpool = self.pool

        if not self.subpool.subnet_of(self.pool):
            raise InputValidationException('Subpool must be a subnet of pool')

        self.allocations = set()
        self.current = self.subpool.hosts()

        self.v6 = isinstance(self.pool, ipaddress.IPv6Network)

    def __eq__(self, pool: 'Pool') -> bool:
        return self.v6 == pool.v6 and self.pool == pool.pool and self.subpool == pool.subpool

    def overlaps(self, pool: 'Pool') -> bool:
        if self.v6 != pool.v6:
            raise InputValidationException('Cannot compare v6 and non-v6 pools')
        return self.pool.overlaps(pool.pool)

    def _is_allocated(self, address: str):
        return str(address) in self.allocations

    def _find_next_address(self):
        for address in self.current:
            if not self._is_allocated(address):
                return address
        self.current = self.subpool.hosts()
        for address in self.current:
            if not self._is_allocated(address):
                return address
        raise InputValidationException('No free addresses in pool')

    def allocate(self, address: str = None) -> str:
        if address is None or address == '':
            address = self._find_next_address()
        else:
            address = ipaddress.ip_address(address)

        if self.pool.network_address == address:
            raise InputValidationException('Cannot allocate network address to a host')
        if not self.v6 and self.pool.broadcast_address == address:
            raise InputValidationException('Cannot allocate broadcast address to a host')
        if address not in self.pool:
            raise InputValidationException('Requested address does not belong to a pool')

        address = str(address)
        if self._is_allocated(address):
            raise InputValidationException('Requested address {} is already used'.format(address))
        self.allocations.add(address)

        return '{}/{}'.format(address, self.pool.prefixlen)

    def deallocate(self, address: str):
        address = ipaddress.ip_address(address)
        address = str(address)
        if address in self.allocations:
            self.allocations.remove(address)

    def __str__(self):
        return str(self.pool)


class Space:
    def __init__(self, name: str):
        self.name = name
        self.pools = {}
        self.pools6 = {}

    def add_pool(self, pool: Pool) -> str:
        check = self.pools6 if pool.v6 else self.pools
        for id, p in check.items():
            if pool == p:
                return id
            if pool.overlaps(p):
                raise InputValidationException('There is already defined pool {} that overlaps this one'.format(id))
        check[str(pool)] = pool
        return str(pool)

    def get_pool(self, pool: str) -> Pool:
        pool = str(pool)
        if pool in self.pools:
            return self.pools[pool]
        elif pool in self.pools6:
            return self.pools6[pool]
        else:
            raise InputValidationException('Unknown pool {}'.format(pool))

    def remove_pool(self, pool: str):
        pool = str(pool)
        if pool in self.pools:
            del self.pools[pool]
        elif pool in self.pools6:
            del self.pools6[pool]
        else:
            raise InputValidationException('Unknown pool {}'.format(pool))


__all__ = ['random_hex', 'Pool', 'Space']
