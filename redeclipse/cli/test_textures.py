#!/usr/bin/env python
import argparse
import random
import logging
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse, weighted_choice
from redeclipse.entities import Sunlight
from redeclipse import prefabs as p
from redeclipse.upm import UnusedPositionManager
from redeclipse.skybox import MinecraftSky
from tqdm import tqdm
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mpz_in, mpz_out, size=2**7, seed=42, rooms=200, debug=False):
    random.seed(seed)
    mymap = parse(mpz_in.name)
    v = VoxelWorld(size=size)

    b = p.SpawnRoom(pos=(8, 8, 8), orientation="+y")
    b.render(v, mymap)

    sunlight = Sunlight(
        red=128,
        green=128,
        blue=128,
        offset=45, # top
    )
    mymap.ents.append(sunlight)

    from redeclipse.aftereffects import grid, decay, gradient3, box
    grid(v, size=48)
    decay(v, gradient3)
    # box(v)

    # Emit config + textures
    p.TEXMAN.emit_conf(mpz_out)
    p.TEXMAN.copy_data()
    # mymap.skybox(MinecraftSky('/home/hxr/games/redeclipse-1.5.3/'))

    # Standard code to render octree to file.
    mymap.world = v.to_octree()
    mymap.world[0].octsav = 0
    mymap.write(mpz_out.name)


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
