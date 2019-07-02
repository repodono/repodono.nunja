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
    StaticProvider,
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


class MoldDataRendererTestCase(unittest.TestCase):
    """
    MoldDataRendere
    """

    def test_base_render(self):
        loader = Mock()
        loader.return_value = 'output'
        renderer = MoldDataRenderer(loader=loader)
        result = renderer(mold_id_path='some.demo/mold/file.txt')
        self.assertTrue(loader.called_with(
            mold_id_path='some.demo/mold/file.txt'))
        self.assertEqual(result.content, 'output')


class StaticProviderTestCase(unittest.TestCase):
    """
    StaticProvider
    """

    def test_base_lookup(self):
        mapping = {
            'logo.png': 'some.demo/mold/logo.png',
            'glyphs.png': 'some.demo/mold/glyphs.png',
        }
        loader = Mock()
        loader.return_value = 'output'
        renderer = MoldDataRenderer(loader=loader)
        sp = StaticProvider(mapping=mapping, renderer=renderer)
        result = sp(filename='logo.png')
        self.assertTrue(loader.called_with(
            mold_id_path='some.demo/mold/logo.png'))
        self.assertEqual(result.content, 'output')
