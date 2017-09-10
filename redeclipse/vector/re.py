class ivec2:
    """
    2D integer vector class
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def X(self):
        return int(self.x)

    def Y(self):
        return int(self.y)

    def to_dict(self):
        return [self.X(), self.Y()]

    def __repr__(self):
        return '<ivec2 {} {}>'.format(*self.to_dict())


class vec2:
    """Float version of ivec2"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def X(self):
        return float(self.x)

    def Y(self):
        return float(self.y)

    def to_dict(self):
        return [self.X(), self.Y()]

    def __repr__(self):
        return '<vec2 {} {}>'.format(*self.to_dict())


class vec3:
    """
    3D vector class
    """

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def X(self):
        return float(self.x)

    def Y(self):
        return float(self.y)

    def Z(self):
        return float(self.z)

    def to_dict(self):
        return [self.X(), self.Y(), self.Z()]

    def __repr__(self):
        return '<vec3 {} {} {}>'.format(*self.to_dict())


class ivec3:
    """
    3D integer vector class
    """

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def X(self):
        return int(self.x)

    def Y(self):
        return int(self.y)

    def Z(self):
        return int(self.z)

    @classmethod
    def ivec5(cls, i, x, y, z, s):
        return ivec3(
            x + ((i & 1) >> 0) * s,
            y + ((i & 2) >> 1) * s,
            z + ((i & 4) >> 2) * s
        )

    def mask(self, mask):
        return ivec3(
            self.X() & mask,
            self.Y() & mask,
            self.Z() & mask
        )

    def shl(self, shift):
        return ivec3(
            self.X() << shift,
            self.Y() << shift,
            self.Z() << shift,
        )

    def sub(self, b):
        return ivec3(
            self.X() - b.X(),
            self.Y() - b.Y(),
            self.Z() - b.Z()
        )

    def mul(self, s):
        return ivec3(
            self.X() * s,
            self.Y() * s,
            self.Z() * s
        )

    def add(self, b):
        return ivec3(
            self.X() + b.x,
            self.Y() + b.y,
            self.Z() + b.z
        )

    def gg(self, idx):
        if idx == 0:
            return self.X()
        elif idx == 1:
            return self.Y()
        elif idx == 2:
            return self.Z()

    def dot(self, o):
        return self.X() * o.x + self.Y() * o.y + self.Z() * o.z

    def iszero(self):
        return self.X() == 0 and self.Y() == 0 and self.Z() == 0

    def to_dict(self):
        return [self.X(), self.Y(), self.Z()]

    def __repr__(self):
        return '<ivec3 {} {} {}>'.format(*self.to_dict())


def cross(a, b):
    """
    cross product of two ivec3/ivec
    """

    if isinstance(a, ivec3):
        return ivec3(
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x,
        )
    else:
        return vec3(
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x,
        )
