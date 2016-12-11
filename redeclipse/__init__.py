import sys
import gzip
import struct
from collections import OrderedDict
from redeclipse.enums import EntType, Faces, VTYPE, OCT, TextNum
from redeclipse.objects import VSlot, SlotShaderParam, cube, SurfaceInfo
from redeclipse.entities import Entity
from redeclipse.vec import ivec3
import simplejson as json
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

MAXSTRLEN = 512

def tb(str_or_bytes):
    if isinstance(str_or_bytes, str):
        return str.encode(str_or_bytes)
    else:
        return str_or_bytes


class Map:

    def __init__(self, magic, version, headersize, meta, map_vars, texmru, ents, vslots, chg, worldroot):
        self.magic = magic
        self.version = version
        self.headersize = headersize
        self.meta = meta
        self.map_vars = map_vars
        self.texmru = texmru
        self.ents = ents
        self.vslots = vslots
        self.chg = chg
        self.world = worldroot

    def write(self, path):
        log.info('WRITING')
        handle = gzip.open(path, 'wb')
        handle.write(self.magic)
        # Write the version
        self.write_int(handle, self.version)
        # Write the header size (Surely some way to calc from self.meta?)
        self.write_int(handle, self.headersize)
        # Write the header block
        self.meta['numents'] = len(self.ents)
        for key in self.meta:
            if key == 'gameident':
                self.write_str(handle, tb(self.meta[key]))
            else:
                self.write_int(handle, self.meta[key])

        # Write the map vars
        for key in self.map_vars:
            var_name = key
            value = self.map_vars[key]
            var_type = type(self.map_vars[key]).__name__

            self.write_int(handle, len(var_name))
            self.write_str(handle, var_name)

            if var_type == 'int':
                self.write_int(handle, 0)
                self.write_int(handle, value)
            elif var_type == 'float':
                self.write_int(handle, 1)
                self.write_float(handle, value)
            elif var_type in ('bytes', 'str'):
                self.write_int(handle, 2)
                self.write_int(handle, len(value))
                self.write_str(handle, value)
            else:
                raise Exception("Can't handle " + var_type)

        # Texmru
        self.write_ushort(handle, len(self.texmru))  # nummru
        # log.debug("texmru: %s", len(self.texmru))
        for value in self.texmru:
            self.write_ushort(handle, value)

        # Entities
        self.write_ents(handle, self.ents)

        # Textures
        self.write_vslots(handle, self.vslots, self.chg)

        # World
        self.write_world(handle, self.world)

    def write_custom(self, handle, fmt, data):
        log.debug('wcc %s %s', fmt, data)
        handle.write(struct.pack(fmt, *data))

    def write_char(self, handle, char):
        log.debug('wchr %s', char)
        handle.write(struct.pack('B', char))

    def write_int_as_chr(self, handle, data):
        log.debug('wichr %s', data)
        handle.write(struct.pack('c', str.encode(chr(data))))

    def write_int(self, handle, value):
        if isinstance(value, int):
            log.debug('wi %s', value)
            handle.write(struct.pack('i', value))
        else:
            log.debug('wi %s', value.value)
            handle.write(struct.pack('i', value.value))

    def write_ushort(self, handle, value):
        log.debug('wu %s', value)
        handle.write(struct.pack('H', value))

    def write_float(self, handle, value):
        log.debug('wf %s', value)
        handle.write(struct.pack('f', value))

    def write_str(self, handle, value, null=True):
        log.debug('ws %s', value)
        strlen = len(value)
        if null:
            strlen += 1

        fmt = '%ds' % strlen
        handle.write(struct.pack(fmt, value))

    def write_ents(self, handle, ents):
        for ent in ents:
            # (x, y, z, etype, a, b, c) = self.read_custom('fffcccc', sizeof_entbase)
            self.write_custom(
                handle,
                'fffcccc',
                ent.serialize()
            )

            self.write_int(handle, len(ent.attrs))
            for at in ent.attrs:
                self.write_int(handle, at)

            self.write_int(handle, len(ent.links))
            for ln in ent.links:
                self.write_int(handle, ln)

    def write_vslots(self, handle, vslots, chg):
        for num in chg:
            self.write_int(handle, num)
            if num < 0:
                pass
            else:
                raise NotImplementedError()

    def write_vslot(self, vs, changed):
        pass

    def write_world(self, handle, world):
        # world is cube_arr len=8
        for c in world:
            self.write_cube(handle, c)

    def write_children(self, handle, cube_arr):
        for c in cube_arr:
            self.write_cube(handle, c)

    def write_cube(self, handle, c):
        """Inverse of loadc"""

        self.write_int_as_chr(handle, c.octsav)
        # log.debug('> octsav %s &7 %s', c.octsav, c.octsav & 0x7)

        if c.octsav & 0x7 == OCT.OCTSAV_CHILDREN.value:
            # log.debug('>> kids')
            self.write_children(handle, c.children)
        elif c.octsav & 0x7 == OCT.OCTSAV_EMPTY.value:
            # log.debug('>> empty')
            pass # Nothing to write
        elif c.octsav & 0x7 == OCT.OCTSAV_SOLID.value:
            # log.debug('>> solid')
            pass # Nothing to write, simply that c is solid
        elif c.octsav & 0x7 == OCT.OCTSAV_NORMAL.value:
            # log.debug('>> normal')
            for e in c.edges:
                self.write_custom(handle, 'B', [e])
        elif c.octsav & 0x7 == OCT.OCTSAV_LODCUBE.value:
            # log.debug('>> lodcube')
            # Nothing to do, this just set c.children, which we know
            # from other sources.
            pass
        else:
            sys.exit(42)
            return

        for t in c.texture:
            if isinstance(t, TextNum):
                self.write_ushort(handle, t.value)
            else:
                self.write_ushort(handle, t)

        if c.octsav & 0x40:
            self.write_ushort(handle, c.material)
        if c.octsav & 0x80:
            self.write_int_as_chr(handle, c.merged)
        if c.octsav & 0x20:
            self.write_int_as_chr(handle, c.surfmask)
            self.write_int_as_chr(handle, c.totalverts)
            for i in range(6):
                # log.debug(('>loadc 0x20 %d, %d' % (i, c.surfmask & (1 << i))))

                if not c.surfmask & (1<<i):
                    pass
                else:
                    surfinfo = c.ext.surfaces[i]
                    self.write_char(handle, surfinfo.lmid[0])
                    self.write_char(handle, surfinfo.lmid[1])
                    self.write_char(handle, surfinfo.verts)
                    self.write_char(handle, surfinfo.numverts)

                    if surfinfo.verts == 0:
                        continue
                    else:
                        raise NotImplementedError("Gross out")

    def to_dict(self):
        return {
            'magic': bytes.decode(self.magic),
            'version': self.version,
            'headersize': self.headersize,
            'meta': [(key, bytes.decode(value) if isinstance(value, bytes) else value) for (key, value) in self.meta.items()],
            'map_vars': [(bytes.decode(key), bytes.decode(value) if isinstance(value, bytes) else value) for (key, value) in self.map_vars.items()],
            'texmru': self.texmru,
            'entities': [ent.to_dict() for ent in self.ents],
            'world': (x.to_dict() for x in self.world),
            'vslots': (x.to_dict() for x in self.vslots),
            'chg': self.chg,
        }

    def to_json(self):
        return json.dumps(self.to_dict(), iterable_as_array=True)
    @classmethod
    def from_dict(cls, data):
        # TODO
        meta = OrderedDict()
        for (key, value) in data['meta']:
            meta[key] = value

        map_vars = OrderedDict()
        for (key, value) in data['map_vars']:
            if isinstance(value, str):
                map_vars[str.encode(key)] = str.encode(value)
            else:
                map_vars[str.encode(key)] = value

        # TODO
        world = {}

        m = Map(
            magic=str.encode(data['magic']),
            version=data['version'],
            headersize=data['headersize'],
            meta=meta,
            map_vars=map_vars,
            texmru=data['texmru'],
            ents=[Entity.from_dict(x) for x in data['entities']],
            vslots=[VSlot.from_dict(x) for x in data['vslots']],
            chg=data['chg'],
            worldroot=world,
        )

        return m


class MapParser(object):

    def parseMap(self, base_path):
        """Load the specified map"""
        self.base_path = base_path
        self.mpz = base_path
        self.index = 0
        return self.read()

    def _read_custom(self, pattern, width):
        val = struct.unpack(pattern, self.bytes[self.index:self.index + width])
        self.index += width
        return val

    def read_int(self):
        val = self._read_custom('i', 4)[0]
        log.debug('wi %s', val)
        return val

    def read_char(self):
        val = self._read_custom('B', 1)[0]
        log.debug('wc %s', val)
        return val

    def read_custom(self, pattern, width):
        val = self._read_custom(pattern, width)
        log.debug('wcc %s %s', pattern, val)
        return val

    def read_float(self):
        val = self._read_custom('f', 4)[0]
        log.debug('wf %s', val)
        return val

    def read_ushort(self):
        val = self._read_custom('H', 2)[0]
        log.debug('wu %s', val)
        return val

    def read_str(self, strlen, null=True):
        if null:
            # Strings are null terminated
            strlen += 1
        fmt = '%ds' % strlen
        data = struct.unpack(fmt, self.bytes[self.index:self.index + strlen])
        self.index += strlen
        if null:
            log.debug('ws %s', data[0][0:-1])
            return data[0][0:-1]
        log.debug('ws %s', data[0])
        return data[0]

    def loadvslots(self, numvslots):
        prev = [-1] * numvslots
        vslots = []
        chg = []
        log.debug("Sizeof int 4")
        log.debug("numvslots %s", numvslots)
        while numvslots > 0:
            log.debug("numvslots %s", numvslots)
            changed = self.read_int()
            chg.append(changed)
            log.debug("changed %s", changed)
            if changed < 0:
                for i in range(-changed):
                    vslots.append(VSlot(None, len(vslots)))
                numvslots += changed
            else:
                prev.append(self.read_int())
                self.loadvslot(VSlot(None, len(vslots)), changed)
                numvslots -= 1


        log.debug("Vslots: %s", len(vslots))
        for idx, v in enumerate(vslots):
            log.debug("\t[%s] %s %s", idx, prev[idx], int(0 <= idx < numvslots))
            if 0 <= idx < numvslots:
                vslots[prev[idx]]._next = vslots[idx]

        return vslots, chg

    def loadvslot(self, vs, changed):
        vs.changed = changed
        if vs.changed & (1<<VTYPE.VSLOT_SHPARAM.value):
            flags = self.read_ushort()
            numparams = flags & 0x7FFF
            for i in range(numparams):
                ssp = SlotShaderParam()
                nlen = self.read_ushort()
                if nlen >= MAXSTRLEN:
                    log.error("Cannot handle")
                    sys.exit()

                name = self.read_str(nlen, null=False)
                ssp.name = name
                ssp.loc = -1
                ssp.val = [
                    self.read_float(),
                    self.read_float(),
                    self.read_float(),
                    self.read_float(),
                ]
                if flags & 0x8000:
                    ssp.palette = self.read_int()
                    ssp.palindex = self.read_int()
                else:
                    ssp.palette = 0
                    ssp.palindex = 0
        if vs.changed & (1<<VTYPE.VSLOT_SCALE.value):
            vs.scale = self.read_float()
        if vs.changed & (1<<VTYPE.VSLOT_ROTATION.value):
            vs.rotation = self.read_int()
        if vs.changed & (1<<VTYPE.VSLOT_OFFSET.value):
            vs.offset_x = self.read_int()
            vs.offset_y = self.read_int()
        if vs.changed & (1<<VTYPE.VSLOT_SCROLL.value):
            vs.scroll_x = self.read_int()
            vs.scroll_y = self.read_int()
        if vs.changed & (1<<VTYPE.VSLOT_LAYER.value):
            vs.layer = self.read_int()
        if vs.changed & (1<<VTYPE.VSLOT_ALPHA.value):
            vs.alphafront = self.read_float()
            vs.alphaback = self.read_float()

        if vs.changed & (1<<VTYPE.VSLOT_COLOR.value):
            vs.colorscale = [
                self.read_float(),
                self.read_float(),
                self.read_float()
            ]
        if vs.changed & (1<<VTYPE.VSLOT_PALETTE.value):
            vs.palette = self.read_int()
            vs.palindex = self.read_int()
        if vs.changed & (1<<VTYPE.VSLOT_COAST.value):
            vs.coastscale = self.read_float()

    def loadchildren(self, co, size, failed):
        log.debug('lc %s %s', size, 1 if failed else 0)
        cube_arr = cube.newcubes(Faces.F_EMPTY, 0)
        for i in range(8):
            log.debug("\t, %d %d %d", i, size, 1 if failed else 0)
            failed, c_x = self.loadc(
                cube_arr[i],
                ivec3.ivec5(i, co.x, co.y, co.z, size),
                size,
                failed
            )
            cube_arr[i] = c_x
            log.debug('\tlc %s %s', i, 1 if failed else 0)

            if failed:
                break
        return cube_arr

    def loadc(self, c, co, size, failed):
        """Loads a single cube? Or rather, based on C, processes it into a cube object?"""
        octsav = self.read_char()
        c.octsav = octsav
        log.debug('< octsav %s &7 %s', octsav, octsav & 0x7)
        c.haschildren = False
        if octsav & 0x7 == OCT.OCTSAV_CHILDREN.value:
            c.children = self.loadchildren(co, size>>1, failed)
            return False, c
        elif octsav & 0x7 == OCT.OCTSAV_EMPTY.value:
            c.setfaces(Faces.F_EMPTY)
        elif octsav & 0x7 == OCT.OCTSAV_SOLID.value:
            c.setfaces(Faces.F_SOLID)
        elif octsav & 0x7 == OCT.OCTSAV_NORMAL.value:
            c.edges = self.read_custom('BBBBBBBBBBBB', 12)
        elif octsav & 0x7 == OCT.OCTSAV_LODCUBE.value:
            c.haschildren = True
        else:
            failed = True
            return failed, c

        c.texture = [self.read_ushort() for i in range(6)]
        for idx, i in enumerate(c.texture):
            log.debug('c.tex[%d] = %d', idx, i)

        log.debug('octsav %d &40 %d &80 %d &20 %d',
            octsav, octsav & 0x40, octsav & 0x80, octsav & 0x20
        )

        if octsav & 0x40:
            c.material = self.read_ushort()
        if octsav & 0x80:
            c.merged = self.read_char()
        if octsav & 0x20:
            surfmask = self.read_char()
            c.surfmask = surfmask
            totalverts = self.read_char()
            c.totalverts = totalverts
            log.debug('sfm %d, tv %d', surfmask, totalverts)
            c.newcubeext(totalverts, False)
            # offset = 0
            for i in range(6):
                log.debug('<loadc 0x20 %d, %d', i, surfmask & (1 << i))

                if not surfmask & (1<<i):
                    c.ext.surfaces.append(None)
                else:
                    c.ext.surfaces.append(
                        SurfaceInfo(
                            self.read_char(),
                            self.read_char(),
                            self.read_char(),
                            self.read_char()
                        )
                    )

                    # log.debug(i, c.ext.surfaces)
                    surf = c.ext.surfaces[i]
                    vertmask = surf.verts
                    log.debug(surf)
                    numverts = surf.totalverts()
                    log.debug('Vertmask %d numverts %d', vertmask, numverts)
                    if not numverts:
                        surf.verts = 0
                        continue

                    raise NotImplementedError("Gross in")

        log.debug('haskids %s', 1 if failed else 0,)
        if c.haschildren:
            c.children = self.loadchildren(co, size>>1, failed)
        else:
            c.children = None

        return failed, c

    def loadents(self, numents):
        sizeof_entbase = 16
        ents = []
        for i in range(int(numents)):
            log.debug('sizeof(entbase) =', sizeof_entbase)
            (x, y, z, etype, a, b, c) = self.read_custom('fffcccc', sizeof_entbase)
            log.debug('e.o = (%0.6f %0.6f %0.6f); e.type = %s', x, y, z, ord(etype))

            # This says reserved but we've seen values in it so...
            reserved = [
                ord(a),
                ord(b),
                ord(c)
            ]

            numattr = self.read_int()
            attrs = []
            for j in range(numattr):
                attrs.append(self.read_int())

            link_count = self.read_int()
            links = []
            for j in range(link_count):
                links.append(self.read_int())

            e = Entity(x, y, z, EntType(ord(etype)), attrs, links, reserved)
            ents.append(e)
        return ents

    def read(self):
        with gzip.open(self.mpz) as handle:
            self.bytes = handle.read()

        magic = self.read_str(4, null=False)
        if magic not in (b'MAPZ', b'BFGZ'):
            raise Exception("Not a mapz file")


        log.debug('Loading map: %s', self.mpz)
        log.debug('Header Magic: %s', magic)
        version = self.read_int()
        log.debug('Version: %s', version)
        headersize = self.read_int()
        log.debug('Header Size: %s', headersize)

        meta_keys = ('worldsize', 'numents', 'numpvs',
                     'lightmaps', 'blendmap', 'numvslots',
                     'gamever', 'revision')
        #'gameident', 'numvars')
        meta = OrderedDict()
        for k in meta_keys:
            meta[k] = self.read_int()

        # char[4], null=True
        log.debug(meta)
        meta['gameident'] = self.read_str(3)
        meta['numvars'] = self.read_int()
        log.debug(meta)

        log.debug('Header Worldsize: %s', meta['worldsize'])


        map_vars = OrderedDict()
        for i in range(meta['numvars']):
            # +1 for null term string
            var_name_len = self.read_int()
            var_name = self.read_str(var_name_len)
            # log.debug(self.index, var_name)
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
                # Cannot recover
                raise Exception("Don't know how to handle map prop type %s", var_type)

            map_vars[var_name] = var_val

        log.debug('Clearing world..')

        texmru = []
        nummru = self.read_ushort()
        log.debug('Nummru %s', nummru)
        for i in range(nummru):
            texmru.append(self.read_ushort())

        # Entities
        log.debug('Header.numents %s', meta['numents'])
        ents = self.loadents(meta['numents'])
        log.debug("Loaded %s entities", len(ents))

        # Textures?
        vslots, chg = self.loadvslots(meta['numvslots'])
        log.debug("Loaded %s vslots", len(vslots))

        # arggghhh
        worldroot = []
        failed = False
        log.debug("Loadchildren")
        worldroot = self.loadchildren(
            ivec3(0,0,0),
            meta['worldsize']>>1,
            failed
        )

        cube.validatec(worldroot, meta['worldsize'] >> 1)

        worldscale = 0
        while 1<<worldscale < meta['worldsize']:
            worldscale += 1
        log.debug("Worldscale %s" % worldscale)

        log.debug("failed: %s" % (1 if failed else 0))
        if not failed:
            # Not sure this even works, but no need to implement since
            # we're fine to dump unlit maps.
            log.debug('Lightmaps: %s' % meta['lightmaps'])
            # TODO

        m = Map(magic, version, headersize, meta, map_vars, texmru, ents, vslots, chg,
                worldroot)
        return m
