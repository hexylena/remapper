#!/usr/bin/env python
import argparse
import random
import logging
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.entities import Sunlight
from redeclipse import prefabs as p
from redeclipse.upm import UnusedPositionManager
from redeclipse.magicavoxel.writer import to_magicavoxel
from redeclipse.prefabs import STARTING_POSITION, TEXMAN

from redeclipse.vector.orientations import EAST
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mpz_in, mpz_out, size=2**7, seed=42, rooms=200, debug=False, magica=None):
    random.seed(seed)
    mymap = parse(mpz_in.name)
    v = VoxelWorld(size=size)

    possible_rooms = [
        p.SpawnRoom,
        p.Room,
        p.NLongCorridor,
        p.Corridor2way,
        p.JumpCorridor3,
        p.JumpCorridorVertical,
        p.Corridor4way,
        p.PoleRoom,
        p.ImposingBlockRoom,
        p.JumpCorridorVerticalCenter,
        p.PlusPlatform,
        p.FlatSpace,
        p.Stair,
        p.DigitalRoom,
        p.DoricTemple,
        p.ImposingRingRoom,
        p.ImposingBlockRoom,
    ]
    possible_endcaps = [p.SpawnRoom]
    # Initialize
    upm = UnusedPositionManager(size, mirror=4)

    # Insert a starting room. We move it vertically downward from center since
    # we have no way to build stairs downwards yet.
    # We use the spawn room as our base starting room
    Room = possible_rooms[0]
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

    # TODO: This isn't called correctly
    upm.place_rooms(v, mymap, debug, rooms=rooms)

    # Apply endcaps
    for room in upm.endcap(debug=debug, possible_endcaps=possible_endcaps):
        room.render(v, mymap)

    # from redeclipse.aftereffects import grid, decay, gradient3, box
    # grid(v, size=48)
    # decay(v, gradient3)
    # box(v)

    # Emit config + textures
    TEXMAN.emit_conf(mpz_out)
    TEXMAN.copy_data()
    # mymap.skybox(MinecraftSky('/home/hxr/games/redeclipse-1.5.3/'))

    # Standard code to render octree to file.

    if magica:
        to_magicavoxel(v, magica, TEXMAN)
        print('voxel')

    mymap.world = v.to_octree()
    mymap.world[0].octsav = 0
    mymap.write(mpz_out.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('mpz_in', type=argparse.FileType('r'), help='Input .mpz file')
    parser.add_argument('mpz_out', type=argparse.FileType('w'), help='Output .mpz file')

    parser.add_argument('--magica', type=argparse.FileType('w'), help='Output .vox file')

    parser.add_argument('--size', default=2**8, type=int, help="World size. Danger!")
    parser.add_argument('--seed', default=42, type=int, help="Random seed")
    parser.add_argument('--rooms', default=200, type=int, help="Number of rooms to place")
    parser.add_argument('--debug', action='store_true', help="Debugging")
    args = parser.parse_args()
    main(**vars(args))
