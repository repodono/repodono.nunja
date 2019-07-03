from calmjs.registry import get
from calmjs.base import BaseRegistry
from calmjs.artifact import ArtifactRegistry
from nunja.registry import MoldRegistry


def get_registry(registry_name, registry_cls):
    registry = get(registry_name)
    if not isinstance(registry, registry_cls):
        raise ValueError("'%s' does not resolve to a %s:%s, got %r instead" % (
            registry_name,
            registry_cls.__module__,
            registry_cls.__name__,
            registry,
        ))
    return registry


class BaseLoader(object):
    """
    The base implementation for loader that extracts data from some
    registry.
    """

    def __init__(self, registry_name):
        self.registry = get_registry(registry_name, BaseRegistry)

    def resolve(self, identifier):
        """
        Convert the identifier into target arguments.

        Default implementation returns a 1-tuple with the identifier
        intract.
        """

        return identifier,

    def invoke(self, *a):
        raise NotImplementedError

    def __call__(self, identifier):
        return self.invoke(*self.resolve(identifier))


class MoldPathLoader(BaseLoader):
    """
    Simply returns the path on the filesystem.
    """

    def __init__(self, registry_name='nunja.mold'):
        self.registry = get_registry(registry_name, MoldRegistry)

    def invoke(self, mold_id_path):
        return self.registry.lookup_path(mold_id_path)


class BinLoader(MoldPathLoader):
    """
    Return a target as a binary object.
    """

    def invoke(self, mold_id_path):
        path = self.registry.lookup_path(mold_id_path)
        with open(path, 'rb') as stream:
            return stream.read()


class ArtifactLoader(BaseLoader):
    """
    Return an artifact from a package by name.
    """

    def __init__(self, registry_name='calmjs.artifacts'):
        self.registry = get_registry(registry_name, ArtifactRegistry)

    def resolve(self, identifier):
        """
        Convert the identifier in the form of `{module_name}:{filename}`
        into a 2-tuple (split by the first `:`).
        """

        result = identifier.split(':', 1)
        if len(result) != 2:
            raise ValueError(
                "'%s' is an invalid reference to a package artifact; it must "
                "be in the form of '{package_name}:{artifact_name}'" % (
                    identifier))
        return result

    def invoke(self, package_name, artifact_name):
        path = self.registry.get_artifact_filename(package_name, artifact_name)
        with open(path, 'rb') as stream:
            return stream.read()
