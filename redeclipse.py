import sys
import gzip
import binascii # noqa
import struct
from enum import Enum
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

MAXENTATTRS = 100


class EntType(Enum):
    ET_EMPTY = 0
    ET_LIGHT = 1
    ET_MAPMODEL = 2
    ET_PLAYERSTART = 3
    ET_ENVMAP = 4
    ET_PARTICLES = 5
    ET_SOUND = 6
    ET_LIGHTFX = 7
    ET_SUNLIGHT = 8
    ET_WEAPON = 9
    ET_UNKNOWN_A = 10
    ET_UNKNOWN_B = 11
    ET_UNKNOWN_C = 12
    ET_UNKNOWN_D = 13
    ET_AFFINITY = 14


class Entity(object):

    def __init__(self, x, y, z, type):
        self.o = ivec(x, y, z)
        self.type = type
        self.attrs = []
        self.links = []

    def __str__(self):
        return '[Ent %s %s [Attr: %s] [Links: %s]]' % (
            self.o, self.type.name,
            ','.join(map(str, self.attrs)),
            ','.join(map(str, self.links))
        )

class Map(object):

    def __init__(self, magic, version, meta, map_vars):
        self.magic = magic
        self.version = version
        self.meta = meta
        self.map_vars = map_vars

class cube:
    def __init__(self):
        self.c = [None] * 8

class ivec:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def ivec5(cls, i, x, y, z, s):
        return ivec(
            x + ((i&1)>>0) * s,
            y + ((i&2)>>1) * s,
            z + ((i&4)>>2) * s
        )

    def __str__(self):
        return "(%f, %f, %f)" % (self.x, self.y, self.z)

class MapParser(object):

    def parseMap(self, base_path):
        self.base_path = base_path
        self.mpz = base_path + '.mpz'
        self.index = 0
        return self.read()

    def read_int(self):
        return self.read_ints(1)[0]

    def read_custom(self, pattern, width):
        data = struct.unpack(
            pattern,
            self.bytes[self.index:self.index + width]
        )
        self.index += width
        return data

    def read_ints(self, count):
        width = 4 * count
        data = struct.unpack(
            'i' * count,
            self.bytes[self.index:self.index + width]
        )
        self.index += width
        return data

    def read_float(self):
        data = struct.unpack(
            'f',
            self.bytes[self.index:self.index + 4]
        )
        self.index += 4
        return data[0]

    def read_ushort(self):
        data = struct.unpack(
            'H',
            self.bytes[self.index:self.index + 2]
        )
        self.index += 2
        return data[0]

    def read_str(self, strlen, null=True):
        if null:
            # Strings are null terminated
            strlen += 1
        fmt = '%ds' % strlen
        data = struct.unpack(fmt, self.bytes[self.index:self.index + strlen])
        self.index += strlen
        if null:
            return data[0][0:-1]
        return data[0]


    def loadvslots(self, numvslots):
        prev = [-1] * numvslots
        vslots = []
        while numvslots > 0:
            changed = self.read_int()
            if changed < 0:
                for i in range(-changed):
                    vslots.append(None)
                numvslots += changed
            else:
                prev[len(vslots)] = self.read_int()
                # TODO
                print 'UNIMPLEMENTED'
                sys.exit(42)
                pass

    R = (1, 2, 0) # row
    C = (2, 0, 1) # col
    D = (0, 1, 2) # depth

    def loadchildren(self, co, size):
        c = cube()
        for i in range(8):
            if not self.loadc(
                c.c[i],
                ivec.ivec5(i, co.x, co.y, co.z, size),
                size
            ):
                break
        return c

    def loadc(self, c, co, size):
        # haschildren = False
        octsav = self.read_ushort()
        print hex(octsav)

    def loadents(self, numents):
        sizeof_entbase = 16
        self.ents = []
        for i in range(int(numents)):
            (x, y, z, etype, a, b, c) = self.read_custom('fffcccc', sizeof_entbase)
            print (x, y, z, etype, a, b, c)
            e = Entity(x, y, z, EntType(ord(etype)))
            # This says reserved but we've seen values in it so...
            e.reserved = [ord(q) for q in (a, b, c)]
            numattr = self.read_int()
            attrs = []
            for j in range(numattr):
                attrs.append(self.read_int())
            e.attrs = attrs

            link_count = self.read_int()
            links = []
            print link_count
            for j in range(link_count):
                links.append(self.read_int())
            e.links = links
            self.ents.append(e)

    def read(self):
        with gzip.open(self.mpz, 'rb') as handle:
            self.bytes = handle.read()

        magic = self.read_str(4, null=False)
        if magic not in ('MAPZ', 'BFGZ'):
            raise Exception("Not a mapz file")

        version = self.read_int()
        headersize = self.read_int()  # noqa

        meta_keys = ('worldsize', 'numents', 'numpvs', 'lightmaps', 'blendmap',
                     'numvslots', 'gamever', 'revision') #'gameident', 'numvars')
        meta_data = self.read_ints(len(meta_keys))
        meta = {}
        for (k, v) in zip(meta_keys, meta_data):
            meta[k] = v

        # char[4], null=True
        meta['gameident'] = self.read_str(3)
        meta['numvars'] = self.read_int()
        import pprint; pprint.pprint(meta)

        map_vars = {}
        for i in range(meta['numvars']):
            # +1 for null term string
            var_name_len = self.read_int()
            var_name = self.read_str(var_name_len)
            # print self.index, var_name
            var_type = self.read_int()

            # String
            if var_type == 2:
                var_len = self.read_int()
                var_val = self.read_str(var_len)
            elif var_type == 1:
                var_val = self.read_float()
            elif var_type == 0:
                var_val = self.read_int()
            else:
                log.error("Don't know how to handle map prop type %s", var_type)
                sys.exit()

            map_vars[var_name] = var_val

        texmru = []
        nummru = self.read_ushort()
        for i in range(nummru):
            texmru.append(self.read_ushort())

        # TODO: enttity handling
        self.loadents(meta['numents'])

        # small and blank hjave zero ents
        self.loadvslots(meta['numvslots'])

        # arggghhh
        self.loadchildren(ivec(0,0,0), meta['worldsize']>>1)


        m = Map(magic, version, meta, map_vars)
        return m


mp = MapParser()
m = mp.parseMap(sys.argv[1])
