from math import sin, cos, pi, floor, atan2


class BaseVector(object):

    def __hash__(self):
        return (0 << 31) + (floor(self.x) << 20) + (floor(self.y) << 10) + floor(self.z)

    def __eq__(self, other):
        return isinstance(other, BaseVector) and \
            self.x == other.x and \
            self.y == other.y and \
            self.z == other.z

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        if self.__class__ == other.__class__:
            return self.__class__(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z,
            )
        else:
            raise Exception("addition not defined for dissimilar classes")

    def __sub__(self, other):
        if self.__class__ == other.__class__:
            return self.__class__(
                self.x - other.x,
                self.y - other.y,
                self.z - other.z,
            )
        else:
            raise Exception("addition not defined for dissimilar classes")

    def __mul__(self, m):
        return self.__class__(
            self.x * m,
            self.y * m,
            self.z * m
        )

    def __truediv__(self, m):
        return self.__class__(
            self.x / m,
            self.y / m,
            self.z / m
        )

    def __floordiv__(self, m):
        return self.__class__(
            floor(self.x / m),
            floor(self.y / m),
            floor(self.z / m)
        )

    def __repr__(self):
        return 'BV(%s, %s, %s)' % (self.x, self.y, self.z)
        # return 'BV(%s, %s, %s)VBV(%s, %s, %s)' % (self.x, self.y, self.z, floor(self.x), floor(self.y), floor(self.z))

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

    def __lt__(self, other):
        """
        https://math.stackexchange.com/questions/54655/how-to-compare-points-in-multi-dimensional-space

        This ordering isn't a super logical one, but it is a functional one
        which is what we need to provide sorted() ability.
        """
        if self.x < other.x:
            return True
        elif self.x == other.x:
            if self.y < other.y:
                return True
            elif self.y == other.y:
                if self.z < other.z:
                    return True
        return False

    def __le__(self, other):
        return self == other or self < other

    def vox(self):
        """
        Return a voxel-appropriate version of self (i.e. apply floor to drag it to the right location.)
        """
        return self.__class__(floor(self.x), floor(self.y), floor(self.z))

    def rotate(self, deg):
        """
        Return a new vector, rotated by the specified
        number of degrees.

        :param deg: degrees (0, 90, 180, ...) or orientation (+x, -x, ...)
        :type deg: str or int

        Note that rotation is counterclockwise around the z=+1 axis. I.e. use
        the right handle rule.

        :returns: a new ``redeclipse.vector.BaseVector``, rotated as
                  needed.
        :rtype: redeclipse.vector.BaseVector
        """
        if not isinstance(deg, int):
            y = deg.y
            x = deg.x
            theta = atan2(y, x)
        else:
            theta = pi * deg / 180
        # We allow 0.5 increments for properly centered cubes. So we need to do
        # the math in double, round it there, then divide by two to ensure
        # everything is in (0, 0.5, 1, 1.5, ...)
        return self.__class__(
            round((2 * self.x * cos(theta)) - (2 * self.y * sin(theta))) / 2,
            round((2 * self.x * sin(theta)) + (2 * self.y * cos(theta))) / 2,
            self.z
        )

    def offset_rotate(self, deg, offset=None):
        """
        Return a new vector, rotated by the specified
        number of degrees.

        :param deg: degrees (0, 90, 180, ...) or orientation (+x, -x, ...)
        :type deg: str or int

        :param offset: point around which to rotate
        :type offset: redeclipse.vector.BaseVector (or child thereof)

        Note that rotation is counterclockwise around the z=+1 axis. I.e. use
        the right handle rule.

        :returns: a new ``redeclipse.vector.BaseVector``, rotated as
                  needed.
        :rtype: redeclipse.vector.BaseVector
        """
        # TODO: We could auto-vox_off, not sure if this is useful?
        return (self + offset).rotate(deg) - offset


class AbsoluteVector(BaseVector):
    """
    This is a derivative of BaseVector specifically for some odd circumstances,
    namely making rectangular prisms. It has odd rotational semantics
    specifically for use there.
    """

    def __hash__(self):
        return (1 << 31) + (floor(self.x) << 20) + (floor(self.y) << 10) + floor(self.z)

    def rotate(self, deg):
        """
        Obtain a rotated version of self by deg

        :param deg: Angle to rotate (clockwise). Can either be ±x/y, or a
                    positive multiple of 90.
        :type deg: str or int
        """
        if deg == '+x':
            deg = 0
        elif deg == '-y':
            deg = 90
        elif deg == '-x':
            deg = 180
        elif deg == '+y':
            deg = 270

        deg %= 360

        if deg == 0:
            return AbsoluteVector(self.x, self.y, self.z)
        elif deg == 90:
            return AbsoluteVector(-self.y, self.x, self.z)
        elif deg == 180:
            return AbsoluteVector(-self.x, -self.y, self.z)
        elif deg == 270:
            return AbsoluteVector(self.y, -self.x, self.z)
        else:
            raise ValueError("Degree must be a multiple of 90.")

    def __repr__(self):
        rp = super().__repr__()
        return 'AV(%s)' % rp


class FineVector(BaseVector):

    def __hash__(self):
        return (2 << 31) + (floor(self.x) << 20) + (floor(self.y) << 10) + floor(self.z)

    def __eq__(self, other):
        if isinstance(other, CoarseVector):
            # If the other one is coarse, convert the other to fine so they're
            # the same.
            tmp = other.fine()
            return \
                self.x == tmp.x and \
                self.y == tmp.y and \
                self.z == tmp.z

        elif isinstance(other, FineVector):
            # Otherwise just compare as-is
            return \
                self.x == other.x and \
                self.y == other.y and \
                self.z == other.z

        else:
            return False

    def __repr__(self):
        rp = super().__repr__()
        return 'FV(%s)' % rp

    def fine(self):
        return self

    def __add__(self, other):
        a = self.fine()
        b = other.fine()
        return FineVector(
            a.x + b.x,
            a.y + b.y,
            a.z + b.z,
        )

    def __sub__(self, other):
        a = self.fine()
        b = other.fine()
        return FineVector(
            a.x - b.x,
            a.y - b.y,
            a.z - b.z,
        )


class CoarseVector(BaseVector):

    def __hash__(self):
        return (3 << 31) + (floor(self.x) << 20) + (floor(self.y) << 10) + floor(self.z)

    def __eq__(self, other):
        if isinstance(other, CoarseVector):
            # If we're both coarse, compare as-is
            return \
                self.x == other.x and \
                self.y == other.y and \
                self.z == other.z
        elif isinstance(other, FineVector):
            # If the other one is fine, convert ourselves to find so we can
            # compare
            tmp = self.fine()
            return \
                tmp.x == other.x and \
                tmp.y == other.y and \
                tmp.z == other.z
        else:
            return False

    def __repr__(self):
        rp = super().__repr__()
        return 'CV(%s)' % rp

    def fine(self):
        newvec = self * 8
        return FineVector(
            newvec.x,
            newvec.y,
            newvec.z
        )

    def __add__(self, other):
        if isinstance(other, CoarseVector):
            return CoarseVector(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z,
            )
        elif isinstance(other, FineVector):
            a = self.fine()
            b = other.fine()
            return FineVector(
                a.x + b.x,
                a.y + b.y,
                a.z + b.z,
            )
        else:
            raise Exception("Unsupported operand")

    def __sub__(self, other):
        if isinstance(other, CoarseVector):
            return CoarseVector(
                self.x - other.x,
                self.y - other.y,
                self.z - other.z,
            )
        elif isinstance(other, FineVector):
            a = self.fine()
            b = other.fine()
            return FineVector(
                a.x - b.x,
                a.y - b.y,
                a.z - b.z,
            )
        else:
            raise Exception("Unsupported operand")
