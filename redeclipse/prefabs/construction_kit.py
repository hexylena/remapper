import random

from bresenham import bresenham

from redeclipse.objects import cube
from redeclipse.vector import FineVector
from redeclipse.vector.orientations import TILE_VOX_OFF, NORTH, SOUTH, EAST, WEST, ABOVE, BELOW
ROOM_SIZE = 8


def line_points(start, end):
    """
    TODO: this is broken af currently.
    """
    print("Line from ", start, 'to', end)
    if start.x == end.x:
        return []

    xy = list(bresenham(start.x, start.y, end.x, end.y))
    xz = list(bresenham(start.x, start.z, end.x, end.z))
    print(xy)
    print(xz)
    # There are gonna be uuuugly cases aren't there :(

    kv = {}
    for x in range(start.x, end.x + 1):
        kv[x] = {
            'y': [],
            'z': [],
        }
    print(kv)

    for pxz in xz:
        kv[pxz[0]]['z'].append(pxz[1])

    for pxy in xy:
        kv[pxy[0]]['y'].append(pxy[1])

    # resolve
    for pt in kv.keys():
        ys = kv[pt]['y']
        zs = kv[pt]['z']

        if len(ys) == len(zs):
            for (y, z) in zip(ys, zs):
                yield FineVector(pt, y, z)
        elif len(ys) % len(zs) == 0:
            # eg. 9ys and 3zs
            it_size = len(ys) // len(zs)
            for i in range(len(zs)):
                for j in range(it_size):
                    yield FineVector(pt, ys[i + j], zs[i])
        elif len(zs) % len(ys) == 0:
            it_size = len(zs) // len(ys)
            for i in range(len(ys)):
                for j in range(it_size):
                    yield FineVector(pt, ys[i], zs[i + j])
        else:
            # worst case.
            for i in range(len(ys)):
                for j in range(len(zs)):
                    yield FineVector(pt, ys[i], zs[j])


def column_points(size, direction):
    """
    Yield points needed to draw a column

    :param int size: Length of column
    :param str direction: direction the column should go in. One of (±x/y/z)

    :returns: An iterable of FineVectors
    :rtype: list(redeclipse.vector.FineVector)
    """
    # Convert direction to fine.
    direction = direction.fine() / 8
    for i in range(size):
        yield direction * i


def wall_points(size, direction, limit_j=100, limit_i=100):
    """
    Yield points needed to draw a wall. The semantics of direction are a
    bit odd.

    :param int size: size of the (square) wall
    :param str direction: Face the wall is on, e.g. -z is floor, +z is ceiling (size - 1)
    :param int limit_i: A clamp applied to the x component
    :param int limit_j: A clamp applied to the y component

    :returns: An iterable of FineVectors
    :rtype: list(redeclipse.vector.FineVector)
    """
    if size > 0:
        i_lower_bound = 0
        i_upper_bound = size
        j_lower_bound = 0
        j_upper_bound = size
    else:
        i_lower_bound = size
        i_upper_bound = 0
        j_lower_bound = size
        j_upper_bound = 0

    for i in range(i_lower_bound, i_upper_bound):
        # Allow partial_j walls
        if i > limit_i:
            continue

        for j in range(j_lower_bound, j_upper_bound):
            # Allow partial_j walls
            if j > limit_j:
                continue

            if direction == BELOW:
                yield FineVector(i, j, 0)
            elif direction == ABOVE:
                yield FineVector(i, j, size - 1)
            elif direction == SOUTH:
                yield FineVector(i, 0, j)
            elif direction == NORTH:
                yield FineVector(i, size - 1, j)
            elif direction == WEST:
                yield FineVector(0, i, j)
            elif direction == EAST:
                yield FineVector(size - 1, i, j)


def cube_points(x, y, z):
    """
    Yield points needed to draw a rectangular prism or cube.

    :param int x: size of the rectangular_prism in the x direction
    :param int y: size of the rectangular_prism in the y direction
    :param int z: size of the rectangular_prism in the z direction

    If, e.g., x is less than zero, it will go from (-x to 0) rather than
    (0, x)

    :returns: An iterable of FineVectors
    :rtype: list(redeclipse.vector.FineVector)
    """
    if x > 0:
        x_lower_bound = 0
        x_upper_bound = x
    else:
        x_lower_bound = x + 1
        x_upper_bound = 1

    if y > 0:
        y_lower_bound = 0
        y_upper_bound = y
    else:
        y_lower_bound = y + 1
        y_upper_bound = 1

    if z > 0:
        z_lower_bound = 0
        z_upper_bound = z
    else:
        z_lower_bound = z + 1
        z_upper_bound = 1

    for i in range(x_lower_bound, x_upper_bound):
        for j in range(y_lower_bound, y_upper_bound):
            for k in range(z_lower_bound, z_upper_bound):
                yield FineVector(i, j, k)


def subtract_or_skip(subtract, prob):
    """
    determine if we should subtract or skip based on the parameters.

    :param boolean subtract: Should subtract the point
    :param float prob: If ``random.random()`` > prob, will return that we
                       should "skip" the point.

    :returns: should we subtract (true) or skip the point (false)
    :rtype: boolean
    """
    if subtract:
        return True
    else:
        if prob < 1:
            if random.random() > prob:
                return True
    return False


class ConstructionKitMixin(object):
    """
    A mixin for constructing things in the VoxelWorld. The code is still
    a bit messy...
    """

    def x(self, construction, world, *args, **kwargs):
        funcname = 'x_' + construction
        if not hasattr(self, funcname):
            raise Exception("Unknown function")
        func = getattr(self, funcname)
        tex = 2
        subtract = kwargs.get('subtract', False)
        prob = kwargs.get('prob', 1.1)
        if 'tex' in kwargs:
            tex = kwargs['tex']
            del kwargs['tex']

        if 'subtract' in kwargs:
            del kwargs['subtract']

        if 'prob' in kwargs:
            del kwargs['prob']

        for point in func(*args, **kwargs):
            if subtract_or_skip(subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def x_cube(self, offset):
        yield self.pos + offset.offset_rotate(self.orientation, offset=TILE_VOX_OFF)

    def x_column(self, offset, direction, length):
        local_position = self.pos + offset.offset_rotate(self.orientation, offset=TILE_VOX_OFF)
        for point in column_points(length, direction.rotate(self.orientation)):
            yield point + local_position

    def x_interpolate(self, offset, start, end):
        start = start.rotate(self.orientation).vox()
        end = end.rotate(self.orientation).vox()
        local_position = self.pos + offset.offset_rotate(self.orientation, offset=TILE_VOX_OFF)

        for point in line_points(start, end):
            yield point + local_position

    def x_dotted_column(self, offset, direction, length, on=2, off=2):
        local_position = self.pos + offset.offset_rotate(self.orientation, offset=TILE_VOX_OFF)
        onoff = [True] * on + [False] * off
        for idx, point in enumerate(column_points(length, direction.rotate(self.orientation))):
            if onoff[idx % len(onoff)]:
                yield point + local_position

    def x_ceiling(self, offset, size=ROOM_SIZE):
        yield from self.x_rectangular_prism(offset + FineVector(0, 0, 7), FineVector(size, size, 1))

    def x_floor(self, offset, size=ROOM_SIZE):
        yield from self.x_rectangular_prism(offset, FineVector(size, size, 1))

    def x_low_wall(self, offset, face):
        yield from self.x_wall(offset, face, limit_j=3)

    def x_wall(self, offset, face, limit_j=8):
        if face == EAST:
            yield from self.x_rectangular_prism(offset + FineVector(7, 0, 0), FineVector(1, 8, limit_j))
        elif face == WEST:
            yield from self.x_rectangular_prism(offset + FineVector(0, 0, 0), FineVector(1, 8, limit_j))
        elif face == NORTH:
            yield from self.x_rectangular_prism(offset + FineVector(0, 7, 0), FineVector(8, 1, limit_j))
        elif face == SOUTH:
            yield from self.x_rectangular_prism(offset + FineVector(0, 0, 0), FineVector(8, 1, limit_j))

    def x_ring(self, offset, size):
        # world, FineVector(-2, -2, i), 12, tex=accent_tex)
        yield from self.x_rectangular_prism(offset, FineVector(1, size - 1, 1))
        yield from self.x_rectangular_prism(offset, FineVector(size - 1, 1, 1))
        yield from self.x_rectangular_prism(offset + FineVector(0, size - 1, 0), FineVector(size, 1, 1))
        yield from self.x_rectangular_prism(offset + FineVector(size - 1, 0, 0), FineVector(1, size, 1))

    def x_rectangular_prism(self, offset, xyz):
        xyz = xyz.rotate(self.orientation).vox()
        local_position = self.pos + offset.offset_rotate(self.orientation, offset=TILE_VOX_OFF)

        for point in cube_points(xyz.x, xyz.y, xyz.z):
            yield point + local_position
