from calmjs.registry import get
from nunja.registry import MoldRegistry


class BaseLoader(object):
    """
    Simply load a resource inside a mold.
    """

    def __init__(self, registry_name='nunja.mold'):
        self.registry = get(registry_name)
        if not isinstance(self.registry, MoldRegistry):
            raise ValueError(
                "'%s' does not resolve to a nunja.registry:MoldRegistry, "
                "got %r instead" % (registry_name, self.registry)
            )

    def __call__(self, mold_id_path):
        return self.registry.lookup_path(mold_id_path)


class BinLoader(BaseLoader):
    """
    Return a binary object instead
    """

    def __call__(self, mold_id_path):
        path = self.registry.lookup_path(mold_id_path)
        with open(path, 'rb') as stream:
            return stream.read()
