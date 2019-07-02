"""
Base loader test cases

Integration tests with the nunja registries will be done in a separate
integration test case module.
"""

import unittest
from unittest.mock import Mock
from tempfile import NamedTemporaryFile

from repodono.nunja.loader import (
    BaseLoader,
    BinLoader,
)


class BaseLoaderTestCase(unittest.TestCase):

    def test_base_loader_init_fail(self):
        with self.assertRaises(ValueError) as e:
            BaseLoader(registry_name='no-such-name')
        self.assertEqual(
            e.exception.args[0], "'no-such-name' does not resolve to a "
            "nunja.registry:MoldRegistry, got None instead"
        )

    def test_base_loader(self):
        registry = Mock()
        registry.lookup_path.return_value = '/some/target/path'
        loader = BaseLoader()
        loader.registry = registry
        result = loader('some.package/mold/target')
        self.assertEqual(result, '/some/target/path')
        self.assertTrue(registry.lookup_path.called_with(
            mold_id_path='some.package/mold/target'))


class BinLoaderTestCase(unittest.TestCase):

    def test_base_loader(self):
        registry = Mock()
        tf = NamedTemporaryFile()
        registry.lookup_path.return_value = tf.name
        self.addCleanup(tf.close)
        tf.write(b'somedata')
        tf.flush()

        loader = BinLoader()
        loader.registry = registry
        result = loader('some.package/mold/target')
        self.assertTrue(registry.lookup_path.called_with(
            mold_id_path='some.package/mold/target'))

        self.assertEqual(result, b'somedata')
