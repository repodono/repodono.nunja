"""
These will simply be isolated, independent test cases.

Integration tests will be done in a separate test module.
"""

import unittest
from unittest.mock import Mock

from repodono.model.http import Response
from repodono.nunja.render import (
    TemplateRenderWrapper,
    JinjaRenderer,
    NunjaRenderer,
    MoldDataRenderer,
    ArtifactRenderer,
    MappedDataProvider,
)


class TemplateWrapperTestCase(unittest.TestCase):

    def test_construction(self):
        result = TemplateRenderWrapper(object, {'content-type': 'text/plain'})
        self.assertIs(result.template, object)
        self.assertEqual(result.headers, {'content-type': 'text/plain'})
        self.assertEqual(result.data, {})

    def test_build_data(self):
        trw = TemplateRenderWrapper(object, {}, {'a': 'b'})
        self.assertEqual({
            'a': 'b',
            'c': 'd',
        }, trw.build_data(c='d'))

        self.assertEqual({
            'a': 'bbbb',
        }, trw.build_data(a='bbbb'))

    def test_prerender(self):
        template = object()
        headers = {}
        trw = TemplateRenderWrapper(template, headers)
        trw1 = trw.prerender(a='b')
        self.assertIs(trw1.template, template)
        self.assertIs(trw1.headers, headers)
        self.assertEqual(trw1.data, {'a': 'b'})
        trw2 = trw1.prerender(c='d')
        self.assertIs(trw2.template, template)
        self.assertIs(trw2.headers, headers)
        self.assertEqual(trw2.data, {'a': 'b', 'c': 'd'})

    def test_call(self):
        template = Mock()
        template.render.return_value = ''
        headers = {}
        trw = TemplateRenderWrapper(template, headers)
        trw()
        template.render.assert_called_with()

        trw1 = trw.prerender(a='b')
        trw1()
        template.render.assert_called_with(a='b')

        trw1(cc='dd')
        template.render.assert_called_with(a='b', cc='dd')


class JinjaRendererTestCase(unittest.TestCase):

    def test_render_template_called_with(self):
        engine = Mock()
        engine.render_template.return_value = 'output'
        renderer = JinjaRenderer(engine=engine)
        result = renderer('mold_id', data={'key': 'value'})
        engine.render_template.assert_called_with(
            'mold_id', data={'key': 'value'})

        self.assertTrue(isinstance(result, Response))
        self.assertEqual(result.content, b'output')
        self.assertEqual(result.headers, {
            'Content-type': 'text/html',
        })

    def test_load_template_called_with(self):
        engine = Mock()
        template = Mock()
        engine.load_template.return_value = template
        renderer = JinjaRenderer(engine=engine)
        result = renderer.load_template('mold_id', data={'key': 'value'})
        self.assertTrue(result, isinstance(result, TemplateRenderWrapper))
        self.assertIs(result.template, template)


class NunjaRendererTestCase(unittest.TestCase):

    def test_base_render_called_with(self):
        engine = Mock()
        engine.render.return_value = 'output'
        renderer = NunjaRenderer(engine=engine)
        result = renderer('mold_id', data={'key': 'value'})
        engine.render.assert_called_with(
            'mold_id', data={'key': 'value'})

        self.assertTrue(isinstance(result, Response))
        self.assertEqual(result.content, b'output')
        self.assertEqual(result.headers, {
            'Content-type': 'text/html',
        })

    def test_execute_called_with(self):
        engine = Mock()
        engine.execute.return_value = 'output'
        renderer = NunjaRenderer(engine=engine)
        result = renderer.execute('mold_id', data={'key': 'value'})
        engine.execute.assert_called_with('mold_id', data={'key': 'value'})
        self.assertEqual(result, 'output')

    def test_render_called_with(self):
        engine = Mock()
        engine.render.return_value = 'output'
        renderer = NunjaRenderer(engine=engine)
        result = renderer.render('mold_id', data={'key': 'value'})
        engine.render.assert_called_with('mold_id', data={'key': 'value'})
        self.assertEqual(result, 'output')

    def test_render_template_called_with(self):
        template = Mock()
        template.render.return_value = 'output'
        engine = Mock()
        engine.load_template.return_value = template
        renderer = NunjaRenderer(engine=engine)
        result = renderer.render_template(
            'mold_id_template', data={'key': 'value'})
        engine.load_template.assert_called_with('mold_id_template')
        template.render.assert_called_with(key='value')
        self.assertEqual(result, 'output')


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
        loader.assert_called_with('some.demo/mold/file.txt')
        self.assertEqual(result.content, b'output')

    def test_artifact_render(self):
        loader = Mock()
        loader.return_value = 'output'
        renderer = ArtifactRenderer(loader=loader)
        result = renderer(identifier='some.package:artifact.bin')
        loader.assert_called_with('some.package:artifact.bin')
        self.assertEqual(result.content, b'output')


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
        loader.assert_called_with('some.demo/mold/logo.png')
        self.assertEqual(result.content, b'output')
