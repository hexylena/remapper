#!/usr/bin/env python
import argparse
import random
import logging

from redeclipse import prefabs
# We must override this ASAP since everyone else (e.g. prefabs) also imports the TEXMAN from prefab.
# from redeclipse.textures import DefaultThemedTextureManager, PrimaryThemedTextureManager, RainbowPukeTextureManager
# prefabs.TEXMAN = RainbowPukeTextureManager()
# Back to our normally scheduled imports.
prefabs.LIGHTMAN.brightness = 0.3
from redeclipse.cli import parse, output, output_args
from redeclipse.entities import Sunlight
from redeclipse.prefabs import STARTING_POSITION
from redeclipse.prefabs import castle, dungeon, spacestation, original, egypt  # noqa
from redeclipse.upm import UnusedPositionManager
from redeclipse.vector.orientations import EAST
from redeclipse.voxel import VoxelWorld
import redeclipse.worldflavors

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mpz_in, size=2**8, seed=42, rooms=200, debug=False, ctf=False, mirror=2, flavor=None, **kwargs):
    random.seed(seed)
    mymap = parse(mpz_in.name)
    v = VoxelWorld(size=size)
    # Update with chosen world flavouring
    mymap = redeclipse.worldflavors.update(mymap, flavor)

    possible_rooms = [
        # # Original
        # original.spawn_room,
        # # Castle
        # castle.castle_gate, castle.castle_gate_simple,
        # castle.castle_large,

        # castle.castle_wall_corner,
        # castle.castle_wall_end_cliff, castle.castle_wall_entry,
        # castle.castle_wall_section, castle.castle_wall_section_long,
        # castle.castle_wall_section_long_damaged,
        # castle.castle_wall_section_tjoint,
        # castle.castle_wall_section_x,
        # castle.castle_wall_tower,
        # castle.wooden_bridge,

        # # Dungeon
        # dungeon.dungeon_2x2, dungeon.dungeon_junction, dungeon.dungeon_stair2,
        # dungeon.dungeon_walkway, dungeon.dungeon_walkway3,

        # # Space
        # spacestation.station_right,
        # spacestation.station_ring,
        # spacestation.station_ring_vertical,
        # spacestation.station_sbend,
        # spacestation.station_sphere,
        # spacestation.station_sphere_slice,
        # spacestation.station_stair2,
        # spacestation.station_tube1,
        # spacestation.station_tube3,
        # spacestation.station_tube3layered,
        # spacestation.station_tube_jumpx,
        # spacestation.station_tubeX,
        # spacestation.station_tubeX_variant,
        # spacestation.station_uturn,
        egypt.house_2x2,
        egypt.house_2x2x3,
        egypt.stair,
        egypt.stair_toplatform,
        egypt.gate,
        egypt.statue,
        egypt.statue_cat,
    ]

    # possible_endcaps = [castle.castle_wall_end_cliff, castle.castle_wall_section_endcap]
    # possible_endcaps = [spacestation.station_endcap]
    possible_endcaps = [egypt.statue_cat]

    # Initialize
    upm = UnusedPositionManager(size, mirror=mirror)

    # Insert a starting room. We move it vertically downward from center since
    # we have no way to build stairs downwards yet.
    # We use the spawn room as our base starting room
    if ctf:
        # Room = castle.castle_flag_room
        Room = spacestation.station_flagroom
    else:
        Room = spacestation.station_tubeX

    b = Room(pos=STARTING_POSITION, orientation=EAST)
    upm.register_room(b)

    # Convert rooms to int
    rooms = int(rooms)
    sunlight = Sunlight(
        red=128,
        green=128,
        blue=128,
        offset=45,  # top
    )
    mymap.ents.append(sunlight)

    # Place all rooms
    upm.place_rooms(debug, possible_rooms, rooms=rooms)
    # Apply endcaps
    upm.endcap(debug=debug, possible_endcaps=possible_endcaps)

    # Now we get around to actually rendering the rooms, allowing us to do
    # modifications to their models before we render to our VoxelWorld.
    for room in upm.rooms:
        room.render(v, mymap)

    # from redeclipse.aftereffects import box_outline
    # box_outline(v, height=48)

    # Emit config + textures
    # mymap.skybox(MinecraftSky('/home/hxr/games/redeclipse-1.5.3/'))
    return v, mymap, upm


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('mpz_in', type=argparse.FileType('r'), help='Input .mpz file')
    # Add output arguments
    output_args(parser)

    parser.add_argument('--size', default=2**8, type=int, help="World size. Danger!")
    parser.add_argument('--seed', default=42, type=int, help="Random seed")
    parser.add_argument('--rooms', default=200, type=int, help="Number of rooms to place")
    parser.add_argument('--debug', action='store_true', help="Debugging")
    parser.add_argument('--ctf', action='store_true', help="Include flags for CTFs")
    parser.add_argument('--mirror', type=int, choices=[1, 2, 4], help="Mirror mode (1 = unmirrored, 2 = 2-way mirroring, 4 = 4-way mirroring)")
    parser.add_argument('--flavor', nargs='*', choices=redeclipse.worldflavors.choices)
    args = parser.parse_args()
    # Build our map
    v, mymap, upm = main(**vars(args))
    # Save our map in whatever formats are requested.
    output(v, mymap, upm, prefabs, args)
