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
    MoldPathLoader,
    BinLoader,
    ArtifactLoader,
)


class BaseLoaderTestCase(unittest.TestCase):

    def test_base_loader_init_fail(self):
        with self.assertRaises(ValueError) as e:
            BaseLoader(registry_name='no-such-name')
        self.assertEqual(
            e.exception.args[0], "'no-such-name' does not resolve to a "
            "calmjs.base:BaseRegistry, got None instead"
        )

    def test_base_loader(self):
        # as calmjs should be installed, that would be a valid registry
        loader = BaseLoader('calmjs.registry')
        with self.assertRaises(NotImplementedError):
            loader.invoke()

        identifier = object()
        with self.assertRaises(NotImplementedError):
            loader(identifier)

        self.assertEqual((identifier,), loader.resolve(identifier))


class MoldPathLoaderTestCase(unittest.TestCase):

    def test_base_loader_init_fail(self):
        with self.assertRaises(ValueError) as e:
            MoldPathLoader(registry_name='no-such-name')
        self.assertEqual(
            e.exception.args[0], "'no-such-name' does not resolve to a "
            "nunja.registry:MoldRegistry, got None instead"
        )

    def test_base_loader(self):
        registry = Mock()
        registry.lookup_path.return_value = '/some/target/path'
        loader = MoldPathLoader()
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


class ArtifactLoaderTestCase(unittest.TestCase):

    def test_resolve(self):
        loader = ArtifactLoader()
        self.assertEqual(
            loader.resolve('thing:file:txt'),
            ['thing', 'file:txt'],
        )

        with self.assertRaises(ValueError) as e:
            loader.resolve('bad')
        self.assertEqual(
            e.exception.args[0], "'bad' is an invalid reference to a package "
            "artifact; it must be in the form of "
            "'{package_name}:{artifact_name}'"
        )

    def test_base_loader(self):
        registry = Mock()
        tf = NamedTemporaryFile()
        registry.get_artifact_filename.return_value = tf.name
        self.addCleanup(tf.close)
        tf.write(b'somedata')
        tf.flush()

        loader = ArtifactLoader()
        loader.registry = registry

        result = loader('some.package:data.txt')
        self.assertTrue(registry.lookup_path.called_with(
            mold_id_path='some.package/mold/target'))

        self.assertEqual(result, b'somedata')
