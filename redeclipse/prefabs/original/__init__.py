import os
from redeclipse.entities import PlayerSpawn
from redeclipse.prefabs import LIGHTMAN
from redeclipse.prefabs import TEXMAN
from redeclipse.prefabs.magica import MagicaRoom
from redeclipse.vector import FineVector
from redeclipse.vector.orientations import EAST, SOUTH, ABOVE, WEST, NORTH, TILE_CENTER

# p.Room, p.NLongCorridor, p.Corridor2way,
# p.JumpCorridor3, p.JumpCorridorVertical, p.Corridor4way, p.PoleRoom,
# p.ImposingBlockRoom, p.JumpCorridorVerticalCenter, p.PlusPlatform,
# p.FlatSpace, p.Stair, p.DigitalRoom, p.DoricTemple,
# p.ImposingRingRoom, p.ImposingBlockRoom,


class OriginalRoom(MagicaRoom):
    colour_map = {
        (0, 0, 0): TEXMAN.get_c('floor'),
    }

    def colour_to_texture(self, r, g, b):
        r1 = int(r * 255)
        g1 = int(g * 255)
        b1 = int(b * 255)

        if (r1, g1, b1) not in self.colour_map:
            r1 = 0
            g1 = 0
            b1 = 0

        return getattr(self, '_' + self.colour_map[(r1, g1, b1)])


class spawn_room(OriginalRoom):
    name = 'spawn_room'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'spawn_room.vox')
    room_type = 'platform_setpiece'

    doors = [
        {'orientation': EAST, 'offset': EAST},
    ]

    colour_map = {
        (50, 50, 50): 'wall',
        (255, 255, 0): 'accent',
        (0, 0, 0): 'floor',
    }

    def initialize_textures(self):
        self._wall = TEXMAN.get_c('wall')
        self._accent = TEXMAN.get_c('accent')
        self._floor = TEXMAN.get_c('floor')

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos)

        xmap.ents.append(PlayerSpawn(
            xyz=self.pos + TILE_CENTER + FineVector(0, 0, 1)
        ))
