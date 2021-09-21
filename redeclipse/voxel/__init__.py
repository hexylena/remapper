"""
We can't work with octrees. Just... no.

So we work in a voxel world, and then convert this to an octree with the small
resolution cube that makes sense, and then let RE optimise the map when need be.
"""
from redeclipse.objects import cube
from redeclipse.enums import OCT
import logging
log = logging.getLogger(__name__)


class VoxelWorld:

    def __init__(self, size=2**7):
        # Size defines number of cubes from left to right.
        self.size = size
        self.world = {}

        # Boundaries
        self.xmax = 0
        self.xmin = size
        self.ymax = 0
        self.ymin = size
        self.zmax = 0
        self.zmin = size

    def _update_boundaries(self, x, y, z):
        if x > self.xmax:
            self.xmax = x
        if x < self.xmin:
            self.xmin = x
        if y > self.ymax:
            self.ymax = y
        if y < self.ymin:
            self.ymin = y
        if z > self.zmax:
            self.zmax = z
        if z < self.zmin:
            self.zmin = z

    def set_point(self, x, y, z, data):
        log.debug("set_point (%d, %d, %d)", x, y, z)
        self._update_boundaries(x, y, z)
        self.world[x, y, z] = data

    def set_pointv(self, xyz, data):
        log.debug("set_point %s", xyz)
        self._update_boundaries(xyz.x, xyz.y, xyz.z)
        self.world[tuple(xyz)] = data

    def del_point(self, x, y, z):
        log.debug("del_point (%d, %d, %d)", x, y, z)
        if (x, y, z) in self.world:
            del self.world[x, y, z]

    def del_pointv(self, xyz):
        (x, y, z) = xyz
        if (x, y, z) in self.world:
            del self.world[x, y, z]

    def get_point(self, x, y, z):
        if (x, y, z) in self.world:
            return self.world[x, y, z]
        else:
            return None

    def to_magicavoxel(self, path):
        import redeclipse.magicavoxel.writer
        from redeclipse.prefabs import TEXMAN
        with open(path, 'wb') as handle:
            redeclipse.magicavoxel.writer.to_magicavoxel(self, handle, TEXMAN)

    def to_octree(self, x_bounds=None, y_bounds=None, z_bounds=None, layers=False):
        if x_bounds is None:
            x_bounds = (
                0, self.size
            )
            y_bounds = (
                0, self.size
            )
            z_bounds = (
                0, self.size
            )

        # If it is the smallest possible cube, just return the cube
        # structure. Since we always go in perfect cubes, only need to
        # check one.
        if x_bounds[1] - x_bounds[0] == 1:
            return self.get_point(x_bounds[0], y_bounds[0], z_bounds[0])

        # Otherwise, split into 8 smaller cubes
        current_level_cubes = [
            self.to_octree(
                (x_bounds[0], (sum(x_bounds) // 2)),
                (y_bounds[0], (sum(y_bounds) // 2)),
                (z_bounds[0], (sum(z_bounds) // 2))
            ),
            self.to_octree(
                ((sum(x_bounds) // 2), x_bounds[1]),
                (y_bounds[0], (sum(y_bounds) // 2)),
                (z_bounds[0], (sum(z_bounds) // 2))
            ),
            self.to_octree(
                (x_bounds[0], (sum(x_bounds) // 2)),
                ((sum(y_bounds) // 2), y_bounds[1]),
                (z_bounds[0], (sum(z_bounds) // 2))
            ),
            self.to_octree(
                ((sum(x_bounds) // 2), x_bounds[1]),
                ((sum(y_bounds) // 2), y_bounds[1]),
                (z_bounds[0], (sum(z_bounds) // 2))
            ),
            self.to_octree(
                (x_bounds[0], (sum(x_bounds) // 2)),
                (y_bounds[0], (sum(y_bounds) // 2)),
                ((sum(z_bounds) // 2), z_bounds[1])
            ),
            self.to_octree(
                ((sum(x_bounds) // 2), x_bounds[1]),
                (y_bounds[0], (sum(y_bounds) // 2)),
                ((sum(z_bounds) // 2), z_bounds[1])
            ),
            self.to_octree(
                (x_bounds[0], (sum(x_bounds) // 2)),
                ((sum(y_bounds) // 2), y_bounds[1]),
                ((sum(z_bounds) // 2), z_bounds[1])
            ),
            self.to_octree(
                ((sum(x_bounds) // 2), x_bounds[1]),
                ((sum(y_bounds) // 2), y_bounds[1]),
                ((sum(z_bounds) // 2), z_bounds[1])
            )
            # new cube * 8
        ]

        # Worldroot is an array not a cube
        if x_bounds[0] == 0 and x_bounds[1] == self.size:
            return [cube.newcube() if x is None else x for x in current_level_cubes]
        elif all([x is None for x in current_level_cubes]):
            # If they're all empty, return
            return None
        else:
            # Some of them are non-empty, replace the others with empty cubes.
            c = cube.newcube()
            c.children = [cube.newcube() if x is None else x for x in current_level_cubes]
            c.octsav = OCT.OCTSAV_CHILDREN.value
            return c
