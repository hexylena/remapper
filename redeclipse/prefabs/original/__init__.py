import os
from redeclipse.prefabs import LIGHTMAN
from redeclipse.prefabs import TEXMAN
from redeclipse.prefabs.magica import MagicaRoom
from redeclipse.vector.orientations import EAST, SOUTH, ABOVE, WEST, NORTH

# p.SpawnRoom, p.Room, p.NLongCorridor, p.Corridor2way,
# p.JumpCorridor3, p.JumpCorridorVertical, p.Corridor4way, p.PoleRoom,
# p.ImposingBlockRoom, p.JumpCorridorVerticalCenter, p.PlusPlatform,
# p.FlatSpace, p.Stair, p.DigitalRoom, p.DoricTemple,
# p.ImposingRingRoom, p.ImposingBlockRoom,


class spawn_room(MagicaRoom):
    name = 'spawn_room'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'spawn_room.vox')
    room_type = 'platform_setpiece'

    doors = [
        {'orientation': EAST, 'offset': EAST},
    ]

    def initialize_textures(self):
        self._wall = TEXMAN.get_c('wall')
        self._accent = TEXMAN.get_c('accent')
        self._floor = TEXMAN.get_c('floor')

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos)

    def colour_to_texture(self, r, g, b):
        r1 = int(r * 255)
        g1 = int(g * 255)
        b1 = int(b * 255)

        if (r1, g1, b1) == (50, 50, 50):
            return self._wall
        elif (r1, g1, b1) == (255, 255, 0):
            return self._accent
        else:
            return self._floor
