import os
import glob
import yaml
from redeclipse.magicavoxel.reader import Magicavoxel
from redeclipse.prefabs import Room
from redeclipse.vector import FineVector
from redeclipse.vector.orientations import SELF, NORTH, SOUTH, EAST, WEST, ABOVE, BELOW  # NOQA
from redeclipse.textures import AutomatedMagicaTextureManager
from redeclipse.voxel import VoxelWorld
PATH = os.path.abspath(os.path.dirname(__file__))
ROOMS = os.path.join(PATH, 'rooms')
TEXMAN = AutomatedMagicaTextureManager()


class MagicaRoom(Room):
    """
    A 'magic' room definition, it should be initialized with the voxel and yml
    files, but then re_initialized with the real room instantiation.
    """

    def re_init(self, pos, orientation=EAST, randflags=None):
        """
        instead of ``r = Stair(pos=...)``, this is called as::

            r = copy.copy(room_base)
            r.re_init(pos=...)

        it's a bit awkward but it work for now.
        """
        super().__init__(pos, orientation=orientation, randflags=randflags)

    def __repr__(self):
        return '<MagicRoom %s ori%s>' % (self.name, self.orientation)

    def __init__(self, yml, vox):
        """
        The 'false' init method that builds an in-memory room class based on
        the yml file and the magica voxel model.

        :param str yml: path to a yaml file documenting the room
        :param str vox: path to a .vox file

        The yaml file is more or less undocumented so far.
        """
        self.model = Magicavoxel.from_file(vox)
        self.vox = VoxelWorld()
        self._colours = {}
        for vox in self.model.model_voxels.voxels:
            self.vox.set_point(vox.x, vox.y, vox.z, vox.c)
            # For every colour in the palette, register it with the current
            # class's colour atlas (non-global colour atlas).
            for idx, colour in enumerate(self.model.palette.colours):
                self._colours[idx] = (colour.r / 255, colour.g / 255, colour.b / 255)

        with open(yml, 'r') as handle:
            data = yaml.load(handle)
            self.name = data['name']
            self.room_type = data['room_type']
            self.__doors = []
            for door in data['doors']:
                self.__doors.append(eval(door))

            # Occupied positions
            if data['occupied'] == 'autocalc':
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
        return self.__doors

    def _get_positions(self):
        return self.__positions

    def render(self, world, xmap):
        """
        Render the magic room to the world.

        TODO: broken colours/textures.
        """
        self.light(xmap)
        for v in self.vox.world:
            (r, g, b) = self._colours[self.vox.world[v]]
            c = TEXMAN.get_colour(r, g, b)
            self.x('cube', world, SELF + FineVector(*v), tex=c)


def autodiscover():
    """
    Automatically load yml/vox pairs from the module.
    """
    rooms = []
    for yml in glob.glob(os.path.join(ROOMS, '*.yml')):
        room_class = MagicaRoom(yml, yml.replace('.yml', '.vox'))
        rooms.append(room_class)
    return rooms
