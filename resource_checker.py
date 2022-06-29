import hashlib

CHUNK_SIZE = 4096


def md5_checksum(filename: str):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class Resource:
    __resource_name__: str

    def __init__(self, source_path: str | None = None):
        self.__source_path: str | None = source_path
        self.__checksum: str | None = md5_checksum(source_path) if source_path is not None else None

    @property
    def checksum(self):
        return self.__checksum

    @property
    def resource_name(self):
        return self.__resource_name__

    @property
    def source(self):
        return self.__source_path

    def is_similar(self):
        try:
            return md5_checksum(self.__source_path) == self.__checksum
        except: # noqa
            return False


class ResourceManager:
    def __init__(self):
        self.__resources = {}
        # TODO (Gorkovets): Auto-check flag and functionality.

    def insert(self, resource: Resource):
        self.__resources[resource.__resource_name__] = resource
        return True

    def remove(self, resource_name: str) -> bool:
        try:
            self.__resources.pop(resource_name)
            return True
        except KeyError:
            return False

    def get(self, resource_name: str | None = None):
        if resource_name is None:
            return self.__resources
        return self.__resources.get(resource_name, default=None)
