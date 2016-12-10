#!/usr/bin/env python
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.objects import cube, cubext, SurfaceInfo
import argparse
# import random

def simplify(d):
    d['faces'] = d['faces'][0]
    if len(set(d['edges'])) == 1:
        d['edges'] = '%s * %s' % (len(d['edges']), d['edges'][0])

    if len(set(d['texture'])) == 1:
        d['texture'] = d['texture'][0]

    for k in list(d.keys()):
        if not d[k]:
            del d[k]
    return d

def show_cubes(m, indent=0):
    for c in m:
        print(('\t' * indent), 'CUBE', simplify(c.to_dict(children=False)))
        if c.children:
            show_cubes(c.children, indent=indent + 1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('input', help='Input .mpz file')
    parser.add_argument('output', help='Output .mpz file')
    args = parser.parse_args()

    mymap = parse(args.input)
    show_cubes(mymap.world)

    v = VoxelWorld(size=2**3)
    for i in range(0, 2**3):
        c = cube.newcube()
        # c.material = None
        # c.escaped = 0
        # c.set_solid()
        # c.visible = 0
        # c.edges = [128] * 12
        # c.children = []
        # c.texture = [2, 35, 60, 3, 27, 21]
        # c.ext = cubext()
        # c.ext.verts = 0
        # c.ext.surfaces = [
            # SurfaceInfo(2, 0, 0, 32),
            # SurfaceInfo(2, 0, 0, 32),
            # SurfaceInfo(2, 0, 0, 32),
            # SurfaceInfo(2, 0, 0, 32),
            # SurfaceInfo(2, 0, 0, 32),
            # SurfaceInfo(2, 0, 0, 32),
        # ]
        # c.octsav = 34
        # c.surfmask = 63
        # c.totalverts = 0
        v.set_point(i, i, i, c)

    mymap.world = v.to_octree()
    show_cubes(mymap.world)
    mymap.write(args.output)
