import os

from redeclipse.textures import AutomatedMagicaTextureManager
from redeclipse.prefabs import Room, TEXMAN
from redeclipse.magicavoxel.reader import Magicavoxel
from redeclipse.voxel import VoxelWorld
from redeclipse.vector import FineVector
from redeclipse.vector.orientations import SELF, EAST, SOUTH, ABOVE, WEST, NORTH


class MagicaRoom(Room):

    vox_file = None

    def __repr__(self):
        return '<MagicRoom %s ori%s>' % (self.name, self.orientation)

    def load_model(self):
        """
        The 'false' init method that builds an in-memory room class based on
        the magica voxel model.

        :param str vox: path to a .vox file

        The yaml file is more or less undocumented so far.
        """
        self.model = Magicavoxel.from_file(self.vox_file)
        self.vox = VoxelWorld()
        self._colours = {}
        for vox in self.model.model_voxels.voxels:
            self.vox.set_point(vox.x, vox.y, vox.z, vox.c)
            # For every colour in the palette, register it with the current
            # class's colour atlas (non-global colour atlas).
            for idx, colour in enumerate(self.model.palette.colours):
                self._colours[idx] = (colour.r / 255, colour.g / 255, colour.b / 255)

        self.__doors = []
        for door in self.doors:
            self.__doors.append(door)

        # Occupied positions are automatically calculated
        self.__positions = []

        x_dims = (self.vox.xmax - self.vox.xmin) // 8
        y_dims = (self.vox.ymax - self.vox.ymin) // 8
        z_dims = (self.vox.zmax - self.vox.zmin) // 8

        for i in range(x_dims + 1):
            for j in range(y_dims + 1):
                for k in range(z_dims + 1):
                    self.__positions.append(
                        (EAST * i) + (SOUTH * j) + (ABOVE * k)
                    )

    def _get_doorways(self):
        if not hasattr(self, 'model'):
            self.load_model(self.vox_file)
        return self.__doors

    def _get_positions(self):
        if not hasattr(self, 'model'):
            self.load_model(self.vox_file)
        return self.__positions

    def render_extra(self, world, xmap):
        self.light(xmap)

    def render(self, world, xmap):
        """
        Render the magic room to the world.
        """
        if not hasattr(self, 'model'):
            self.load_model(self.vox_file)

        for v in self.vox.world:
            (r, g, b) = self._colours[self.vox.world[v]]
            c = TEXMAN.get_colour(r, g, b)
            self.x('cube', world, SELF + FineVector(*v), tex=c)

        self.render_extra(world, xmap)


class castle_gate(MagicaRoom):
    vox_file = os.path.abspath(__file__).replace('.py', '.vox')
    name = 'castle_gate'
    room_type = 'oriented'
    doors = [
        WEST + ABOVE,
        EAST + EAST + EAST + ABOVE,
        EAST + NORTH,
        EAST + SOUTH
    ]
