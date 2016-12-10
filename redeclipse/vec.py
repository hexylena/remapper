class ivec2:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def X(self):
        return int(self.x)

    def Y(self):
        return int(self.y)

    def to_dict(self):
        return [self.X(), self.Y()]


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


class vec3:
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


class ivec3:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def ivec5(cls, i, x, y, z, s):
        return ivec3(
            x + ((i&1)>>0) * s,
            y + ((i&2)>>1) * s,
            z + ((i&4)>>2) * s
        )

    def mask(self, mask):
        return ivec3(
            self.x & mask,
            self.y & mask,
            self.z & mask
        )

    def shl(self, shift):
        return ivec3(
            self.x << shift,
            self.y << shift,
            self.z << shift,
        )

    def sub(self, b):
        return ivec3(
            self.x - b.x,
            self.y - b.y,
            self.z - b.z
        )

    def mul(self, s):
        return ivec3(
            self.x * s,
            self.y * s,
            self.z * s
        )

    def add(self, b):
        return ivec3(
            self.x + b.x,
            self.y + b.y,
            self.z + b.z
        )

    def gg(self, idx):
        if idx == 0:
            return self.x
        elif idx == 1:
            return self.y
        elif idx == 2:
            return self.z

    def dot(self, o):
        return self.x*o.x + self.y*o.y + self.z*o.z

    def iszero(self):
        return self.x == 0 and self.y == 0 and self.z == 0

    def __str__(self):
        return "(%d, %d, %d)" % (self.x, self.y, self.z)

    def to_dict(self):
        return [self.X(), self.Y(), self.Z()]


def cross(a, b):
    if isinstance(a, ivec3):
        return ivec3(
            a.y*b.z-a.z*b.y,
            a.z*b.x-a.x*b.z,
            a.x*b.y-a.y*b.x,
        )
    else:
        return vec3(
            a.y*b.z-a.z*b.y,
            a.z*b.x-a.x*b.z,
            a.x*b.y-a.y*b.x,
        )

