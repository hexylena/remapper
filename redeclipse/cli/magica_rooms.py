#!/usr/bin/env python
import argparse
import random
import logging

from redeclipse import prefabs
# We must override this ASAP since everyone else (e.g. prefabs) also imports the TEXMAN from prefab.
# from redeclipse.textures import DefaultThemedTextureManager, PrimaryThemedTextureManager, RainbowPukeTextureManager
# prefabs.TEXMAN = RainbowPukeTextureManager()
# Back to our normally scheduled imports.
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.entities import Sunlight
from redeclipse.upm import UnusedPositionManager
from redeclipse.magicavoxel.writer import to_magicavoxel
from redeclipse.prefabs import STARTING_POSITION
from redeclipse.prefabs import castle, dungeon, spacestation, original

from redeclipse.vector.orientations import EAST

from tqdm import tqdm
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mpz_in, mpz_out, size=2**8, seed=42, rooms=200, debug=False, magica=None):
    random.seed(seed)
    mymap = parse(mpz_in.name)
    v = VoxelWorld(size=size)

    possible_rooms = [
        # # Original
        original.spawn_room,
        # # Castle
        # castle.castle_gate, castle.castle_gate_simple,
        castle.castle_large, castle.castle_wall_corner,
        castle.castle_wall_end_cliff, castle.castle_wall_entry,
        castle.castle_wall_section, castle.castle_wall_section_long,
        castle.castle_wall_section_long_damaged,
        castle.castle_wall_section_tjoint, castle.castle_wall_tower,
        castle.wooden_bridge,
        # # Dungeon
        # dungeon.dungeon_2x2, dungeon.dungeon_junction, dungeon.dungeon_stair2,
        # dungeon.dungeon_walkway, dungeon.dungeon_walkway3,
        # # Space
        # spacestation.station_tube1, spacestation.station_tube3, spacestation.station_tube_jumpx,
        # spacestation.station_tubeX, spacestation.station_endcap, spacestation.station_right, spacestation.station_ring,
        # spacestation.station_ring_vertical, spacestation.station_sphere, spacestation.station_sphere_slice,
        # spacestation.station_stair2,
    ]

    possible_endcaps = [castle.castle_wall_end_cliff, castle.castle_wall_section_endcap]

    # Initialize
    upm = UnusedPositionManager(size, mirror=4)

    # Insert a starting room. We move it vertically downward from center since
    # we have no way to build stairs downwards yet.
    # We use the spawn room as our base starting room
    Room = castle.castle_small_deis
    b = Room(pos=STARTING_POSITION, orientation=EAST)
    [m.render(v, mymap) for m in upm.register_room(b)]
    # Convert rooms to int
    rooms = int(rooms)
    sunlight = Sunlight(
        red=128,
        green=128,
        blue=128,
        offset=45,  # top
    )
    mymap.ents.append(sunlight)
    upm.place_rooms(v, mymap, debug, possible_rooms, rooms=rooms)

    # Apply endcaps
    for room in upm.endcap(debug=debug, possible_endcaps=possible_endcaps):
        room.render(v, mymap)

    # from redeclipse.aftereffects import box_outline
    # box_outline(v, height=48)

    # Emit config + textures
    # mymap.skybox(MinecraftSky('/home/hxr/games/redeclipse-1.5.3/'))

    if magica:
        to_magicavoxel(v, magica, prefabs.TEXMAN)

    if mpz_out:
        prefabs.TEXMAN.emit_conf(mpz_out)
        prefabs.TEXMAN.copy_data()

        mymap.world = v.to_octree()
        mymap.world[0].octsav = 0
        mymap.write(mpz_out.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('mpz_in', type=argparse.FileType('r'), help='Input .mpz file')
    parser.add_argument('--mpz_out', type=argparse.FileType('w'), help='Output .mpz file')

    parser.add_argument('--magica', type=argparse.FileType('wb'), help='Output .vox file')

    parser.add_argument('--size', default=2**8, type=int, help="World size. Danger!")
    parser.add_argument('--seed', default=42, type=int, help="Random seed")
    parser.add_argument('--rooms', default=200, type=int, help="Number of rooms to place")
    parser.add_argument('--debug', action='store_true', help="Debugging")
    args = parser.parse_args()
    main(**vars(args))
