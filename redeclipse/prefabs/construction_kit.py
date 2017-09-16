from redeclipse.objects import cube
import random
from redeclipse.vector.orientations import VEC_ORIENT_MAP, get_vector_rotation, TILE_VOX_OFF, VOXEL_OFFSET, NORTH
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
        yield from self.x_rectangular_prism(
            offset + FineVector(0, 0, 7),
            FineVector(size, size, 1)
        )

    def x_floor(self, offset, size=ROOM_SIZE):
        # Get the center for an arbitrary sized room
        room_center = VOXEL_OFFSET - FineVector(ROOM_SIZE / 2, ROOM_SIZE / 2, 0)
        print('room center', room_center)
        for i in range(ROOM_SIZE):
            # Loop across the 'bottom' edge
            off = offset + FineVector(i, 0, 0)
            print('off', off)
            # sum these two together to get the offset for a column to start from.
            lop = self.pos + off.offset_rotate(self.orientation, offset=room_center)
            print('lop', lop)
            # And then yield those.
            for point in column_points(ROOM_SIZE, NORTH.rotate(self.orientation)):
                yield point + lop

    def x_wall(self, offset, face, limit_j=8):
        local_position = self.pos + offset.offset_rotate(self.orientation, offset=TILE_VOX_OFF)
        real_face = self.x_get_face(face)

        for point in wall_points(ROOM_SIZE, real_face, limit_j=limit_j):
            yield point + local_position

    def x_ring(self, offset, size):
        # world, FineVector(-2, -2, i), 12, tex=accent_tex)
        yield from self.x_rectangular_prism(offset, FineVector(1, size - 1, 1))
        yield from self.x_rectangular_prism(offset, FineVector(size - 1, 1, 1))
        yield from self.x_rectangular_prism(offset + FineVector(0, size - 1, 0), FineVector(size, 1, 1))
        yield from self.x_rectangular_prism(offset + FineVector(size - 1, 0, 0), FineVector(1, size, 1))

    def x_rectangular_prism(self, offset, xyz):
        xyz = xyz.rotate(self.orientation).vox()
        local_position = self.pos + offset.offset_rotate(self.orientation, offset=TILE_VOX_OFF)
        print(local_position, xyz)

        for point in cube_points(xyz.x, xyz.y, xyz.z):
            yield point + local_position

    def x_low_wall(self, offset, face):
        yield from self._x_wall(offset, face, limit_j=2)

    def x_get_face(self, face):
        """
        Get the appropriate translation of ``face`` for ``self.orientation``

        :param face: The face that we want to represent
        :type face: redeclipse.vector.CoarseVector

        :returns: New style direction
        :rtype: redeclipse.vector.CoarseVector
        """
        # Convert self's orientation to a vector
        ori_vec = VEC_ORIENT_MAP[self.orientation]
        # Get the "rotation" of this vector (i.e. 0/90/180/270)
        ori_dir = get_vector_rotation(ori_vec)
        # Now we add the rotation of our orientation to the requested face.
        return face.rotate(ori_dir)
