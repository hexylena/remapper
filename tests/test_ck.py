from redeclipse.prefabs import Room
from redeclipse.vector import CoarseVector, FineVector
from redeclipse.vector.orientations import NORTH, SOUTH, EAST, WEST, ABOVE, BELOW
from redeclipse.prefabs.construction_kit import wall_points, column_points, ConstructionKitMixin, cube_points, subtract_or_skip


def test_wall_points_ltz():
    a = list(wall_points(
        4, '-z'
    ))

    for i in range(4):
        for j in range(4):
            assert FineVector(i, j, 0) in a


def test_wall_points_gtz():
    a = list(wall_points(
        4, '+z'
    ))

    for i in range(4):
        for j in range(4):
            assert FineVector(i, j, 4 - 1) in a


def test_wall_points_ltx():
    a = list(wall_points(
        4, '-x'
    ))

    for i in range(4):
        for j in range(4):
            assert FineVector(0, i, j) in a


def test_wall_points_gtx():
    a = list(wall_points(
        4, '+x'
    ))

    for i in range(4):
        for j in range(4):
            assert FineVector(4 - 1, i, j) in a


def test_wall_points_lty():
    a = list(wall_points(
        4, '-y'
    ))

    for i in range(4):
        for j in range(4):
            assert FineVector(i, 0, j) in a


def test_wall_points_gty():
    a = list(wall_points(
        4, '+y'
    ))

    for i in range(4):
        for j in range(4):
            assert FineVector(i, 4 - 1, j) in a


def test_wall_points_ltz2():
    a = list(wall_points(
        -4, '-z'
    ))

    for i in range(-4, 0):
        for j in range(-4, 0):
            assert FineVector(i, j, 0) in a


def test_wall_points_limit_ij():
    a = list(wall_points(
        4, '-z', limit_i=2, limit_j=2
    ))

    for i in range(2):
        for j in range(2):
            assert FineVector(i, j, 0) in a


def test_column_points():
    n = column_points(2, NORTH)
    next(n)
    assert next(n) == FineVector(1, 0, 0)

    n = column_points(2, SOUTH)
    next(n)
    assert next(n) == FineVector(-1, 0, 0)

    n = column_points(2, EAST)
    next(n)
    assert next(n) == FineVector(0, 1, 0)

    n = column_points(2, WEST)
    next(n)
    assert next(n) == FineVector(0, -1, 0)

    n = column_points(2, ABOVE)
    next(n)
    assert next(n) == FineVector(0, 0, 1)

    n = column_points(2, BELOW)
    next(n)
    assert next(n) == FineVector(0, 0, -1)


def test_cube_points():
    a = list(cube_points(
        4, 4, 4
    ))

    for i in range(4):
        for j in range(4):
            for k in range(4):
                assert FineVector(i, j, k) in a


def test_sos_subtract():
    assert subtract_or_skip(True, 0)
    assert subtract_or_skip(True, 1)


def test_sos_skip():
    for i in range(100):
        assert subtract_or_skip(False, 0)

    for i in range(100):
        assert not subtract_or_skip(False, 1)


def test_ck_mixin():
    ckm = ConstructionKitMixin()
    print(ckm)
    assert False
