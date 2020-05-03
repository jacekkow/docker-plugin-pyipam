from .Ipam import *

spaces = {
    'local': Space('local'),
    'global': Space('global'),
}


def get_space_pool(full_id: str):
    space_id, pool_id = full_id.rsplit('-', 2)
    space = spaces[space_id]
    return space, space.get_pool(pool_id)


__all__ = ['spaces', 'get_space_pool']
