import ipaddress
import unittest

from lib.Ipam import *
from docker_plugin_api.Plugin import InputValidationException


class PoolInvalidCreateTest(unittest.TestCase):
    def test_noargs(self):
        with self.assertRaises(InputValidationException):
            Pool()

    def test_subpool_only(self):
        with self.assertRaises(InputValidationException):
            Pool(subPool='127.0.0.0/24')

    def test_subpool_invalid(self):
        with self.assertRaises(InputValidationException):
            Pool(pool='127.0.0.0/24', subPool='127.1.2.3/24')


class PoolCreateTest(unittest.TestCase):
    def test_auto_ipv4(self):
        pool = Pool(v6=False)
        ip = ipaddress.ip_network(str(pool))
        self.assertTrue(isinstance(ip, ipaddress.IPv4Network))

    def test_auto_ipv6(self):
        pool = Pool(v6=True)
        ip = ipaddress.ip_network(str(pool))
        self.assertTrue(isinstance(ip, ipaddress.IPv6Network))

    def test_pool_ipv4(self):
        pool = Pool(pool='127.0.0.1/24')
        ip = ipaddress.ip_network(str(pool))
        self.assertTrue(isinstance(ip, ipaddress.IPv4Network))
        self.assertEqual(ip, ipaddress.ip_network('127.0.0.0/24'))

    def test_pool_ipv6(self):
        pool = Pool(pool='fd00:a:b:c:1:2:3:4/64')
        ip = ipaddress.ip_network(str(pool))
        self.assertTrue(isinstance(ip, ipaddress.IPv6Network))
        self.assertEqual(ip, ipaddress.ip_network('fd00:a:b:c::/64'))

    def test_subpool_ipv4(self):
        pool = Pool(pool='127.0.0.1/8', subPool='127.0.0.2/24')
        ip = ipaddress.ip_network(str(pool))
        self.assertTrue(isinstance(ip, ipaddress.IPv4Network))
        self.assertEqual(ip, ipaddress.ip_network('127.0.0.0/8'))
        ip = ipaddress.ip_network(str(pool.subpool))
        self.assertTrue(isinstance(ip, ipaddress.IPv4Network))
        self.assertEqual(ip, ipaddress.ip_network('127.0.0.0/24'))

    def test_subpool_ipv6(self):
        pool = Pool(pool='fd00:a:b:c:1:2:3:4/48', subPool='fd00:a:b:c:1:2:3:4/64')
        ip = ipaddress.ip_network(str(pool))
        self.assertTrue(isinstance(ip, ipaddress.IPv6Network))
        self.assertEqual(ip, ipaddress.ip_network('fd00:a:b::/48'))
        ip = ipaddress.ip_network(str(pool.subpool))
        self.assertTrue(isinstance(ip, ipaddress.IPv6Network))
        self.assertEqual(ip, ipaddress.ip_network('fd00:a:b:c::/64'))


class PoolComparisonTest(unittest.TestCase):
    def test_pool_same_ipv4(self):
        pool1 = Pool(pool='127.0.0.1/8')
        pool2 = Pool(pool='127.0.0.2/8')
        self.assertEqual(pool1, pool2)
        self.assertEqual(pool2, pool1)

    def test_pool_same_ipv6(self):
        pool1 = Pool(pool='fd00:a:b::/64')
        pool2 = Pool(pool='fd00:a:b:0:1:2:3:4/64')
        self.assertEqual(pool1, pool2)
        self.assertEqual(pool2, pool1)


class PoolOverlapTest(unittest.TestCase):
    def test_pool_overlap_ipv4(self):
        pool1 = Pool(pool='127.0.0.1/24')
        pool2 = Pool(pool='127.0.2.3/16')
        self.assertTrue(pool1.overlaps(pool1))
        self.assertTrue(pool2.overlaps(pool2))
        self.assertTrue(pool1.overlaps(pool2))
        self.assertTrue(pool2.overlaps(pool1))

    def test_pool_overlap_ipv6(self):
        pool1 = Pool(pool='fe80::/64')
        pool2 = Pool(pool='fe80::1:2:3:4/72')
        self.assertTrue(pool1.overlaps(pool1))
        self.assertTrue(pool2.overlaps(pool2))
        self.assertTrue(pool1.overlaps(pool2))
        self.assertTrue(pool2.overlaps(pool1))


class PoolAllocateInvalidTest(unittest.TestCase):
    def test_pool_allocate_invalid_ipv4(self):
        pool = Pool(pool='127.0.0.0/30')
        self.assertEqual(pool.allocate(), '127.0.0.1/30')
        self.assertEqual(pool.allocate(), '127.0.0.2/30')
        with self.assertRaises(InputValidationException):
            pool.allocate('126.255.255.255')
        with self.assertRaises(InputValidationException):
            pool.allocate('127.0.0.0')
        with self.assertRaises(InputValidationException):
            pool.allocate('127.0.0.1')
        with self.assertRaises(InputValidationException):
            pool.allocate('127.0.0.2')
        with self.assertRaises(InputValidationException):
            pool.allocate('127.0.0.3')
        with self.assertRaises(InputValidationException):
            pool.allocate('127.0.0.4')

    def test_pool_allocate_invalid_ipv6(self):
        pool = Pool(pool='fd00::/126')
        self.assertEqual(pool.allocate(), 'fd00::1/126')
        self.assertEqual(pool.allocate(), 'fd00::2/126')
        self.assertEqual(pool.allocate(), 'fd00::3/126')
        with self.assertRaises(InputValidationException):
            pool.allocate('fcff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
        with self.assertRaises(InputValidationException):
            pool.allocate('fd00::')
        with self.assertRaises(InputValidationException):
            pool.allocate('fd00::1')
        with self.assertRaises(InputValidationException):
            pool.allocate('fd00::2')
        with self.assertRaises(InputValidationException):
            pool.allocate('fd00::3')
        with self.assertRaises(InputValidationException):
            pool.allocate('fd00::4')


class PoolAllocateOrderTest(unittest.TestCase):
    def test_pool_allocate_ipv4(self):
        pool = Pool(pool='127.0.0.0/30')
        self.assertEqual(pool.allocate(), '127.0.0.1/30')
        self.assertEqual(pool.allocate(), '127.0.0.2/30')
        with self.assertRaises(InputValidationException):
            pool.allocate()
        with self.assertRaises(InputValidationException):
            pool.allocate()
        with self.assertRaises(InputValidationException):
            pool.allocate()

    def test_pool_allocate_ipv6(self):
        pool = Pool(pool='fd00::/126')
        self.assertEqual(pool.allocate(), 'fd00::1/126')
        self.assertEqual(pool.allocate(), 'fd00::2/126')
        self.assertEqual(pool.allocate(), 'fd00::3/126')
        with self.assertRaises(InputValidationException):
            pool.allocate()
        with self.assertRaises(InputValidationException):
            pool.allocate()
        with self.assertRaises(InputValidationException):
            pool.allocate()

    def test_pool_allocate_large_ipv4(self):
        pool = Pool(pool='127.0.0.0/8')
        self.assertEqual(pool.allocate(), '127.0.0.1/8')
        self.assertEqual(pool.allocate(), '127.0.0.2/8')

    def test_pool_allocate_large_ipv6(self):
        pool = Pool(pool='fd00::/56')
        self.assertEqual(pool.allocate(), 'fd00::1/56')
        self.assertEqual(pool.allocate(), 'fd00::2/56')


class PoolAllocateManualTest(unittest.TestCase):
    def test_pool_allocate_ipv4(self):
        pool = Pool(pool='127.0.0.0/28')
        self.assertEqual(pool.allocate('127.0.0.3'), '127.0.0.3/28')
        self.assertEqual(pool.allocate('127.0.0.5'), '127.0.0.5/28')
        self.assertEqual(pool.allocate('127.0.0.11'), '127.0.0.11/28')
        self.assertEqual(pool.allocate('127.0.0.14'), '127.0.0.14/28')
        self.assertEqual(pool.allocate(), '127.0.0.1/28')
        self.assertEqual(pool.allocate(), '127.0.0.2/28')
        self.assertEqual(pool.allocate(), '127.0.0.4/28')
        self.assertEqual(pool.allocate(), '127.0.0.6/28')
        self.assertEqual(pool.allocate(), '127.0.0.7/28')
        self.assertEqual(pool.allocate(), '127.0.0.8/28')
        self.assertEqual(pool.allocate(), '127.0.0.9/28')
        self.assertEqual(pool.allocate(), '127.0.0.10/28')
        self.assertEqual(pool.allocate(), '127.0.0.12/28')
        self.assertEqual(pool.allocate(), '127.0.0.13/28')
        with self.assertRaises(InputValidationException):
            pool.allocate()

    def test_pool_allocate_ipv6(self):
        pool = Pool(pool='fd00::/124')
        self.assertEqual(pool.allocate('fd00::3'), 'fd00::3/124')
        self.assertEqual(pool.allocate('fd00::5'), 'fd00::5/124')
        self.assertEqual(pool.allocate('fd00::b'), 'fd00::b/124')
        self.assertEqual(pool.allocate('fd00::e'), 'fd00::e/124')
        self.assertEqual(pool.allocate(), 'fd00::1/124')
        self.assertEqual(pool.allocate(), 'fd00::2/124')
        self.assertEqual(pool.allocate(), 'fd00::4/124')
        self.assertEqual(pool.allocate(), 'fd00::6/124')
        self.assertEqual(pool.allocate(), 'fd00::7/124')
        self.assertEqual(pool.allocate(), 'fd00::8/124')
        self.assertEqual(pool.allocate(), 'fd00::9/124')
        self.assertEqual(pool.allocate(), 'fd00::a/124')
        self.assertEqual(pool.allocate(), 'fd00::c/124')
        self.assertEqual(pool.allocate(), 'fd00::d/124')
        self.assertEqual(pool.allocate(), 'fd00::f/124')
        with self.assertRaises(InputValidationException):
            pool.allocate()

    def test_subpool_allocate_ipv4(self):
        pool = Pool(pool='127.0.0.0/8', subPool='127.0.0.0/30')
        self.assertEqual(pool.allocate('127.0.0.2'), '127.0.0.2/8')
        self.assertEqual(pool.allocate('127.1.2.3'), '127.1.2.3/8')
        self.assertEqual(pool.allocate('127.255.0.5'), '127.255.0.5/8')
        self.assertEqual(pool.allocate('127.248.255.11'), '127.248.255.11/8')
        self.assertEqual(pool.allocate('127.71.12.14'), '127.71.12.14/8')
        self.assertEqual(pool.allocate(), '127.0.0.1/8')
        # This is not-fully-correct as we can theoretically assign 127.0.0.3 - feel free to fix it
        with self.assertRaises(InputValidationException):
            pool.allocate()
        self.assertEqual(pool.allocate('127.0.0.3'), '127.0.0.3/8')

    def test_subpool_middle_allocate_ipv4(self):
        pool = Pool(pool='127.0.0.0/8', subPool='127.248.255.0/30')
        self.assertEqual(pool.allocate('127.0.0.2'), '127.0.0.2/8')
        self.assertEqual(pool.allocate('127.1.2.3'), '127.1.2.3/8')
        self.assertEqual(pool.allocate('127.255.0.5'), '127.255.0.5/8')
        self.assertEqual(pool.allocate('127.248.255.2'), '127.248.255.2/8')
        self.assertEqual(pool.allocate('127.71.12.14'), '127.71.12.14/8')
        self.assertEqual(pool.allocate(), '127.248.255.1/8')
        # This is not-fully-correct as we can theoretically assign 127.248.255.0 and 127.248.255.3 - feel free to fix it
        with self.assertRaises(InputValidationException):
            pool.allocate()
        self.assertEqual(pool.allocate('127.248.255.0'), '127.248.255.0/8')
        self.assertEqual(pool.allocate('127.248.255.3'), '127.248.255.3/8')

    def test_subpool_allocate_ipv6(self):
        pool = Pool(pool='fe80::/64', subPool='fe80::/126')
        self.assertEqual(pool.allocate('fe80::2'), 'fe80::2/64')
        self.assertEqual(pool.allocate('fe80::1:2:3:4'), 'fe80::1:2:3:4/64')
        self.assertEqual(pool.allocate('fe80::ffff:fefe:fdfd:fcfc'), 'fe80::ffff:fefe:fdfd:fcfc/64')
        self.assertEqual(pool.allocate(), 'fe80::1/64')
        self.assertEqual(pool.allocate(), 'fe80::3/64')
        with self.assertRaises(InputValidationException):
            pool.allocate()

    def test_subpool_middle_allocate_ipv6(self):
        pool = Pool(pool='fe80::/64', subPool='fe80::ffff:0:0:0/126')
        self.assertEqual(pool.allocate('fe80::2'), 'fe80::2/64')
        self.assertEqual(pool.allocate('fe80::1:2:3:4'), 'fe80::1:2:3:4/64')
        self.assertEqual(pool.allocate('fe80::ffff:0:0:2'), 'fe80::ffff:0:0:2/64')
        self.assertEqual(pool.allocate(), 'fe80::ffff:0:0:1/64')
        self.assertEqual(pool.allocate(), 'fe80::ffff:0:0:3/64')
        # This is not-fully-correct as we can theoretically assign fe80::ffff:0:0:0 - feel free to fix it
        with self.assertRaises(InputValidationException):
            pool.allocate()
        self.assertEqual(pool.allocate('fe80::ffff:0:0:0'), 'fe80::ffff:0:0:0/64')


class TestPoolAllocateRelease(unittest.TestCase):
    def test_pool_allocate_release_ipv4(self):
        pool = Pool(pool='127.0.0.0/29')
        self.assertEqual(pool.allocate('127.0.0.3'), '127.0.0.3/29')
        self.assertEqual(pool.allocate('127.0.0.5'), '127.0.0.5/29')
        self.assertEqual(pool.allocate(), '127.0.0.1/29')
        self.assertEqual(pool.allocate(), '127.0.0.2/29')
        pool.deallocate('127.0.0.3')
        self.assertEqual(pool.allocate(), '127.0.0.3/29')
        self.assertEqual(pool.allocate(), '127.0.0.4/29')
        self.assertEqual(pool.allocate(), '127.0.0.6/29')
        with self.assertRaises(InputValidationException):
            pool.allocate()
        pool.deallocate('127.0.0.5')
        self.assertEqual(pool.allocate(), '127.0.0.5/29')
        pool.deallocate('127.0.0.1')
        pool.deallocate('127.0.0.2')
        self.assertEqual(pool.allocate('127.0.0.2'), '127.0.0.2/29')
        self.assertEqual(pool.allocate(), '127.0.0.1/29')

    def test_pool_allocate_release_ipv6(self):
        pool = Pool(pool='fe80::/125')
        self.assertEqual(pool.allocate('fe80::3'), 'fe80::3/125')
        self.assertEqual(pool.allocate('fe80::5'), 'fe80::5/125')
        self.assertEqual(pool.allocate(), 'fe80::1/125')
        self.assertEqual(pool.allocate(), 'fe80::2/125')
        pool.deallocate('fe80::3')
        self.assertEqual(pool.allocate(), 'fe80::3/125')
        self.assertEqual(pool.allocate(), 'fe80::4/125')
        self.assertEqual(pool.allocate(), 'fe80::6/125')
        self.assertEqual(pool.allocate(), 'fe80::7/125')
        with self.assertRaises(InputValidationException):
            pool.allocate()
        pool.deallocate('fe80::5')
        self.assertEqual(pool.allocate(), 'fe80::5/125')
        pool.deallocate('fe80::1')
        pool.deallocate('fe80::2')
        self.assertEqual(pool.allocate('fe80::2'), 'fe80::2/125')
        self.assertEqual(pool.allocate(), 'fe80::1/125')
