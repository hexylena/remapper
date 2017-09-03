import sys
import random
from tqdm import tqdm
import math
from redeclipse.objects import cube
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def vertical_gradient(x, y, z, slope=256):
    """
    Function representing a vertical gradient going from f(z=0) = 1,
    f(z=256) = 0 smoothly.

    :param x: x-coordinate to use in gradient generation
    :type x: int
    :param y: y-coordinate to use in gradient generation
    :type y: int
    :param z: x-coordinate to use in gradient generation
    :type z: int

    :returns: a float for that specific point.
    :rtype: float
    """
    if slope < 1:
        slope = 1
    return 1 - (z / slope)


def gradient3(x, y, z):
    """
    An experimental gradient that also varies only based on z-depth

    :param x: x-coordinate to use in gradient generation
    :type x: int
    :param y: y-coordinate to use in gradient generation
    :type y: int
    :param z: x-coordinate to use in gradient generation
    :type z: int

    :returns: a float for that specific point.
    :rtype: float
    """
    return 2 - (2 / (1 + math.pow(1.001, - z)))


def vertical_gradient2(x, y, z):
    """
    Yet another variant that provides a reasonable level of decay.

    :param x: x-coordinate to use in gradient generation
    :type x: int
    :param y: y-coordinate to use in gradient generation
    :type y: int
    :param z: x-coordinate to use in gradient generation
    :type z: int

    :returns: a float for that specific point.
    :rtype: float
    """
    result = 1.004742 - 0.0002448721 * z - 0.00001396083 * z * z
    if result < 0:
        result = 0
    if result > 1:
        result = 1
    return result


def vertical_gradient2inv(x, y, z):
    """
    Inverse of vertical_gradient2

    :param x: x-coordinate to use in gradient generation
    :type x: int
    :param y: y-coordinate to use in gradient generation
    :type y: int
    :param z: x-coordinate to use in gradient generation
    :type z: int

    :returns: a float for that specific point.
    :rtype: float
    """
    return 1 - vertical_gradient2(x, y, z)


def grid(world, size=24):
    """
    A grid effect applied to the world.

    :param world: Input world
    :type world: redeclipse.Map

    :param size: spacing between the grids
    :type size: int

    :rtype: None
    """
    log.info('Applying Grid Effect')
    def pos_func(x, y, z):
        return (x % size == 0 and y % size == 0) or \
                (z % size == 0 and y % size == 0) or \
                (z % size == 0 and x % size == 0)

    for z in tqdm(range(world.heighest_point)):
        for x in range(world.size):
            for y in range(world.size):
                if pos_func(x, y, z):
                    if not world.get_point(x, y, z):
                        world.set_point(
                            x, y, z,
                            cube.newtexcube(tex=2)
                        )


def decay(world, position_function):
    """
    A decay effect applied to the world. Decay at any specific point
    will occur when ``random.random() > position_function``.

    :param world: Input world
    :type world: redeclipse.Map

    :param position_function: Position function, as seen above in this module
    :type position_function: function

    :rtype: None
    """
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
    """
    Basically the opposite of decay. Apply SPARINGLY. Otherwise this
    will take forever to serialize and be completely non-functional.

    :param world: Input world
    :type world: redeclipse.Map

    :param position_function: Position function, as seen above in this module
    :type position_function: function

    :rtype: None
    """
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


def box(world):
    """
    A box added around the edge of the world.

    :param world: Input world
    :type world: redeclipse.Map

    :rtype: None
    """
    for z in tqdm(range(world.size)):
        for x in range(world.size):
            for y in range(world.size):
                if x == 0 or y == 0 or z == 0 or x == world.size - 1 or y == world.size - 1 or z == world.size - 1:
                    world.set_point(
                        x, y, z,
                        cube.newtexcube(tex=2)
                    )
