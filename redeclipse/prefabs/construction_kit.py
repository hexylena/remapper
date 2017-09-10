from redeclipse.objects import cube
import random
from redeclipse.vector.orientations import SOUTH, NORTH, WEST, EAST, VEC_ORIENT_MAP_INV
from redeclipse.vector import FineVector, CoarseVector, AbsoluteVector
ROOM_SIZE = 8


def column_points(size, direction):
    for i in range(size):
        if direction in ('-x', '+x', 'x'):
            yield FineVector(i, 0, 0)
        elif direction in ('-y', '+y', 'y'):
            yield FineVector(0, i, 0)
        elif direction in ('-z', '+z', 'z'):
            yield FineVector(0, 0, i)


def wall_points(size, direction, limit_j=100, limit_i=100):
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


def subtract_or_skip(point, subtract, prob):
    if subtract:
        return True
    else:
        if prob < 1:
            if random.random() > prob:
                return True
    return False


class ConstructionKitMixin(object):

    def x_column(self, world, offset, direction, length, tex=2, subtract=False, prob=1.0):
        for point in self._x_column(world, offset, direction, length):
            if subtract_or_skip(point, subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_column(self, world, offset, direction, length):
        offset = offset.rotate(self.orientation)
        adjustment = self.x_get_adjustment()
        local_position = self.pos + offset + adjustment
        # Then get the orientation, rotated, and converted to ±xyz
        orient = VEC_ORIENT_MAP_INV[direction.rotate(self.orientation)]
        for point in column_points(length, orient):
            yield point + local_position

    def x_ceiling(self, world, offset, tex=2, size=ROOM_SIZE, subtract=False, prob=1.0):
        for point in self._x_ceiling(world, offset, size=size):
            if subtract_or_skip(point, subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_ceiling(self, world, offset, size=ROOM_SIZE):
        for point in self._x_rectangular_prism(world, offset + FineVector(0, 0, 7), AbsoluteVector(size, size, 1)):
            yield point

    def x_floor(self, world, offset, tex=2, size=ROOM_SIZE, subtract=False, prob=1.0):
        for point in self._x_floor(world, offset, size=size):
            if subtract_or_skip(point, subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_floor(self, world, offset, size=ROOM_SIZE):
        for point in self._x_rectangular_prism(world, offset, AbsoluteVector(size, size, 1)): yield point

    def x_wall(self, world, offset, face, tex=2, subtract=False, prob=1.0):
        for point in self._x_wall(world, offset, face):
            if subtract_or_skip(point, subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_wall(self, world, offset, face, tex=2):
        offset = offset.rotate(self.orientation)
        local_position = self.pos + offset
        real_face = self.x_get_face(face)

        for point in wall_points(ROOM_SIZE, real_face):
            yield point + local_position

    def x_get_adjustment(self):
        if self.orientation == '+x':
            return CoarseVector(0, 0, 0)
        elif self.orientation == '-x':
            return CoarseVector(1, 1, 0)
        elif self.orientation == '+y':
            return CoarseVector(1, 0, 0)
        elif self.orientation == '-y':
            return CoarseVector(0, 1, 0)

    def x_ring(self, world, offset, size, tex=2, subtract=False, prob=1.0):
        for point in self._x_ring(world, offset, size):
            if subtract_or_skip(point, subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_ring(self, world, offset, size, tex=2):
        # world, FineVector(-2, -2, i), 12, tex=accent_tex)
        for point in self._x_rectangular_prism(world, offset, AbsoluteVector(1, size - 1, 1)):
            yield point
        for point in self._x_rectangular_prism(world, offset, AbsoluteVector(size - 1, 1, 1)):
            yield point
        for point in self._x_rectangular_prism(world, offset + FineVector(0, size - 1, 0), AbsoluteVector(size, 1, 1)):
            yield point
        for point in self._x_rectangular_prism(world, offset + FineVector(size - 1, 0, 0), AbsoluteVector(1, size, 1)):
            yield point

    def x_rectangular_prism(self, world, offset, xyz, tex=2, subtract=False, prob=1.0):
        for point in self._x_rectangular_prism(world, offset, xyz):
            if subtract_or_skip(point, subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_rectangular_prism(self, world, offset, xyz, tex=2):
        offset = offset.rotate(self.orientation)
        xyz = xyz.rotate(self.orientation)
        # We need to offset self.pos with an adjustment vector. Because
        # reasons. Awful awful reasons.
        adjustment = self.x_get_adjustment()
        local_position = self.pos + adjustment + offset

        for point in cube_points(xyz.x, xyz.y, xyz.z):
            yield point + local_position

    def x_low_wall(self, world, offset, face, tex=2, subtract=False, prob=1.0):
        for point in self._x_rectangular_prism(world, offset, face):
            if subtract_or_skip(point, subtract, prob):
                world.del_pointv(point)
                continue
            world.set_pointv(point, cube.newtexcube(tex=tex))

    def _x_low_wall(self, world, offset, face):
        offset = offset.rotate(self.orientation)
        local_position = self.pos + offset
        real_face = self.x_get_face(face)

        for point in wall_points(ROOM_SIZE, real_face, limit_j=2):
            yield point + local_position

    def x_get_face(self, face):
        if self.orientation == '+x':
            if face == NORTH:
                return '-x'
            elif face == SOUTH:
                return '+x'
            elif face == EAST:
                return '+y'
            elif face == WEST:
                return '-y'
        elif self.orientation == '-x':
            if face == NORTH:
                return '+x'
            elif face == SOUTH:
                return '-x'
            elif face == EAST:
                return '-y'
            elif face == WEST:
                return '+y'
        elif self.orientation == '+y':
            if face == NORTH:
                return '-y'
            elif face == SOUTH:
                return '+y'
            elif face == EAST:
                return '+x'
            elif face == WEST:
                return '-x'
        elif self.orientation == '-y':
            if face == NORTH:
                return '+y'
            elif face == SOUTH:
                return '-y'
            elif face == EAST:
                return '-x'
            elif face == WEST:
                return '+x'
        else:
            raise Exception()


def cube_points(x, y, z):
    """
    call with a single number for a cube, or x, y, z for a rectangular prism
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


def rotate(position, orientation):
    (x, y, z) = position
    if orientation == '-x':
        return (x, y, z)
    elif orientation == '+x':
        return (-x, y, z)
    elif orientation == '-y':
        return (y, x, z)
    elif orientation == '+y':
        return (y, -x, z)
    else:
        raise Exception("Unknown Orientation")
