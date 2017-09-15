from redeclipse.objects import cube
import random
from redeclipse.vector.orientations import SOUTH, NORTH, WEST, EAST, ABOVE, BELOW, VEC_ORIENT_MAP, get_vector_rotation
from redeclipse.vector import FineVector, CoarseVector, AbsoluteVector
ROOM_SIZE = 8


def column_points(size, direction):
    """
    Yield points needed to draw a column

    :param int size: Length of column
    :param str direction: direction the column should go in. One of (±x/y/z)

    :returns: An iterable of FineVectors
    :rtype: list(redeclipse.vector.FineVector)
    """
    for i in range(size):
        if direction == NORTH:
            yield FineVector(i, 0, 0)
        elif direction == SOUTH:
            yield FineVector(-i, 0, 0)
        elif direction == EAST:
            yield FineVector(0, i, 0)
        elif direction == WEST:
            yield FineVector(0, -i, 0)
        elif direction == ABOVE:
            yield FineVector(0, 0, i)
        elif direction == BELOW:
            yield FineVector(0, 0, -i)


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
    else:
        i_lower_bound = size
        i_upper_bound = 0

    for i in range(i_lower_bound, i_upper_bound):
        # Allow partial_j walls
        if i > limit_i:
            continue

        if size > 0:
            j_lower_bound = 0
            j_upper_bound = size
        else:
            j_lower_bound = size
            j_upper_bound = 0

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

    def x_column(self, world, offset, direction, length, tex=2, subtract=False, prob=1.0):
        """
        Draw a column

        :param world: The universe
        :type world: redeclipse.voxel.VoxelWorld

        :param offset: The offset to start drawing at.
        :type offset: redeclipse.vector.FineVector or redeclipse.vector.CoarseVector

        :param direction: The direction to draw the column in
        :type direction: str

        :param length: The length of the column
        :type length: str

        :param tex: Texture index
        :type tex: int

        :param subtract: Should we instead subtract the selected space
        :type subtract: boolean

        :param prob: Probability of placing any given cube.
        :type prob: float
        """
        for point in self._x_column(offset, direction, length):
            if subtract_or_skip(subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_column(self, offset, direction, length):
        offset = offset.rotate(self.orientation)
        adjustment = self.x_get_adjustment()
        local_position = self.pos + offset + adjustment
        # Then get the orientation, rotated, and converted to +/-xyz
        for point in column_points(length, direction.rotate(self.orientation)):
            yield point + local_position

    def x_ceiling(self, world, offset, tex=2, size=ROOM_SIZE, subtract=False, prob=1.0):
        """
        Draw a ceiling

        :param world: The universe
        :type world: redeclipse.voxel.VoxelWorld

        :param offset: The offset to start drawing at.
        :type offset: redeclipse.vector.FineVector or redeclipse.vector.CoarseVector

        :param size: The size of the wall (usually 8)
        :type size: str

        :param tex: Texture index
        :type tex: int

        :param subtract: Should we instead subtract the selected space
        :type subtract: boolean

        :param prob: Probability of placing any given cube.
        :type prob: float
        """
        for point in self._x_ceiling(offset, size=size):
            if subtract_or_skip(subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_ceiling(self, offset, size=ROOM_SIZE):
        for point in self._x_rectangular_prism(
                offset + FineVector(0, 0, 7),
                AbsoluteVector(size, size, 1)
        ):
            yield point

    def x_floor(self, world, offset, tex=2, size=ROOM_SIZE, subtract=False, prob=1.0):
        """
        Draw a floor

        :param world: The universe
        :type world: redeclipse.voxel.VoxelWorld

        :param offset: The offset to start drawing at.
        :type offset: redeclipse.vector.FineVector or redeclipse.vector.CoarseVector

        :param size: The size of the floor
        :type size: str

        :param tex: Texture index
        :type tex: int

        :param subtract: Should we instead subtract the selected space
        :type subtract: boolean

        :param prob: Probability of placing any given cube.
        :type prob: float
        """
        for point in self._x_floor(offset, size=size):
            if subtract_or_skip(subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_floor(self, offset, size=ROOM_SIZE):
        for point in self._x_rectangular_prism(offset, AbsoluteVector(size, size, 1)): yield point

    def x_wall(self, world, offset, face, tex=2, subtract=False, prob=1.0):
        """
        Draw a wall (non-floor)

        :param world: The universe
        :type world: redeclipse.voxel.VoxelWorld

        :param offset: The offset to start drawing at.
        :type offset: redeclipse.vector.FineVector or redeclipse.vector.CoarseVector

        :param face: The face to draw the wall on
        :type face: redeclipse.vector.orientations.NORTH or redeclipse.vector.orientations.EAST or
                    redeclipse.vector.orientations.SOUTH or redeclipse.vector.orientations.WEST or
                    redeclipse.vector.orientations.BELOW or redeclipse.vector.orientations.ABOVE

        :param size: The size of the floor
        :type size: str

        :param tex: Texture index
        :type tex: int

        :param subtract: Should we instead subtract the selected space
        :type subtract: boolean

        :param prob: Probability of placing any given cube.
        :type prob: float
        """
        for point in self._x_wall(offset, face):
            if subtract_or_skip(subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_wall(self, offset, face):
        offset = offset.rotate(self.orientation)
        local_position = self.pos + offset
        real_face = self.x_get_face(face)

        for point in wall_points(ROOM_SIZE, real_face):
            yield point + local_position

    def x_get_adjustment(self):
        """
        Get the offset/adjustment needed in some circumstances.

        :returns: a vector to be added to position
        :rtype: redeclipse.vector.CoarseVector
        """
        if self.orientation == '+x':
            return CoarseVector(0, 0, 0)
        elif self.orientation == '-x':
            return CoarseVector(1, 1, 0)
        elif self.orientation == '+y':
            return CoarseVector(1, 0, 0)
        elif self.orientation == '-y':
            return CoarseVector(0, 1, 0)

    def x_ring(self, world, offset, size, tex=2, subtract=False, prob=1.0):
        """
        Draw a ring

        :param world: The universe
        :type world: redeclipse.voxel.VoxelWorld

        :param offset: The offset to start drawing at.
        :type offset: redeclipse.vector.FineVector or redeclipse.vector.CoarseVector

        :param size: The size of the ring
        :type size: str

        :param tex: Texture index
        :type tex: int

        :param subtract: Should we instead subtract the selected space
        :type subtract: boolean

        :param prob: Probability of placing any given cube.
        :type prob: float
        """
        for point in self._x_ring(offset, size):
            if subtract_or_skip(subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_ring(self, offset, size):
        # world, FineVector(-2, -2, i), 12, tex=accent_tex)
        for point in self._x_rectangular_prism(offset, AbsoluteVector(1, size - 1, 1)):
            yield point
        for point in self._x_rectangular_prism(offset, AbsoluteVector(size - 1, 1, 1)):
            yield point
        for point in self._x_rectangular_prism(offset + FineVector(0, size - 1, 0), AbsoluteVector(size, 1, 1)):
            yield point
        for point in self._x_rectangular_prism(offset + FineVector(size - 1, 0, 0), AbsoluteVector(1, size, 1)):
            yield point

    def x_rectangular_prism(self, world, offset, xyz, tex=2, subtract=False, prob=1.0):
        """
        Draw a rectangular prism

        :param world: The universe
        :type world: redeclipse.voxel.VoxelWorld

        :param offset: The offset to start drawing at.
        :type offset: redeclipse.vector.FineVector or redeclipse.vector.CoarseVector

        :param xyz: The size of the rectangular prism
        :type xyz: redeclipse.vector.AbsoluteVector

        :param tex: Texture index
        :type tex: int

        :param subtract: Should we instead subtract the selected space
        :type subtract: boolean

        :param prob: Probability of placing any given cube.
        :type prob: float
        """
        for point in self._x_rectangular_prism(offset, xyz):
            if subtract_or_skip(subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_rectangular_prism(self, offset, xyz):
        offset = offset.rotate(self.orientation)
        xyz = xyz.rotate(self.orientation)
        # We need to offset self.pos with an adjustment vector. Because
        # reasons. Awful awful reasons.
        adjustment = self.x_get_adjustment()
        local_position = self.pos + adjustment + offset

        for point in cube_points(xyz.x, xyz.y, xyz.z):
            yield point + local_position

    def x_low_wall(self, world, offset, face, tex=2, subtract=False, prob=1.0):
        """
        Draw a low wall (2 high)

        :param world: The universe
        :type world: redeclipse.voxel.VoxelWorld

        :param offset: The offset to start drawing at.
        :type offset: redeclipse.vector.FineVector or redeclipse.vector.CoarseVector

        :param face: The face to draw the wall on
        :type face: redeclipse.vector.orientations.NORTH or redeclipse.vector.orientations.EAST or
                    redeclipse.vector.orientations.SOUTH or redeclipse.vector.orientations.WEST or
                    redeclipse.vector.orientations.BELOW or redeclipse.vector.orientations.ABOVE

        :param tex: Texture index
        :type tex: int

        :param subtract: Should we instead subtract the selected space
        :type subtract: boolean

        :param prob: Probability of placing any given cube.
        :type prob: float
        """
        for point in self._x_low_wall(offset, face):
            if subtract_or_skip(subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_low_wall(self, offset, face):
        offset = offset.rotate(self.orientation)
        local_position = self.pos + offset
        real_face = self.x_get_face(face)
        print('>', offset, local_position, real_face)

        for point in wall_points(ROOM_SIZE, real_face, limit_j=2):
            print('.', point)
            yield point + local_position

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
