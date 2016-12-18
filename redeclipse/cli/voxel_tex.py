#!/usr/bin/env python
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.objects import cube, cubext, SurfaceInfo
from redeclipse.cli.show_cubes import show_cubes
import argparse
import simplejson as json
# import random

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('input', help='Input .mpz file')
    parser.add_argument('output', help='Output .mpz file')
    args = parser.parse_args()

    mymap = parse(args.input)
    v = VoxelWorld(size=2**3)

    v.set_point(3, 3, 3, cube.newtexcube(tex=[3, 4, 5, 6, 7, 8]))

    mymap.world = v.to_octree()
    mymap.world[0].octsav = 0

    show_cubes(mymap.world, simple=False)
    # print(json.dumps(mymap.to_dict()['world'], iterable_as_array=True))

    mymap.write(args.output)
