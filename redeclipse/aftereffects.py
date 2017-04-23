import sys
import random
from tqdm import tqdm
from redeclipse.objects import cube
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def vertical_gradient(x, y, z):
    return 1 - (z / 256)


def vertical_gradient2(x, y, z):
    result = 1.004742 - 0.0002448721 * z - 0.00001396083 * z * z
    if result < 0:
        result = 0
    if result > 1:
        result = 1
    return result


def vertical_gradient2inv(x, y, z):
    return 1 - vertical_gradient2(x, y, z)


def decay(world, position_function):
    log.info('Applying Decay Effect')
    for z in tqdm(range(world.heighest_point)):
        for x in range(world.size):
            for y in range(world.size):
                if random.random() > position_function(x, y, z):
                    # sys.stdout.write('.')
                    world.del_point(x, y, z)
                # else:
                    # pass
                    # sys.stdout.write('|')


def growth(world, position_function):
    log.info('Applying Growth Effect')
    for z in tqdm(range(world.heighest_point)):
        for x in range(world.size):
            for y in range(world.size):
                if random.random() > position_function(x, y, z):
                    if not world.get_point(x, y, z):
                        world.set_point(
                            x, y, z,
                            cube.newtexcube(tex=2)
                        )
