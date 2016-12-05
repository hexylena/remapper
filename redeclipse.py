import sys
import gzip
import binascii # noqa
import struct
from enums import EntType, Faces, VTYPE, OCT, OctLayers, TextNum
from vec import ivec2, ivec3, vec2, vec3, cross
import copy
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

MAXENTATTRS = 100
VSLOT_SHPARAM = 0
MAXSTRLEN = 512
DEFAULT_ALPHA_FRONT = 0.5
DEFAULT_ALPHA_BACK = 0.0

ALLOCNODES = 0


def dimension(orient):
    return orient >> 1


def dimcoord(orient):
    return orient & 1


def opposite(orient):
    return orient ^ 1


class VSlot(object):

    def __init__(self, a, b):
        self.a = a
        self.b = b


        self.slot = None
        self._next = None
        self.index = None
        self.changed = None
        self.params = {}
        self.linked = False
        self.scale = 1
        self.rotation = 0
        self.offset = ivec2(0, 0)
        self.scroll = vec2(0, 0)
        self.layer = 0
        self.palette = 0
        self.palindex = 0
        self.alphafront = DEFAULT_ALPHA_FRONT
        self.alphaback = DEFAULT_ALPHA_BACK
        self.colorscale = vec3(1, 1, 1)
        self.glowcolor = None
        self.coastscale = 1


class SurfaceInfo:
    def __init__(self, lmid0, lmid1, verts, numverts):
        self.lmid = [lmid0, lmid1]
        self.verts = verts
        self.numverts = numverts

    def totalverts(self):
        if self.numverts & OctLayers.LAYER_DUP.value:
            return (self.numverts & OctLayers.MAXFACEVERTS.value) * 2
        else:
            return (self.numverts & OctLayers.MAXFACEVERTS.value)

    def __str__(self):
        return 'Surf: lmid %d %d verts %d numverts %d' % (
            self.lmid[0], self.lmid[1], self.verts, self.numverts
        )


class vertinfo:
    def __init__(self, x, y, z, u, v, norm):
        self.x = x
        self.y = y
        self.z = z
        self.u = u
        self.v = v
        self.norm = norm

    def setxyz(self, t):
        self.x = t.x
        self.y = t.y
        self.z = t.z

    def setxyz2(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return 'Vertinfo (%d, %d, %d) (u=%d v=%d n=%d)' % (self.x, self.y, self.z, self.u, self.v, self.norm)


class SlotShaderParam(object):

    def __str__(self):
        return 'name %s, loc %s, val0 %f, val1 %f, val2 %f, val3 %f, palette %d, palindex %d' % (
            self.name, self.loc,
            self.val[0],
            self.val[1],
            self.val[2],
            self.val[3],
            self.palette,
            self.palindex
        )


class Entity(object):

    def __init__(self, x, y, z, type):
        self.o = ivec3(x, y, z)
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


class cubext:
    def __init__(self, old=None, maxverts=0):
        if old:
            self.va = old.va
            self.ents = old.ents
            self.tjoints = old.tjoints
        else:
            self.va = None
            self.ents = None
            self.tjoints = -1
        self.surfaceinfo = []
        self.maxverts = maxverts
        self.verts = []


class cubeedge:
    def __init__(self, next, offset, size, index, flags):
        self.next = next
        self.offset = offset
        self.size = size
        self.index = index
        self.flags = flags


class cube:
    def __init__(self):
        self.children = [None] * 8
        self.ext = None # extended info
        self.edges = [128] * 12 # 12
        self.faces = [] # 3
        self.texture = [TextNum.DEFAULT_GEOM] * 6
        self.merged = 0
        self.escaped = 0
        self.visible = 0

    @classmethod
    def newcubes(cls, face, mat):
        c = [cube()] * 8
        for x in c:
            x.children = None
            x.ext = None
            x.visible = 0
            x.merged = 0
            x.faces = [
                face, face, face
            ]
            x.texture = [TextNum.DEFAULT_GEOM] * 6
            x.mat = mat
        global ALLOCNODES
        ALLOCNODES += 1
        return c

    def setfaces(self, face):
        #octa.h L256
        self.faces = [
            face,
            face,
            face
        ]

    def newcubeext(self, maxverts, init):
        if self.ext and self.ext.maxverts >= maxverts:
            return self.ext
        newext = cubext(old=self.ext, maxverts=maxverts)
        if init:
            if self.ext:
                newext.surfaces = self.ext.surfaces
                newext.verts = self.ext.verts
            else:
                newext.surfaces = 0
        self.ext = newext
        return newext

    def genfaceverts(self, orient):
        if orient == 0:
            return [
                ivec3(
                    self.edges[0+2+1] &0xF,
                    self.edges[4+0+1] >>4,
                    self.edges[8+2+0] >>4
                ),
                ivec3(
                    self.edges[0+0+1] &0xF,
                    self.edges[4+0+0] >>4,
                    self.edges[8+2+0] &0xF
                ),
                ivec3(
                    self.edges[0+0+0] &0xF,
                    self.edges[4+0+0] &0xF,
                    self.edges[8+0+0] &0xF
                ),
                ivec3(
                    self.edges[0+2+0] &0xF,
                    self.edges[4+0+1] &0xF,
                    self.edges[8+0+0] >>4
                )
            ]
        elif orient == 1:
            return [
                ivec3(
                    self.edges[0+2+1] >>4,
                    self.edges[4+2+1] >>4,
                    self.edges[8+2+1] >>4
                ),
                ivec3(
                    self.edges[0+2+0] >>4,
                    self.edges[4+2+1] &0xF,
                    self.edges[8+0+1] >>4
                ),
                ivec3(
                    self.edges[0+0+0] >>4,
                    self.edges[4+2+0] &0xF,
                    self.edges[8+0+1] &0xF
                ),
                ivec3(
                    self.edges[0+0+1] >>4,
                    self.edges[4+2+0] >>4,
                    self.edges[8+2+1] &0xF
                ),
            ]
        elif orient == 2:
            return [
                ivec3(
                    self.edges[0+2+0] >>4,
                    self.edges[4+2+1] &0xF,
                    self.edges[8+0+1] >>4
                ),
                ivec3(
                    self.edges[0+2+0] &0xF,
                    self.edges[4+0+1] &0xF,
                    self.edges[8+0+0] >>4
                ),
                ivec3(
                    self.edges[0+0+0] &0xF,
                    self.edges[4+0+0] &0xF,
                    self.edges[8+0+0] &0xF
                ),
                ivec3(
                    self.edges[0+0+0] >>4,
                    self.edges[4+2+0] &0xF,
                    self.edges[8+0+1] &0xF
                )
            ]
        elif orient == 3:
            return [
                ivec3(
                    self.edges[0+0+1] &0xF,
                    self.edges[4+0+0] >>4,
                    self.edges[8+2+0] &0xF
                ),
                ivec3(
                    self.edges[0+2+1] &0xF,
                    self.edges[4+0+1] >>4,
                    self.edges[8+2+0] >>4
                ),
                ivec3(
                    self.edges[0+2+1] >>4,
                    self.edges[4+2+1] >>4,
                    self.edges[8+2+1] >>4
                ),
                ivec3(
                    self.edges[0+0+1] >>4,
                    self.edges[4+2+0] >>4,
                    self.edges[8+2+1] &0xF
                )
            ]
        elif orient == 4:
            return [
                ivec3(
                    self.edges[0+0+0] &0xF,
                    self.edges[4+0+0] &0xF,
                    self.edges[8+0+0] &0xF
                ),
                ivec3(
                    self.edges[0+0+1] &0xF,
                    self.edges[4+0+0] >>4,
                    self.edges[8+2+0] &0xF
                ),
                ivec3(
                    self.edges[0+0+1] >>4,
                    self.edges[4+2+0] >>4,
                    self.edges[8+2+1] &0xF
                ),
                ivec3(
                    self.edges[0+0+0] >>4,
                    self.edges[4+2+0] &0xF,
                    self.edges[8+0+1] &0xF
                )
            ]
        elif orient == 5:
            return [
                ivec3(
                    self.edges[0+2+0] &0xF,
                    self.edges[4+0+1] &0xF,
                    self.edges[8+0+0] >>4
                ),
                ivec3(
                    self.edges[0+2+0] >>4,
                    self.edges[4+2+1] &0xF,
                    self.edges[8+0+1] >>4
                ),
                ivec3(
                    self.edges[0+2+1] >>4,
                    self.edges[4+2+1] >>4,
                    self.edges[8+2+1] >>4
                ),
                ivec3(
                    self.edges[0+2+1] &0xF,
                    self.edges[4+0+1] >>4,
                    self.edges[8+2+0] >>4
                )
            ]
        return v

    @classmethod
    def validatec(cls, cube, size, depth=0):
        if depth > 0:
            return

        print((' ' * depth) + 'validatec,', size)

        for i in range(8):
            print((' ' * depth) + "c[%s]=%s" % (i, '(nil)' if not cube[i].children else id(cube[i]),))
            if cube[i].children:
                print((' ' * depth) + '\tkid')
                if size <= 1:
                    cls.solidfaces(cube[i])
                    cls.discardchildren(cube[i], True)
                else:
                    cls.validatec(cube[i].children, size >> 1, depth + 1)
            elif size > 0x1000:
                print((' ' * depth) + '\tlarge')
                cls.subdividecube(cube[i], True, False)
                cls.validatec(cube[i].children, size>>1, depth + 1)
            else:
                print((' ' * depth) + '\telse')
                for j in range(3):
                    f = cube[i].faces[j].value
                    e0 = f & 0x0F0F0F0F
                    e1 = (f>>4) & 0x0F0F0F0F
                    if (e0 == e1 or ((e1+0x07070707)|(e1-e0))&0xF0F0F0F0):
                        cls.emptyfaces(cube[i]);
                        break

    @classmethod
    def emptyfaces(cls, cube):
        cube.setfaces(Faces.F_EMPTY)


class MapParser(object):

    R = (1, 2, 0) # row
    C = (2, 0, 1) # col
    D = (0, 1, 2) # depth

    def parseMap(self, base_path):
        self.base_path = base_path
        self.mpz = base_path + '.mpz'
        self.index = 0
        return self.read()

    def read_int(self):
        return self.read_ints(1)[0]

    def read_char(self):
        return self.read_custom('B', 1)[0]

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
        print("Sizeof int 4")
        print("numvslots %s" % numvslots)
        while numvslots > 0:
            print("numvslots %s" % numvslots)
            changed = self.read_int()
            print("changed %s" % changed)
            if changed < 0:
                for i in range(-changed):
                    vslots.append(VSlot(None, len(vslots)))
                numvslots += changed
            else:
                prev.append(self.read_int())
                self.loadvslot(VSlot(None, len(vslots)), changed)
                numvslots -= 1


        print("Vslots: %s" % len(vslots))
        for idx, v in enumerate(vslots):
            print("\t[%s] %s %s" % (idx, prev[idx], int(0 <= idx < numvslots)))
            if 0 <= idx < numvslots:
                vslots[prev[idx]]._next = vslots[idx]

        self.vslots = vslots
        # print(list(enumerate(vslots)))
        # print(list(enumerate(prev)))

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
        print('lc %s %s' % (size, 1 if failed else 0))
        c = cube.newcubes(0, 0)
        for i in range(8):
            print("\t, %d %d %d" % (i, size, 1 if failed else 0))
            failed, c_x = self.loadc(
                c[i],
                ivec3.ivec5(i, co.x, co.y, co.z, size),
                size,
                failed
            )
            c[i] = c_x
            print('\tlc %s %s' % (i, 1 if failed else 0))

            if failed:
                break
        return c

    def loadc(self, c, co, size, failed):
        # haschildren = False
        octsav = self.read_char()
        haschildren = False
        print('octsav', octsav, '&7', octsav & 0x7)
        if octsav & 0x7 == OCT.OCTSAV_CHILDREN.value:
            c.children = self.loadchildren(co, size>>1, failed)
            for x in range(8):
                print('lc.c[%s]=%s' % (x, id(c.children[x])))
            return False, c
        elif octsav & 0x7 == OCT.OCTSAV_EMPTY.value:
            c.setfaces(Faces.F_EMPTY)
        elif octsav & 0x7 == OCT.OCTSAV_SOLID.value:
            c.setfaces(Faces.F_SOLID)
        elif octsav & 0x7 == OCT.OCTSAV_NORMAL.value:
            c.edges = self.read_custom('B', 12)
        elif octsav & 0x7 == OCT.OCTSAV_LODCUBE.value:
            haschildren = True
        else:
            failed = True
            return failed, c

        c.texture = [self.read_ushort() for i in range(6)]
        for idx, i in enumerate(c.texture):
            print('c.tex[%d] = %d' % (idx, i))

        print('octsav %d &40 %d &80 %d &20 %d' % (
            octsav, octsav & 0x40, octsav & 0x80, octsav & 0x20
        ))
        if octsav & 0x40:
            c.material = self.read_ushort()
        if octsav & 0x80:
            c.merged = self.read_char()
        if octsav & 0x20:
            surfmask = self.read_char()
            totalverts = self.read_char()
            print('sfm %d, tv %d' % (surfmask, totalverts))
            c.newcubeext(totalverts, False)
            c.ext.surfaces = []
            c.ext.verts = 0
            offset = 0
            for i in range(6):
                print('loadc 0x20 %d, %d' % (i, surfmask & (1 << i)))

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

                    # print(i, c.ext.surfaces)
                    surf = c.ext.surfaces[i]
                    vertmask = surf.verts
                    print(surf)
                    numverts = surf.totalverts()
                    print('Vertmask %d numverts %d' % (vertmask, numverts))
                    if not numverts:
                        surf.verts = 0
                        continue
                    surf.verts = offset
                    offset += numverts
                    verts = [
                        vertinfo(0,0,0,0,0,0)
                    ] * 20
                    v = []
                    n = None
                    vo = co.mask(0xFFF).shl(3)
                    layerverts = surf.numverts & OctLayers.MAXFACEVERTS.value
                    dim = dimension(i)
                    vc = self.C[dim]
                    vr = self.R[dim]
                    bias = 0
                    v = c.genfaceverts(i)
                    hasxyz = (vertmask & 0x04) != 0
                    hasuv = (vertmask &0x40) != 0
                    hasnorm = (vertmask & 0x80) != 0
                    if hasxyz:
                        e1 = copy.deepcopy(v[1])
                        e2 = copy.deepcopy(v[2])
                        e3 = copy.deepcopy(v[3])
                        n = cross(
                            e1.sub(v[0]),
                            e2.sub(v[0])
                        )
                        print(e1)
                        print(e2)
                        print(e3)
                        print(n)
                        if n.iszero():
                            n = cross(e2, e3.sub(v[0]))
                        bias = -n.dot(
                            v[0].mul(size).add(vo)
                        )
                        print("Bias: %d" % bias)
                    else:
                        vis = 3
                        if layerverts < 4:
                            if vertmask & 0x02:
                                vis = 2
                            else:
                                vis = 1
                        order = 0
                        if vertmask & 0x01:
                            order = 1
                        k = 0
                        verts[k].setxyz(v[order].mul(size).add(vo))
                        k += 1
                        if vis & 1:
                            verts[k].setxyz(v[order+1].mul(size).add(vo))
                            k += 1
                        verts[k].setxyz(v[order+2].mul(size).add(vo))
                        k += 1
                        if vis & 2:
                            verts[k].setxyz(v[(order+3)&3].mul(size).add(vo))
                            k += 1

                    # TODO
                    print('layerverts %d' % layerverts)
                    if layerverts == 4:
                        print('hasxyz %s hasuv %s' % (hasxyz, hasuv))
                        if hasxyz and (vertmask & 0x01):
                            c1 = self.read_ushort()
                            r1 = self.read_ushort()
                            c2 = self.read_ushort()
                            r2 = self.read_ushort()
                            print('c1 ... %d, %d, %d, %d' % (c1, r1, c2, r2))
                            xyz = [0] * 3
                            print('vc = %d, vr = %d, dim = %d' % (vc, vr, dim))

                            xyz[vc] = c1
                            xyz[vr] = r1
                            if n.gg(dim):
                                xyz[dim] =  -(bias + n.gg(vc)*xyz[vc] + n.gg(vr)*xyz[vr]) / n.gg(dim)
                            else:
                                xyz[dim] = vo[dim]

                            verts[0].setxyz2(*xyz)
                            print(verts[0])

                            xyz[vc] = c1
                            xyz[vr] = r2
                            if n.gg(dim):
                                xyz[dim] =  -(bias + n.gg(vc)*xyz[vc] + n.gg(vr)*xyz[vr]) / n.gg(dim)
                            else:
                                xyz[dim] = vo[dim]

                            verts[1].setxyz2(*xyz)
                            print(verts[1])

                            xyz[vc] = c2
                            xyz[vr] = r2
                            if n.gg(dim):
                                xyz[dim] =  -(bias + n.gg(vc)*xyz[vc] + n.gg(vr)*xyz[vr]) / n.gg(dim)
                            else:
                                xyz[dim] = vo[dim]

                            verts[2].setxyz2(*xyz)
                            print(verts[2])

                            xyz[vc] = c2
                            xyz[vr] = r1
                            if n.gg(dim):
                                xyz[dim] =  -(bias + n.gg(vc)*xyz[vc] + n.gg(vr)*xyz[vr]) / n.gg(dim)
                            else:
                                xyz[dim] = vo[dim]

                            verts[3].setxyz2(*xyz)
                            print(verts[3])
                            hasxyz = False
                        if hasuv and (vertmask & 0x02):
                            uvorder = (vertmask&0x30)>>4
                            v0 = verts[uvorder]
                            v1 = verts[(uvorder + 1) & 0x3]
                            v2 = verts[(uvorder + 2) & 0x3]
                            v3 = verts[(uvorder + 3) & 0x3]
                            v0.u = self.read_ushort()
                            v0.v = self.read_ushort()
                            v2.u = self.read_ushort()
                            v2.v = self.read_ushort()
                            v1.u = v0.u
                            v1.v = v2.v
                            v3.u = v2.u
                            v3.v = v0.v
                            if surf.numverts & OctLayers.LAYER_DUP.value:
                                v0 = verts[4 + uvorder]
                                v1 = verts[4 + ((uvorder + 1) & 0x3)]
                                v2 = verts[4 + ((uvorder + 2) & 0x3)]
                                v3 = verts[4 + ((uvorder + 3) & 0x3)]
                                v0.u = self.read_ushort()
                                v0.v = self.read_ushort()
                                v2.u = self.read_ushort()
                                v2.v = self.read_ushort()
                                v1.u = v0.u
                                v1.v = v2.v
                                v3.u = v2.u
                                v3.v = v0.v
                                hasuv = False
                    if hasnorm and (vertmask & 0x08):
                        norm = self.read_ushort()
                        for k in range(layerverts):
                            verts[k].norm = norm
                    if hasxyz or hasuv or hasnorm:
                        for k in range(layerverts):
                            v = verts[k]
                            if hasxyz:
                                xyz = [0] * 3
                                xyz[vc] = self.read_ushort()
                                xyz[vr] = self.read_ushort()
                                if n.gg(dim):
                                    xyz[dim] =  -(bias + n.gg(vc)*xyz[vc] + n.gg(vr)*xyz[vr]) / n.gg(dim)
                                else:
                                    xyz[dim] = vo[dim]
                            if hasuv:
                                v.u = self.read_ushort()
                                v.v = self.read_ushort()
                            if hasnorm:
                                v.norm = self.read_ushort()
                    if surf.numverts & OctLayers.LAYER_DUP.value:
                        for k in range(layerverts):
                            v = verts[k + layerverts]
                            t = verts[k]
                            v.setxyz(t)
                            if hasuv:
                                v.u = self.read_ushort()
                                v.v = self.read_ushort()
                            v.norm = t.norm
            # sys.exit()

        print('haskids %s' % (1 if failed else 0,))
        if haschildren:
            c.children = self.loadchildren(co, size>>1, failed)
        else:
            c.children = None

        return failed, c

    def loadents(self, numents):
        sizeof_entbase = 16
        self.ents = []
        for i in range(int(numents)):
            (x, y, z, etype, a, b, c) = self.read_custom('fffcccc', sizeof_entbase)
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


        print('Loading map:', self.mpz)
        print('Header Magic:', magic)
        print('Header Version:')

        version = self.read_int()
        headersize = self.read_int()  # noqa
        print('Header Size:', headersize)

        meta_keys = ('worldsize', 'numents', 'numpvs',
                     'lightmaps', 'blendmap', 'numvslots',
                     'gamever', 'revision')
        #'gameident', 'numvars')
        meta_data = self.read_ints(len(meta_keys))
        meta = {}
        for (k, v) in zip(meta_keys, meta_data):
            meta[k] = v

        # char[4], null=True
        meta['gameident'] = self.read_str(3)
        meta['numvars'] = self.read_int()

        print('Header Worldsize:', meta['worldsize'])
        print('Header Worldsize:', meta['worldsize'])


        map_vars = {}
        for i in range(meta['numvars']):
            # +1 for null term string
            var_name_len = self.read_int()
            var_name = self.read_str(var_name_len)
            # print(self.index, var_name)
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

        print('Clearing world..')

        texmru = []
        nummru = self.read_ushort()
        print('Nummru', nummru)
        for i in range(nummru):
            texmru.append(self.read_ushort())

        # Entities
        self.loadents(meta['numents'])
        print('Header.numents', meta['numents'])
        log.info("Loaded %s entities", len(self.ents))

        # Textures?
        self.loadvslots(meta['numvslots'])
        log.info("Loaded %s vslots", len(self.vslots))

        # arggghhh
        failed = False
        print("Loadchildren")
        worldroot = self.loadchildren(
            ivec3(0,0,0),
            meta['worldsize']>>1,
            failed
        )

        cube.validatec(worldroot, meta['worldsize'] >> 1)

        m = Map(magic, version, meta, map_vars)
        return m


mp = MapParser()
m = mp.parseMap(sys.argv[1])
