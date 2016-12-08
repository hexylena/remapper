from redeclipse.enums import Faces, TextNum, OctLayers
from redeclipse.vec import ivec2, ivec3, vec2, vec3
MAXENTATTRS = 100
VSLOT_SHPARAM = 0
DEFAULT_ALPHA_FRONT = 0.5
DEFAULT_ALPHA_BACK = 0.0
ALLOCNODES = 0


def dimension(orient):
    return orient >> 1


def dimcoord(orient):
    return orient & 1


def opposite(orient):
    return orient ^ 1


class VSlot:

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


class SlotShaderParam:

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


class Entity:

    def __init__(self, x, y, z, type):
        self.o = ivec3(x, y, z)
        self.type = type
        self.attrs = []
        self.links = []
        self.reserved = []

    def __str__(self):
        return '[Ent %s %s [Attr: %s] [Links: %s]]' % (
            self.o, self.type.name,
            ','.join(map(str, self.attrs)),
            ','.join(map(str, self.links))
        )

    def serialization_format(self):
        return 'fffcccc' + ('i' * len(self.attrs)) + ('i' * len(self.links))

    def serialize(self):
        return [self.o.x, self.o.y, self.o.z, str.encode(str(self.type.value))] + \
            [str.encode(str(x)) for x in self.reserved] + \
            self.attrs + self.links


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
        # points to 8 cube structures which are its children, or NULL. -Z first, then -Y, -X
        self.children = None
        # extended info for the cube
        self.ext = None # extended info
        # edges of the cube, each uchar is 2 4bit values denoting the range.
        self.edges = [128] * 12 # 12
        # 4 edges of each dimension together representing 2 perpendicular faces
        self.faces = [] # 3
        # one for each face. same order as orient.
        self.texture = [TextNum.DEFAULT_GEOM] * 6
        # empty-space material
        self.material = None
        # merged faces of the cube
        self.merged = 0
        # mask of which children have escaped merges
        self.escaped = 0
        # visibility info for faces
        self.visible = 0

    @classmethod
    def newcubes(cls, face, mat):
        c = [
            cube(), cube(),
            cube(), cube(),
            cube(), cube(),
            cube(), cube(),
        ]
        for i in range(8):
            c[i].setfaces(face)
            c[i].mat = mat
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

    @classmethod
    def validatec(cls, cube_arr, size, depth=0):

        for i in range(8):
            if cube_arr[i].children:
                if size <= 1:
                    cls.solidfaces(cube.children[i])
                    cls.discardchildren(cube.children[i], True)
                else:
                    cls.validatec(cube_arr[i].children, size >> 1, depth + 1)
            elif size > 0x1000:
                cls.subdividecube(cube_arr[i], True, False)
                cls.validatec(cube_arr[i].children, size>>1, depth + 1)
            else:
                for j in range(3):
                    f = cube_arr[i].faces[j].value
                    e0 = f & 0x0F0F0F0F
                    e1 = (f>>4) & 0x0F0F0F0F
                    if (e0 == e1 or ((e1+0x07070707)|(e1-e0))&0xF0F0F0F0):
                        cls.emptyfaces(cube_arr[i]);
                        break

    @classmethod
    def emptyfaces(cls, cube):
        cube.setfaces(Faces.F_EMPTY)
