from functools import partial
from mimetypes import MimeTypes
from nunja.core import engine
from repodono.model.http import Response
from repodono.nunja.loader import BinLoader
from repodono.nunja.loader import ArtifactLoader


class NunjaRenderer(object):

    def __init__(self, engine=engine):
        self.engine = engine

    def __call__(self, mold_id, data={}, content_type='text/html'):
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
