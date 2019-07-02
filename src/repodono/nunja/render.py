from mimetypes import MimeTypes
from nunja.core import engine
from repodono.model.http import Response
from repodono.nunja.loader import BinLoader


class NunjaRenderer(object):

    def __init__(self, engine=engine):
        self.engine = engine

    def __call__(self, mold_id, data, content_type='text/html'):
        content = self.engine.render(mold_id, data)
        headers = {
            'Content-type': content_type,
        }
        return Response(content, headers)


class MoldDataRenderer(object):

    def __init__(self, loader=BinLoader(), mimetypes=MimeTypes()):
        self.loader = loader
        self.mimetypes = mimetypes

    def __call__(self, mold_id_path):
        # content_type = 'application/octet-stream'
        mimetype, encoding = self.mimetypes.guess_type(mold_id_path)
        content = self.loader(mold_id_path)
        headers = {
            'Content-type': mimetype,
        }
        return Response(content, headers)


class StaticProvider(object):

    def __init__(self, mapping, renderer=MoldDataRenderer()):
        """
        The mapping should be a simple filename mapping to a target
        mold_id_path resolvable to a valid target.
        """

        self.mapping = mapping
        self.renderer = renderer
        # TODO figure out how to cache the responses?

    def __call__(self, filename):
        """
        Return a response for that filename.
        """

        # XXX of course this is going to fail
        # XXX what to do/handle not found,
        # TODO figure out how to support standard codes such as 404
        return self.renderer(self.mapping[filename])
