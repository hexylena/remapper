from redeclipse.objects import cube
import random
from redeclipse.vector.orientations import TILE_VOX_OFF, VOXEL_OFFSET, NORTH, SOUTH, EAST, WEST, ABOVE
from redeclipse.vector import FineVector
ROOM_SIZE = 8


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

            if direction == '-z':
                yield FineVector(i, j, 0)
            elif direction == '+z':
                yield FineVector(i, j, size - 1)
            elif direction == '-y':
                yield FineVector(i, 0, j)
            elif direction == '+y':
                yield FineVector(i, size - 1, j)
            elif direction == '-x':
                yield FineVector(0, i, j)
            elif direction == '+x':
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
        x_lower_bound = x
        x_upper_bound = 0

    if y > 0:
        y_lower_bound = 0
        y_upper_bound = y
    else:
        y_lower_bound = y
        y_upper_bound = 0

    if z > 0:
        z_lower_bound = 0
        z_upper_bound = z
    else:
        z_lower_bound = z
        z_upper_bound = 0

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

        for point in func(*args, **kwargs):
            if subtract_or_skip(subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def x_column(self, offset, direction, length):
        local_position = self.pos + offset.offset_rotate(self.orientation, offset=TILE_VOX_OFF)
        for point in column_points(length, direction.rotate(self.orientation)):
            yield point + local_position

    def x_ceiling(self, offset, size=ROOM_SIZE):
        room_center = VOXEL_OFFSET - FineVector(ROOM_SIZE / 2, ROOM_SIZE / 2, 0)
        for i in range(ROOM_SIZE):
            # Loop across the 'bottom' edge
            off = offset + FineVector(i, 0, 7)
            # sum these two together to get the offset for a column to start from.
            lop = self.pos + off.offset_rotate(self.orientation, offset=room_center)
            # And then yield those.
            for point in column_points(ROOM_SIZE, NORTH.rotate(self.orientation)):
                yield point + lop

    def x_floor(self, offset, size=ROOM_SIZE):
        # Get the center for an arbitrary sized room
        room_center = VOXEL_OFFSET - FineVector(ROOM_SIZE / 2, ROOM_SIZE / 2, 0)
        for i in range(ROOM_SIZE):
            # Loop across the 'bottom' edge
            off = offset + FineVector(i, 0, 0)
            # sum these two together to get the offset for a column to start from.
            lop = self.pos + off.offset_rotate(self.orientation, offset=room_center)
            # And then yield those.
            for point in column_points(ROOM_SIZE, NORTH.rotate(self.orientation)):
                print(point, lop, point + lop)
                yield point + lop

    def x_low_wall(self, offset, face):
        yield from self.x_wall(offset, face, limit_j=2)

    def x_wall(self, offset, face, limit_j=8):
        # Get a vector for where we should start drawing.
        if face == SOUTH:
            vec = 0
        elif face == EAST:
            vec = 90
        elif face == NORTH:
            vec = 180
        elif face == WEST:
            vec = 270

        print('wall', offset, face, limit_j, vec)
        for i in range(8):
            # Loop across the 'bottom' edge
            # off = FineVector(i, 0, 0).offset_rotate(vec, offset=TILE_VOX_OFF)
            # sum these two together to get the offset for a column to start from.
            # lop = self.pos + off.offset_rotate(self.orientation, offset=TILE_VOX_OFF)
            print('\t', FineVector(i, 0, 0).offset_rotate(vec, offset=TILE_VOX_OFF))
            # And then yield those.
            for point in column_points(ROOM_SIZE, ABOVE):
                yield point

    # def x_ring(self, offset, size):
        # # world, FineVector(-2, -2, i), 12, tex=accent_tex)
        # yield from self.x_rectangular_prism(offset, FineVector(1, size - 1, 1))
        # yield from self.x_rectangular_prism(offset, FineVector(size - 1, 1, 1))
        # yield from self.x_rectangular_prism(offset + FineVector(0, size - 1, 0), FineVector(size, 1, 1))
        # yield from self.x_rectangular_prism(offset + FineVector(size - 1, 0, 0), FineVector(1, size, 1))

    def x_rectangular_prism(self, offset, xyz):
        xyz = xyz.rotate(self.orientation).vox()
        local_position = self.pos + offset.offset_rotate(self.orientation, offset=TILE_VOX_OFF)
        print(local_position, xyz)

        for point in cube_points(xyz.x, xyz.y, xyz.z):
            yield point + local_position

    def x_get_face(self, face):
        """
        Get the appropriate translation of ``face`` for ``self.orientation``

        :param face: The face that we want to represent
        :type face: redeclipse.vector.CoarseVector


        >>> f(0, 0, 0).offset_rotate(90, offset=f(-3.5, -3.5, .5))
        FV(BV(7.0, 0.0, 0.0))
        >>> f(0, 0, 0).offset_rotate(180, offset=f(-3.5, -3.5, .5))
        FV(BV(7.0, 7.0, 0.0))
        >>> f(0, 0, 0).offset_rotate(270, offset=f(-3.5, -3.5, .5))
        FV(BV(0.0, 7.0, 0.0))

        :returns: New style direction
        :rtype: redeclipse.vector.CoarseVector
        """
