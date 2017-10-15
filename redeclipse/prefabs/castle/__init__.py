import os

from redeclipse.prefabs.magica import MagicaRoom
from redeclipse.vector.orientations import EAST, SOUTH, ABOVE, WEST, NORTH, NORTHWEST, NORTHEAST, SOUTHWEST, SOUTHEAST
from redeclipse.prefabs import LIGHTMAN


class castle_gate(MagicaRoom):
    name = 'castle_gate'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_gate.vox')
    room_type = 'setpiece_medium'

    doors = [
        {'orientation': WEST, 'offset': WEST + NORTH + ABOVE},
        {'orientation': EAST, 'offset': EAST + EAST + EAST + NORTH + ABOVE},
        {'orientation': NORTH, 'offset': EAST + NORTH + NORTH + NORTH},
        {'orientation': SOUTH, 'offset': EAST + SOUTH},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + (EAST + NORTH).rotate(self.orientation))
        LIGHTMAN.light(xmap, self.pos + (EAST + NORTH + ABOVE).rotate(self.orientation))


class castle_gate_simple(MagicaRoom):
    name = 'castle_gate_simple'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_gate_simple.vox')
    room_type = 'setpiece_medium'

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST + EAST + EAST + ABOVE},
        {'orientation': NORTH, 'offset': EAST + NORTH},
        {'orientation': SOUTH, 'offset': EAST + SOUTH},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + (EAST + NORTH).rotate(self.orientation))
        LIGHTMAN.light(xmap, self.pos + (EAST + NORTH + ABOVE).rotate(self.orientation))


class castle_large(MagicaRoom):
    name = 'castle_large'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_large.vox')
    room_type = 'setpiece_large'

    doors = [
        {'orientation': WEST, 'offset': WEST + (NORTH * 2) + ABOVE},
        {'orientation': EAST, 'offset': (EAST * 5) + (NORTH * 2) + ABOVE},
        {'orientation': NORTH, 'offset': (NORTH * 5) + ABOVE + (EAST * 2)},
        {'orientation': SOUTH, 'offset': SOUTH + ABOVE + (EAST * 2)},
    ]

    def render_extra(self, world, xmap):
        large_center = EAST + NORTH + EAST + NORTH
        LIGHTMAN.light(xmap, self.pos + (large_center).rotate(self.orientation), size_factor=2)
        LIGHTMAN.light(xmap, self.pos + (large_center + ABOVE).rotate(self.orientation), size_factor=2)
        LIGHTMAN.light(xmap, self.pos + (large_center + ABOVE + ABOVE).rotate(self.orientation), size_factor=1.5)

        LIGHTMAN.light(xmap, self.pos + (large_center + NORTHWEST + ABOVE + ABOVE).rotate(self.orientation), size_factor=1.5)
        LIGHTMAN.light(xmap, self.pos + (large_center + SOUTHWEST + ABOVE + ABOVE).rotate(self.orientation), size_factor=1.5)
        LIGHTMAN.light(xmap, self.pos + (large_center + NORTHEAST + ABOVE + ABOVE).rotate(self.orientation), size_factor=1.5)
        LIGHTMAN.light(xmap, self.pos + (large_center + SOUTHEAST + ABOVE + ABOVE).rotate(self.orientation), size_factor=1.5)

        LIGHTMAN.light(xmap, self.pos + (large_center + NORTH + NORTH + ABOVE).rotate(self.orientation), size_factor=1.5)
        LIGHTMAN.light(xmap, self.pos + (large_center + SOUTH + SOUTH + ABOVE).rotate(self.orientation), size_factor=1.5)
        LIGHTMAN.light(xmap, self.pos + (large_center + EAST + EAST + ABOVE).rotate(self.orientation), size_factor=1.5)
        LIGHTMAN.light(xmap, self.pos + (large_center + WEST + WEST + ABOVE).rotate(self.orientation), size_factor=1.5)


class castle_small_deis(MagicaRoom):
    name = 'castle_small_deis'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_small_deis.vox')
    room_type = 'setpiece_small'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': EAST, 'offset': EAST},
        {'orientation': NORTH, 'offset': NORTH},
        {'orientation': SOUTH, 'offset': SOUTH},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos)


class castle_wall_corner(MagicaRoom):
    name = 'castle_wall_corner'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_wall_corner.vox')
    room_type = 'hallway'

    doors = [
        {'orientation': WEST, 'offset': WEST},
        {'orientation': SOUTH, 'offset': SOUTH},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos)


class castle_wall_end_cliff(MagicaRoom):
    name = 'castle_wall_end_cliff'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_wall_end_cliff.vox')
    room_type = 'endcap'

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)


class castle_wall_entry(MagicaRoom):
    name = 'castle_wall_entry'
    room_type = 'stair'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_wall_entry.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST + ABOVE + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE + ABOVE)


class castle_wall_section(MagicaRoom):
    name = 'castle_wall_section'
    room_type = 'hallway'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_wall_section.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)


class castle_wall_section_endcap(MagicaRoom):
    name = 'castle_wall_section_endcap'
    room_type = 'endcap'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_wall_section_endcap.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)
        LIGHTMAN.light(xmap, self.pos + (EAST + EAST + ABOVE).rotate(self.orientation))


class castle_wall_section_long(MagicaRoom):
    name = 'castle_wall_section_long'
    room_type = 'hallway'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_wall_section_long.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST * 3 + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)
        LIGHTMAN.light(xmap, self.pos + (EAST + EAST + ABOVE).rotate(self.orientation))


class castle_wall_section_long_damaged(MagicaRoom):
    name = 'castle_wall_section_long_damaged'
    room_type = 'hallway_setpiece'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_wall_section_long_damaged.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST * 3 + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)
        LIGHTMAN.light(xmap, self.pos + (EAST + EAST + ABOVE).rotate(self.orientation))


class castle_wall_section_tjoint(MagicaRoom):
    name = 'castle_wall_section_tjoint'
    room_type = 'hallway'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_wall_section_tjoint.vox')

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST * 3 + ABOVE},
        {'orientation': NORTH, 'offset': EAST + NORTH + NORTH + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)
        LIGHTMAN.light(xmap, self.pos + (EAST + EAST + ABOVE).rotate(self.orientation))


class castle_wall_tower(MagicaRoom):
    name = 'castle_wall_tower'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'castle_wall_tower.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST + ABOVE},
        {'orientation': NORTH, 'offset': NORTH + ABOVE},
        {'orientation': SOUTH, 'offset': SOUTH + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)


class wooden_bridge(MagicaRoom):
    name = 'wooden_bridge'
    vox_file = os.path.abspath(__file__).replace('__init__.py', 'wooden_bridge.vox')
    room_type = 'hallway_setpiece'

    doors = [
        {'orientation': WEST, 'offset': WEST + ABOVE},
        {'orientation': EAST, 'offset': EAST * 3 + ABOVE},
    ]

    def render_extra(self, world, xmap):
        LIGHTMAN.light(xmap, self.pos + ABOVE)
        LIGHTMAN.light(xmap, self.pos + (EAST + EAST + ABOVE).rotate(self.orientation))
