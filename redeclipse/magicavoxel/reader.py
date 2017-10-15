import struct
from pkg_resources import parse_version

from kaitaistruct import __version__ as ks_version, KaitaiStruct


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))


class Magicavoxel(KaitaiStruct):
    SIZE = 256

    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self.magic = self._io.ensure_fixed_contents(struct.pack('4b', 86, 79, 88, 32))
        self.section_type = self._io.read_u4le()
        self.main_chunkre = self._io.ensure_fixed_contents(struct.pack('4b', 77, 65, 73, 78))
        self.chunk_size = self._io.read_u4le()
        self.child_chunk_size = self._io.read_u4le()
        self.chunk_contents = [None] * (self.chunk_size)
        for i in range(self.chunk_size):
            self.chunk_contents[i] = self._io.read_u1()

        self.model_size = self._root.SizeChunk(self._io, self, self._root)
        self.model_voxels = self._root.XyziChunk(self._io, self, self._root)
        self.palette = self._root.PaletteChunk(self._io, self, self._root, size=self.SIZE)

    class XyziChunk(KaitaiStruct):

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.chunk_identifier = self._io.ensure_fixed_contents(struct.pack('4b', 88, 89, 90, 73))
            self.chunk_size = self._io.read_u4le()
            self.child_chunk_size = self._io.read_u4le()
            self.num_voxels = self._io.read_u4le()
            self.voxels = [None] * (self.num_voxels)
            for i in range(self.num_voxels):
                self.voxels[i] = self._root.Voxels(self._io, self, self._root)

    class Colour(KaitaiStruct):

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.r = self._io.read_u1()
            self.g = self._io.read_u1()
            self.b = self._io.read_u1()
            self.a = self._io.read_u1()

    class PaletteChunk(KaitaiStruct):

        def __init__(self, _io, _parent=None, _root=None, size=256):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.chunk_identifier = self._io.ensure_fixed_contents(struct.pack('4b', 82, 71, 66, 65))
            self.chunk_size = self._io.read_u4le()
            self.child_chunk_size = self._io.read_u4le()
            self.colours = [None] * (size)
            for i in range(size):
                self.colours[i] = self._root.Colour(self._io, self, self._root)

    class Voxels(KaitaiStruct):

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.x = self._io.read_u1()
            self.y = self._io.read_u1()
            self.z = self._io.read_u1()
            self.c = self._io.read_u1()

    class SizeChunk(KaitaiStruct):

        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.chunk_identifier = self._io.ensure_fixed_contents(struct.pack('4b', 83, 73, 90, 69))
            self.chunk_size = self._io.read_u4le()
            self.child_chunk_size = self._io.read_u4le()
            self.x = self._io.read_u4le()
            self.y = self._io.read_u4le()
            self.z = self._io.read_u4le()
