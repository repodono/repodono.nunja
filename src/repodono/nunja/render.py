from functools import partial
from mimetypes import MimeTypes
from nunja.core import engine
from nunja.engine import JinjaEngine
from repodono.model.http import Response
from repodono.nunja.loader import BinLoader
from repodono.nunja.loader import ArtifactLoader


class TemplateRenderWrapper(object):

    def __init__(self, template, headers, data=None):
        self.template = template
        self.headers = headers
        self.data = data if isinstance(data, dict) else {}

    def build_data(self, **kw):
        data = {}
        data.update(self.data)
        data.update(kw)
        return data

    def prerender(self, **data):
        return type(self)(self.template, self.headers, self.build_data(**data))

    def __call__(self, **data):
        return Response(self.template.render(
            **self.build_data(**data)), self.headers)


class JinjaRenderer(object):

    def __init__(self, engine=JinjaEngine()):
        self.engine = engine

    def load_template(self, template_id, **headers):
        template = self.engine.load_template(template_id)
        headers.setdefault('content-type', 'text/html')
        return TemplateRenderWrapper(template, headers)

    def __call__(self, template_id, data={}, content_type='text/html'):
        """
        Generates a full response
        """

        content = self.engine.render_template(template_id, data=data)
        headers = {
            'content-type': content_type,
        }
        return Response(content, headers)


class NunjaRenderer(object):

    def __init__(self, engine=engine):
        self.engine = engine

    def execute(self, mold_id, data):
        return self.engine.execute(mold_id, data)

    def render(self, mold_id, data):
        return self.engine.render(mold_id, data)

    def render_template(self, mold_id_template, data):
        """
        Shorthand for rendering a template within a mold.
        """

        return self.engine.load_template(mold_id_template).render(**data)

    def __call__(self, mold_id, data={}, content_type='text/html'):
        """
        Generates a full response
        """

        content = self.engine.render(mold_id, data)
        headers = {
            'Content-type': content_type,
        }
        return Response(content, headers)


class BaseLoaderRenderer(object):
    """
    Provide an interface to an implementation of the BaseLoader class
    from the loader module in a generic manner, where a specified
    end-user/front-end friendly identifier is mapped to some internal
    identifier representing some underlying system resource to be
    provided by some registry.
    """

    def __init__(self, loader, mimetypes=MimeTypes()):
        self.loader = loader
        self.mimetypes = mimetypes

    def __call__(self, identifier):
        mimetype, encoding = self.mimetypes.guess_type(identifier)
        content = self.loader(identifier)
        headers = {
            'Content-type': mimetype,
        }
        return Response(content, headers)


MoldDataRenderer = partial(BaseLoaderRenderer, loader=BinLoader())
ArtifactRenderer = partial(BaseLoaderRenderer, loader=ArtifactLoader())


class MappedDataProvider(object):

    def __init__(self, mapping, renderer):
        """
        The mapping should be a simple filename mapping to a target
        mold_id_path resolvable to a valid target.
        """

        self.mapping = mapping
        self.renderer = renderer
        # TODO figure out how to cache the responses?
        # TODO perhaps provide a common base static type rendering that
        # may be inherited, see following class.

    def __call__(self, filename):
        """
        Return a response for that filename.
        """

        # XXX of course this is going to fail
        # XXX what to do/handle not found,
        # TODO figure out how to support standard codes such as 404
        return self.renderer(self.mapping[filename])


MoldDataProvider = partial(MappedDataProvider, renderer=MoldDataRenderer())
ArtifactProvider = partial(MappedDataProvider, renderer=ArtifactRenderer())
