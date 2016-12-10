"""
We can't work with octrees. Just... no.

So we work in a voxel world, and then convert this to an octree with the small
resolution cube that makes sense, and then let RE optimise the map when need be.
"""
from redeclipse.objects import cube


class VoxelWorld:

    def __init__(self, size=2**7):
        # Size defines number of cubes from left to right.
        self.size = size
        self.world = {}

    def set_point(self, x, y, z, data):
        self.world[x, y, z] = data

    def get_point(self, x, y, z):
        if (x, y, z) in self.world:
            return self.world[x, y, z]
        else:
            return None

    def to_octree(self,  x_bounds=None, y_bounds=None, z_bounds=None):
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
        if all([x is None for x in current_level_cubes]):
            return None
        elif x_bounds[0] == 0 and x_bounds[1] == self.size:
            return [cube.newcube() if x is None else x for x in current_level_cubes]
        else:
            c = cube.newcube()
            c.children = [cube.newcube() if x is None else x for x in current_level_cubes]
            return c
