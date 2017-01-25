#!/usr/bin/env python
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.prefabs import BaseRoom, AltarRoom, Corridor
import argparse
import sys # noqa
import random # noqa
import math # noqa
import noise # noqa
random.seed(22)

IJ_SIZE = 2**7
K_SIZE = 50
MAP_SEED = 0

octaves = 1
noise_scaling = 32
# import random

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('input', help='Input .mpz file')
    parser.add_argument('output', help='Output .mpz file')
    args = parser.parse_args()

    mymap = parse(args.input)
    v = VoxelWorld(size=2**7)
    # Divide world into 2**3 sections
    # So each room has 2**4 to work with
    BaseRoom.render(v, mymap, pos=(0, 0, 0))
    Corridor.render(v, mymap, pos=(16, 16, 16), orientation='y', roof=True)
    Corridor.render(v, mymap, pos=(16, 24, 16), orientation='y', roof=True)
    AltarRoom.render(v, mymap, pos=(16, 32, 16))

    mymap.world = v.to_octree()
    mymap.world[0].octsav = 0
    mymap.write(args.output)
