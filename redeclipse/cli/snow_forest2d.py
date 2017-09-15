#!/usr/bin/env python
import sys # noqa
import random # noqa
import math # noqa
import noise # noqa
from PIL import Image
from tqdm import tqdm

random.seed(22)
IJ_SIZE = 2**6
WORLD_SIZE = 2**9
K_SIZE = 50
MAP_SEED = 0
OVERALL_SCALING = 1

octaves = 1
noise_scaling = 32


def point_height(i, j, k):
    q = noise.pnoise2(
        0.3 * i / noise_scaling,
        0.7 * j / noise_scaling,
        octaves=octaves, base=MAP_SEED
    )
    q *= 25
    q += 60
    return q


def point(i, j):
    wide_area = noise.pnoise2(
        OVERALL_SCALING * 2.1 * i / noise_scaling,
        OVERALL_SCALING * 1.1 * j / noise_scaling,
        octaves=octaves, base=MAP_SEED
    )
    if wide_area < -0.1:
        wide_area = 0
    else:
        wide_area = 1

    local_distribution = noise.pnoise2(
        OVERALL_SCALING * 26.9 * i / noise_scaling,
        OVERALL_SCALING * 23.1 * j / noise_scaling,
        octaves=octaves, base=MAP_SEED
    )
    if 0.2 < local_distribution < 0.25:
        local_distribution = 1
    else:
        local_distribution = 0

    q = (local_distribution & wide_area) * 200
    return q


def main():
    img = Image.new('RGB', (WORLD_SIZE, WORLD_SIZE), "black")  # create a new black image
    pixels = img.load()
    # im.putdata([(255,0,0), (0,255,0), (0,0,255)])

    for i in tqdm(range(WORLD_SIZE)):
        for j in range(WORLD_SIZE):
            q = int(point(i, j))
            pixels[(i, j)] = (q, q, q)

    img.save('out.png')


if __name__ == '__main__':
    main()
