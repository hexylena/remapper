#!/usr/bin/env python
from redeclipse.voxel import VoxelWorld
from redeclipse.entities.model import MapModel
from redeclipse.entities import PlayerSpawn
from redeclipse.cli import parse
from redeclipse.objects import cube
import argparse
import random
import noise
from tqdm import tqdm
random.seed(22)
IJ_SIZE = 2**8
WORLD_SIZE = 2**8
MAP_SEED = 0
OVERALL_SCALING = 2

octaves = 2
noise_scaling = 32


def _light_distribution(i, j, wan=0.2, ldist=0.215, wan_a=2.9, wan_b=1.1, lan_a=26.9, lan_b=23.1, LSEED=0):
    wide_area = noise.pnoise2(
        OVERALL_SCALING * wan_a * i / noise_scaling,
        OVERALL_SCALING * wan_b * j / noise_scaling,
        octaves=octaves, base=MAP_SEED + LSEED
    )
    if wide_area < wan:
        wide_area = 0
    else:
        wide_area = 1

    local_distribution = noise.pnoise2(
        OVERALL_SCALING * lan_a * i / noise_scaling,
        OVERALL_SCALING * lan_b * j / noise_scaling,
        octaves=octaves, base=MAP_SEED + LSEED
    )
    if 0.2 < local_distribution < ldist:
        local_distribution = 1
    else:
        local_distribution = 0

    return wide_area & local_distribution


def point_spawn(i, j):
    # Shift so we don't spawn *In* a tree.
    return _light_distribution(i + 1, j + 1)


def point_tree(i, j):
    return _light_distribution(i, j)


def point_rock(i, j):
    return _light_distribution(i, j, wan=0.275, ldist=0.210, LSEED=100)


def point_height(i, j):
    q = noise.pnoise2(
        0.3 * i / noise_scaling,
        0.7 * j / noise_scaling,
        octaves=octaves, base=MAP_SEED
    )
    q *= 15
    q += 60
    return q


def point_snow(i, j):
    q = noise.pnoise2(0.9 * j / noise_scaling, 0.7 * i / noise_scaling, octaves=octaves, base=MAP_SEED + 100)
    return q < 0


def main():
    parser = argparse.ArgumentParser(description='Snowy forest map')
    parser.add_argument('input', help='Input .mpz file')
    parser.add_argument('output', help='Output .mpz file')
    args = parser.parse_args()

    mymap = parse(args.input)
    v = VoxelWorld(size=WORLD_SIZE)

    heightmap = {}
    for i in tqdm(range(IJ_SIZE), leave=False, desc='Heightmap'):
        for j in range(IJ_SIZE):
            # These are not z-dependent
            height = int(point_height(i, j))
            heightmap[(i, j)] = height
            snow = point_snow(i, j)

            for k in range(height - 2, height):
                tex = 11
                if snow:
                    tex = 13

                v.set_point(i, j, k, cube.newtexcube(tex=tex))

                # # Border wall
                if i == 0 or j == 0 or i == IJ_SIZE - 1 or j == IJ_SIZE - 1:
                    for q in range(10):
                        v.set_point(i, j, k + q, cube.newtexcube(tex=tex))

    tree_count = 0
    for i in tqdm(range(IJ_SIZE), desc='Placing Entities'):
        for j in range(IJ_SIZE):
            if point_tree(i, j):
                tree_count += 1
                # Place tree
                tree = MapModel(
                    x=i * 4,
                    y=j * 4,
                    z=heightmap[(i, j)] * 4,
                    type=137,
                    yaw=random.randint(0, 360),
                    scale=random.randint(56, 200),
                )
                mymap.ents.append(tree)

            if point_spawn(i, j):
                spawn = PlayerSpawn(
                    x=i * 4,
                    y=j * 4,
                    z=heightmap[(i, j)] * 4,
                    team=0,
                    yaw=random.randint(0, 360),
                )
                mymap.ents.append(spawn)

            if point_rock(i, j):
                rock = MapModel(
                    x=i * 4,
                    y=j * 4,
                    z=heightmap[(i, j)] * 4 - random.randint(0, 5),
                    type=122,
                    yaw=random.randint(0, 360),
                    roll=random.randint(0, 360),
                    pitch=random.randint(0, 360),
                    scale=random.randint(56, 300),
                )
                mymap.ents.append(rock)

    mymap.world = v.to_octree()
    mymap.world[0].octsav = 0
    mymap.write(args.output)


if __name__ == '__main__':
    main()
