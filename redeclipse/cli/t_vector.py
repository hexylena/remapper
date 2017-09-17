#!/usr/bin/env python
import argparse
import random
import logging
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.entities import Sunlight
from redeclipse import prefabs as p
from redeclipse.upm import UnusedPositionManager
from redeclipse.magicavoxel import to_magicavoxel

from redeclipse.vector import CoarseVector, FineVector, AbsoluteVector
from redeclipse.vector.orientations import rotate_yaw, SELF, \
    SOUTH, NORTH, WEST, EAST, ABOVE, \
    ABOVE_FINE, NORTHWEST, \
    NORTHEAST, SOUTHWEST, SOUTHEAST, TILE_CENTER, HALF_HEIGHT
# from redeclipse.skybox import MinecraftSky
from redeclipse.vector import CoarseVector, FineVector
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mpz_in, mpz_out, size=2**7, seed=42, rooms=200, debug=False):
    random.seed(seed)
    mymap = parse(mpz_in.name)
    v = VoxelWorld(size=size)
    upm = UnusedPositionManager(size, mirror=True)

    # for room_type in ('Room', 'TestRoom', 'TestRoom', 'NLongCorridor', 'Corridor4way'):
    for room_type in ('TestRoom2',):
        print("Processing %s" % room_type)
        Room = getattr(p, room_type)

        n = Room(pos=CoarseVector(8, 8, 0), orientation=NORTH)
        # n.x('column', v, SOUTH + SOUTH, SOUTH, 8)
        # n.x('column', v, EAST + EAST, EAST, 8)
        # n.x('column', v, NORTH + NORTH, NORTH, 8)

        # s = Room(pos=CoarseVector(8 - 4, 8, 0), orientation='-x')
        # # e = Room(pos=CoarseVector(8, 8 + 4, 0), orientation='+x')
        # # w = Room(pos=CoarseVector(8, 8 - 4, 0), orientation='-x')

        # upm.register_room(n)
        # upm.register_room(s)
        # upm.register_room(e)
        # upm.register_room(w)

        n.render(v, mymap)
        n = Room(pos=CoarseVector(8, 4, 0), orientation=SOUTH)
        n.render(v, mymap)
        n = Room(pos=CoarseVector(8, 12, 0), orientation=NORTH)
        n.render(v, mymap)
        n.x('column', v, NORTH + NORTH, NORTH, 4, tex=p.TEXMAN.get('red'))
        n.x('column', v, NORTH + NORTH, EAST, 8, tex=p.TEXMAN.get('green'))
        n.x('column', v, NORTH + NORTH, SOUTH, 4, tex=p.TEXMAN.get('blue'))
        n.x('column', v, NORTH + NORTH, WEST, 8, tex=p.TEXMAN.get('yellow'))
        # s.render(v, mymap)
        # e.render(v, mymap)
        # w.render(v, mymap)

        from redeclipse.objects import cube
        for i in range(8):
            for j in range(8):
                v.set_pointv(
                    CoarseVector(8 + 5, 8, 3) + FineVector(i, j, 0),
                    cube.newtexcube(tex=1)
                )

        from redeclipse.aftereffects import box_outline
        box_outline(v, height=10)

        with open(room_type + '.vox', 'wb') as handle:
            to_magicavoxel(v, handle, p.TEXMAN)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('mpz_in', type=argparse.FileType('r'), help='Input .mpz file')
    parser.add_argument('mpz_out', type=argparse.FileType('w'), help='Output .mpz file')

    parser.add_argument('--size', default=2**8, type=int, help="World size. Danger!")
    parser.add_argument('--seed', default=42, type=int, help="Random seed")
    parser.add_argument('--rooms', default=200, type=int, help="Number of rooms to place")
    parser.add_argument('--debug', action='store_true', help="Debugging")
    args = parser.parse_args()
    main(**vars(args))
