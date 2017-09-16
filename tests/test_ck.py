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
    ckm.pos = FineVector(64, 64, 64)

    assert ckm.pos.rotate('+x') == ckm.pos
    assert ckm.pos.rotate('-y') == ckm.pos.rotate(90)
    assert ckm.pos.rotate(90) == FineVector(-64, 64, 64)

    ckm.orientation = '+x'
    expected_points = [FineVector(64 + i, 64, 64) for i in range(4)]
    observed_points = list(ckm._x_column(FineVector(0, 0, 0), NORTH, 4))
    for e, o in zip(expected_points, observed_points):
        assert e == o

    # expected_points = [FineVector(64, 64 + i, 64) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), EAST, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o

    # expected_points = [FineVector(64 - i, 64, 64) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), SOUTH, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o

    # expected_points = [FineVector(64, 64 - i, 64) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), WEST, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o


    # ckm.orientation = '-x'
    # expected_points = [FineVector(64 + 8 - i, 64 + 8, 64) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), NORTH, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o

    # expected_points = [FineVector(64 + 8, 64 + 8 - i, 64) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), EAST, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o

    # expected_points = [FineVector(64 + 8 + i, 64 + 8, 64) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), SOUTH, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o

    # expected_points = [FineVector(64 + 8, 64 + 8 + i, 64) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), WEST, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o


def test_ck_mixin2():
    ckm = ConstructionKitMixin()
    ckm.pos = FineVector(56, 56, 56)

    assert ckm.pos.rotate('+x') == ckm.pos
    assert ckm.pos.rotate('-y') == ckm.pos.rotate(90)
    assert ckm.pos.rotate(90) == FineVector(-56, 56, 56)

    # ckm.orientation = '+x'
    # expected_points = [FineVector(56 + i, 56, 56) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), NORTH, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o

    # expected_points = [FineVector(56, 56 + i, 56) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), EAST, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o

    # expected_points = [FineVector(56 - i, 56, 56) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), SOUTH, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o

    # expected_points = [FineVector(56, 56 - i, 56) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), WEST, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o


    # ckm.orientation = '-x'
    # expected_points = [FineVector(56 + 8 - i, 56 + 8, 56) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), NORTH, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o

    # expected_points = [FineVector(56 + 8, 56 + 8 - i, 56) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), EAST, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o

    # expected_points = [FineVector(56 + 8 + i, 56 + 8, 56) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), SOUTH, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o

    # expected_points = [FineVector(56 + 8, 56 + 8 + i, 56) for i in range(4)]
    # observed_points = list(ckm._x_column(FineVector(0, 0, 0), WEST, 4))
    # for e, o in zip(expected_points, observed_points):
        # assert e == o


def test_ck_mixin_3():
    ckm = ConstructionKitMixin()
    ckm.pos = FineVector(16, 8, 0)
    bounds = ckm.pos + FineVector(8, 8, 8)

    # Ok, let's test some invariants. Given a cube with a column along one
    # edge, no matter which way it is rotated, the voxels in the cube should
    # never leave the 8x8x8 space.

    for orientation in ('+x', '-x', '+y', '-y'):
        ckm.orientation = orientation
        # Column straight up from the southwest corner.
        for pt in ckm._x_column(FineVector(1, 1, 0), ABOVE, 8):
            assert ckm.pos < pt < bounds
