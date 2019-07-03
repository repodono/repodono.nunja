"""
These will simply be isolated, independent test cases.

Integration tests will be done in a separate test module.
"""

import unittest
from unittest.mock import Mock

from repodono.model.http import Response
from repodono.nunja.render import (
    NunjaRenderer,
    MoldDataRenderer,
    ArtifactRenderer,
    MappedDataProvider,
)


class NunjaRendererTestCase(unittest.TestCase):

    def test_base_render_called_with(self):
        engine = Mock()
        engine.render.return_value = 'output'
        renderer = NunjaRenderer(engine=engine)
        result = renderer('mold_id', data={'key': 'value'})
        self.assertTrue(engine.execute.called_with(
            mold_id='mold_id', data={'key': 'value'}))

        self.assertTrue(isinstance(result, Response))
        self.assertEqual(result.content, 'output')
        self.assertEqual(result.headers, {
            'Content-type': 'text/html',
        })


class InstancedRendererTestCase(unittest.TestCase):
    """
    These are in no way a proper test.

    A separate integration test will be provided with the aid of a set
    of integration data.
    """

    # XXX note that these tests are actually redundant at this point due
    # to the usage of mocks.

    def test_mold_data_render(self):
        loader = Mock()
        loader.return_value = 'output'
        renderer = MoldDataRenderer(loader=loader)
        result = renderer(identifier='some.demo/mold/file.txt')
        self.assertTrue(loader.called_with(
            identifier='some.demo/mold/file.txt'))
        self.assertEqual(result.content, 'output')

    def test_artifact_render(self):
        loader = Mock()
        loader.return_value = 'output'
        renderer = ArtifactRenderer(loader=loader)
        result = renderer(identifier='some.package:artifact.bin')
        self.assertTrue(loader.called_with(
            identifier='some.package:artifact.bin'))
        self.assertEqual(result.content, 'output')


class MappedDataProviderTestCase(unittest.TestCase):
    """
    MappedDataProvider
    """

    def test_base_lookup(self):
        mapping = {
            'logo.png': 'some.demo/mold/logo.png',
            'glyphs.png': 'some.demo/mold/glyphs.png',
        }
        loader = Mock()
        loader.return_value = 'output'
        renderer = MoldDataRenderer(loader=loader)
        provider = MappedDataProvider(mapping=mapping, renderer=renderer)
        result = provider(filename='logo.png')
        self.assertTrue(loader.called_with(
            identifier='some.demo/mold/logo.png'))
        self.assertEqual(result.content, 'output')
