from docker_plugin_api.Plugin import Blueprint
import flask
from .Ipam import *
from .IpamDriverData import *
from docker_plugin_api.IpamDriverEntities import *

app = Blueprint('IpamDriver', __name__)


@app.route('/IpamDriver.GetCapabilities', methods=['POST'])
def GetCapabilities():
    return {
        'RequiresMACAddress': True,
        'RequiresRequestReplay': True,
    }


@app.route('/IpamDriver.GetDefaultAddressSpaces', methods=['POST'])
def GetDefaultAddressSpaces():
    return {
        'LocalDefaultAddressSpace': 'local',
        'GlobalDefaultAddressSpace': 'global',
    }


@app.route('/IpamDriver.RequestPool', methods=['POST'])
def RequestPool():
    request = RequestPoolEntity(**flask.request.get_json(force=True))
    space = spaces[request.AddressSpace]
    pool = Pool(pool=request.Pool, subPool=request.SubPool, options=request.Options, v6=request.V6)
    pool_id = space.add_pool(pool)
    full_id = '{}-{}'.format(space.name, pool_id)
    return {
        'PoolID': full_id,
        'Pool': str(pool),
        'Data': {},
    }


@app.route('/IpamDriver.ReleasePool', methods=['POST'])
def ReleasePool():
    request = ReleasePoolEntity(**flask.request.get_json(force=True))
    space, pool = get_space_pool(request.PoolID)
    space.remove_pool(pool)
    return {}


@app.route('/IpamDriver.RequestAddress', methods=['POST'])
def RequestAddress():
    request = RequestAddressEntity(**flask.request.get_json(force=True))
    space, pool = get_space_pool(request.PoolID)
    address = pool.allocate(request.Address)
    return {
        'Address': address,
        'Data': {},
    }


@app.route('/IpamDriver.ReleaseAddress', methods=['POST'])
def ReleaseAddress():
    request = ReleaseAddressEntity(**flask.request.get_json(force=True))
    space, pool = get_space_pool(request.PoolID)
    pool.deallocate(request.Address)
    return {}


__all__ = ['app']
