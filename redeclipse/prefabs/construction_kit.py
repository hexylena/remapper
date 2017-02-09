from redeclipse.objects import cube

def mv(a, b):
    return (
        a[0] + b[0],
        a[1] + b[1],
        a[2] + b[2],
    )

def mi(*args):
    if len(args) == 1:
        p0 = args[0][0]
        p1 = args[0][1]
        p2 = args[0][2]
    else:
        p0 = args[0]
        p1 = args[1]
        p2 = args[2]

    return (
        p0 * -1,
        p1 * -1,
        p2 * -1,
    )

def m(*args):
    if len(args) == 2:
        p0 = args[0][0]
        p1 = args[0][1]
        p2 = args[0][2]
    else:
        p0 = args[0]
        p1 = args[1]
        p2 = args[2]

    return (
        p0 * 8,
        p1 * 8,
        p2 * 8,
    )


def column_points(size, direction):
    for i in range(size):
        if direction in ('-x', '+x', 'x'):
            yield (i, 0, 0)
        elif direction in ('-y', '+y', 'y'):
            yield (0, i, 0)
        elif direction in ('-z', '+z', 'z'):
            yield (0, 0, i)


def wall_points(size, direction, limit_j=100, limit_i=100):
    for i in range(size):
        # Allow partial_j walls
        if i > limit_i:
            continue

        for j in range(size):
            # Allow partial_j walls
            if j > limit_j:
                continue

            if direction == '-z':
                yield (i, j, 0)
            elif direction == '+z':
                yield (i, j, size - 1)
            elif direction == '-y':
                yield (i, 0, j)
            elif direction == '+y':
                yield (i, size - 1, j)
            elif direction == '-x':
                yield (0, i, j)
            elif direction == '+x':
                yield (size - 1, i, j)


def wall(world, direction, size, pos, tex=2):
    for point in wall_points(size, direction):
        world.set_point(
            *mv(point, pos),
            cube.newtexcube(tex=tex)
        )

def low_wall(world, direction, size, pos, height=2, tex=2):
    for point in wall_points(size, direction, limit_j=height):
        world.set_point(
            *mv(point, pos),
            cube.newtexcube(tex=tex)
        )


def column(world, direction, size, pos, tex=2):
    for point in column_points(size, direction):
        world.set_point(
            *mv(point, pos),
            cube.newtexcube(tex=tex)
        )


def cube_points(*args):
    """
    call with a single number for a cube, or x, y, z for a rectangular prism
    """
    if len(args) == 1:
        x = args[0]
        y = args[0]
        z = args[0]
    else:
        (x, y, z) = args

    for i in range(x):
        for j in range(y):
            for k in range(z):
                yield (i, j, k)


def cube_s(world, size, pos, tex=2):
    for point in cube_points(size):
        world.set_point(
            *mv(point, pos),
            cube.newtexcube(tex=tex)
        )


def slope(world, pos, corners_down=None, tex=2):
    # Broken
    c = cube.newtexcube(tex=tex)

    if 0 in corners_down:
        c.edges[4] = 136
    if 1 in corners_down:
        c.edges[5] = 136
    if 2 in corners_down:
        c.edges[7] = 136
    if 3 in corners_down:
        c.edges[10] = 136

    world.set_point(*pos, c)


