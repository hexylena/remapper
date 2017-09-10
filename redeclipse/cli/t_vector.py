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
#from redeclipse.skybox import MinecraftSky
from redeclipse.vector import CoarseVector, FineVector
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mpz_in, mpz_out, size=2**7, seed=42, rooms=200, debug=False):
    random.seed(seed)
    mymap = parse(mpz_in.name)
    v = VoxelWorld(size=size)
    upm = UnusedPositionManager(size, mirror=True)

    Room = p.DigitalRoom

    kwargs = Room.randOpts(None)
    n = Room(pos=CoarseVector(8 + 5, 8, 8), orientation='+x', **kwargs)
    kwargs = Room.randOpts(None)
    s = Room(pos=CoarseVector(8 - 5, 8, 8), orientation='-x', **kwargs)
    kwargs = Room.randOpts(None)
    e = Room(pos=CoarseVector(8, 8 + 5, 8), orientation='+y', **kwargs)
    kwargs = Room.randOpts(None)
    w = Room(pos=CoarseVector(8, 8 - 5, 8), orientation='-y', **kwargs)

    upm.register_room(n)
    upm.register_room(s)
    upm.register_room(e)
    upm.register_room(w)

    sp = p.SpawnRoom(pos=CoarseVector(8 + 2, 8, 8), orientation='+x', randflags=[True])
    upm.register_room(sp)
    sp.render(v, mymap)
    n.render(v, mymap)
    s.render(v, mymap)
    e.render(v, mymap)
    w.render(v, mymap)

    from redeclipse.objects import cube
    for i in range(8):
        for j in range(8):
            v.set_pointv(
                CoarseVector(8 + 5, 8, 12) + FineVector(i, j, 0),
                cube.newtexcube(tex=1)
            )


    sunlight = Sunlight(
        red=128,
        green=128,
        blue=128,
        offset=45, # top
    )
    mymap.ents.append(sunlight)

    # from redeclipse.aftereffects import endcap
    # endcap(v, upm)

    # Emit config + textures
    p.TEXMAN.emit_conf(mpz_out)
    p.TEXMAN.copy_data()

    with open('out.vox', 'wb') as handle:
        to_magicavoxel(v, handle)
    # Standard code to render octree to file.
    # mymap.world = v.to_octree()
    # mymap.world[0].octsav = 0
    # mymap.write(mpz_out.name)


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
