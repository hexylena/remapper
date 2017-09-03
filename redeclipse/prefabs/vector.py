from math import sin, cos, pi


def rotate_yaw(angle, orientation):
    if orientation == '+x':
        return angle
    elif orientation == '+y':
        return (angle + 90) % 360
    elif orientation == '-x':
        return (angle + 180) % 360
    elif orientation == '-y':
        return (angle + 270) % 360


class BaseVector(object):
    def __init__(self, x, y, z):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)

    def __add__(self, other):
        return BaseVector(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    def __sub__(self, other):
        return BaseVector(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
        )

    def __mul__(self, m):
        return BaseVector(
            self.x * m,
            self.y * m,
            self.z * m
        )

    def __div__(self, m):
        return BaseVector(
            self.x / m,
            self.y / m,
            self.z / m
        )

    def __repr__(self):
        return 'BV(%s, %s, %s)' % (self.x, self.y, self.z)

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        elif key == 2:
            return self.z
        raise Exception("Could not access %s" % key)

    def __len__(self):
        return 3

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def rotate(self, deg):
        """
        Return a new vector, rotated by the specified
        number of degrees.

        :param deg: degrees (0, 90, 180, ...) or orientation (+x, -x, ...)
        :type deg: str or int

        :returns: a new ``redeclipse.prefabs.vector.BaseVector``, rotated as
                  needed.
        :rtype: redeclipse.prefabs.vector.BaseVector
        """
        if deg == '+x':
            deg = 0
        elif deg == '-x':
            deg = 180
        elif deg == '+y':
            deg = 90
        elif deg == '-y':
            deg = 270

        if deg % 90 != 0:
            raise ValueError("Degree must be a multiple of 90.")

        theta = pi * deg / 180
        return BaseVector(
            self.x * cos(theta) - self.y * sin(theta),
            self.x * sin(theta) + self.y * cos(theta),
            self.z
        )


class FineVector(BaseVector):
    def __add__(self, other):
        if isinstance(other, CoarseVector):
            return FineVector(
                self.x + (8 * other.x),
                self.y + (8 * other.y),
                self.z + (8 * other.z)
            )
        elif isinstance(other, FineVector):
            return FineVector(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z
            )
        else:
            raise Exception("Operation not defined for type %s" % type(other))

    def __sub__(self, other):
        if isinstance(other, CoarseVector):
            return FineVector(
                self.x - (8 * other.x),
                self.y - (8 * other.y),
                self.z - (8 * other.z)
            )
        elif isinstance(other, FineVector):
            return FineVector(
                self.x - other.x,
                self.y - other.y,
                self.z - other.z
            )
        else:
            raise Exception("Operation not defined for type %s" % type(other))

    def __mul__(self, m):
        return FineVector(
            self.x * m,
            self.y * m,
            self.z * m
        )

    def __repr__(self):
        rp = super().__repr__()
        if rp == 'BV(1, 0, 0)':
            return 'FV(NORTH)'
        elif rp == 'BV(-1, 0, 0)':
            return 'FV(SOUTH)'
        elif rp == 'BV(0, 1, 0)':
            return 'FV(EAST)'
        elif rp == 'BV(0, -1, 0)':
            return 'FV(WEST)'
        return 'FV(%s)' % rp


    def rotate(self, deg):
        rotation = super().rotate(deg)
        return FineVector(
            rotation.x,
            rotation.y,
            rotation.z
        )


class CoarseVector(BaseVector):
    def __add__(self, other):
        if isinstance(other, CoarseVector):
            return CoarseVector(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z
            )
        elif isinstance(other, FineVector):
            return FineVector(
                (8 * self.x) + other.x,
                (8 * self.y) + other.y,
                (8 * self.z) + other.z
            )
        else:
            raise Exception("Operation not defined for type %s" % type(other))

    def __sub__(self, other):
        if isinstance(other, CoarseVector):
            return CoarseVector(
                self.x - other.x,
                self.y - other.y,
                self.z - other.z
            )
        elif isinstance(other, FineVector):
            return FineVector(
                (8 * self.x) - other.x,
                (8 * self.y) - other.y,
                (8 * self.z) - other.z
            )
        else:
            raise Exception("Operation not defined for type %s" % type(other))

    def __mul__(self, m):
        return CoarseVector(
            self.x * m,
            self.y * m,
            self.z * m
        )

    def __repr__(self):
        rp = super().__repr__()
        if rp == 'BV(1, 0, 0)':
            return 'CV(NORTH)'
        elif rp == 'BV(-1, 0, 0)':
            return 'CV(SOUTH)'
        elif rp == 'BV(0, 1, 0)':
            return 'CV(EAST)'
        elif rp == 'BV(0, -1, 0)':
            return 'CV(WEST)'
        return 'CV(%s)' % rp

    def rotate(self, deg):
        rotation = super().rotate(deg)
        return CoarseVector(
            rotation.x,
            rotation.y,
            rotation.z
        )

    def fine(self):
        return self * 8
