from math import sin, cos, pi


def rotate_yaw(angle, orientation):
    if orientation == '+x':
        return angle % 360
    elif orientation == '+y':
        return (angle + 90) % 360
    elif orientation == '-x':
        return (angle + 180) % 360
    elif orientation == '-y':
        return (angle + 270) % 360
    raise Exception("Unexpected orientation")


class BaseVector(object):

    def __hash__(self):
        return (0 << 31) + (self.x << 20) + (self.y << 10) + self.z

    def __eq__(self, other):
        return isinstance(other, BaseVector) and \
            self.x == other.x and \
            self.y == other.y and \
            self.z == other.z

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
        if deg == '+x':
            deg = 0
        elif deg == '-y':
            deg = 90
        elif deg == '-x':
            deg = 180
        elif deg == '+y':
            deg = 270

        if deg % 90 != 0:
            raise ValueError("Degree must be a multiple of 90.")

        theta = pi * deg / 180
        return BaseVector(
            round(self.x * cos(theta) - self.y * sin(theta)),
            round(self.x * sin(theta) + self.y * cos(theta)),
            self.z
        )


class AbsoluteVector(BaseVector):
    """
    This is a derivative of BaseVector specifically for some odd circumstances,
    namely making rectangular prisms. It has odd rotational semantics
    specifically for use there.
    """

    def __hash__(self):
        return (1 << 31) + (self.x << 20) + (self.y << 10) + self.z

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
        return (2 << 31) + (self.x << 20) + (self.y << 10) + self.z

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
        return 'FV(%s)' % rp

    def rotate(self, deg):
        rotation = super().rotate(deg)
        return FineVector(
            rotation.x,
            rotation.y,
            rotation.z
        )

    def fine(self):
        return self


class CoarseVector(BaseVector):

    def __hash__(self):
        return (3 << 31) + (self.x << 20) + (self.y << 10) + self.z

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
        return 'CV(%s)' % rp

    def rotate(self, deg):
        rotation = super().rotate(deg)
        return CoarseVector(
            rotation.x,
            rotation.y,
            rotation.z
        )

    def fine(self):
        newvec = self * 8
        return FineVector(
            newvec.x,
            newvec.y,
            newvec.z
        )
