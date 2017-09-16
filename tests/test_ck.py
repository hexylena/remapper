import pytest

# from redeclipse.prefabs import Room
from redeclipse.prefabs.construction_kit import wall_points, column_points, ConstructionKitMixin, cube_points, subtract_or_skip
from redeclipse.vector import FineVector, CoarseVector
from redeclipse.vector.orientations import NORTH, SOUTH, EAST, WEST, ABOVE, BELOW, VOXEL_OFFSET, TILE_VOX_OFF, SELF
from redeclipse.voxel import VoxelWorld


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
    assert next(n) == FineVector(0, 1, 0)

    n = column_points(2, SOUTH)
    next(n)
    assert next(n) == FineVector(0, -1, 0)

    n = column_points(2, EAST)
    next(n)
    assert next(n) == FineVector(1, 0, 0)

    n = column_points(2, WEST)
    next(n)
    assert next(n) == FineVector(-1, 0, 0)

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


def test_vector_to_voxelvec():
    q = VOXEL_OFFSET
    assert q.rotate(180) == FineVector(-0.5, -0.5, 0.5)
    assert q.vox() == FineVector(0, 0, 0)
    assert q.rotate(180).vox() == FineVector(-1, -1, 0)
    assert q.rotate(90).vox() == FineVector(-1, 0, 0)
    assert q.rotate(270).vox() == FineVector(0, -1, 0)


def test_ck_mixin():
    ckm = ConstructionKitMixin()
    ckm.pos = FineVector(64, 64, 64)

    assert ckm.pos.rotate('+x') == ckm.pos
    assert ckm.pos.rotate('-y') == ckm.pos.rotate(90)
    assert ckm.pos.rotate(90) == FineVector(-64, 64, 64)

    # check the general algorithm.
    # for a point, rotate it around the tile center.
    # This means use vector math to find the different
    oa = FineVector(0, 0, 0)  # SW
    ob = FineVector(0, 7, 0)  # NW
    oc = FineVector(7, 7, 0)  # NE
    od = FineVector(7, 0, 0)  # SE

    va = FineVector(0, 0, 0)  # SW
    vb = FineVector(0, 7, 0)  # NW
    vc = FineVector(7, 7, 0)  # NE
    vd = FineVector(7, 0, 0)  # SE
    # First, offset any and all vectors by their half-voxel offset.
    va += TILE_VOX_OFF
    vb += TILE_VOX_OFF
    vc += TILE_VOX_OFF
    vd += TILE_VOX_OFF
    # Now we have voxels around the (0, 0, 0) point where we can safely rotate.
    va = va.rotate(90)
    vb = vb.rotate(90)
    vc = vc.rotate(90)
    vd = vd.rotate(90)
    # Now we have to shift them back
    va -= TILE_VOX_OFF
    vb -= TILE_VOX_OFF
    vc -= TILE_VOX_OFF
    vd -= TILE_VOX_OFF

    # ok, algo looks good!
    assert vb == oa
    assert vc == ob
    assert vd == oc
    assert va == od

    ckm.orientation = '-y'
    observed_points = list(ckm.x_column(FineVector(0, 0, 0), NORTH, 4))
    expected_points = [FineVector(71 - i, 64, 64) for i in range(4)]
    for e, o in zip(expected_points, observed_points):
        assert e == o

    expected_points = [FineVector(71, 64 + i, 64) for i in range(4)]
    observed_points = list(ckm.x_column(FineVector(0, 0, 0), EAST, 4))
    for e, o in zip(expected_points, observed_points):
        assert e == o

    expected_points = [FineVector(71 + i, 64, 64) for i in range(4)]
    observed_points = list(ckm.x_column(FineVector(0, 0, 0), SOUTH, 4))
    for e, o in zip(expected_points, observed_points):
        assert e == o

    expected_points = [FineVector(71, 64 - i, 64) for i in range(4)]
    observed_points = list(ckm.x_column(FineVector(0, 0, 0), WEST, 4))
    for e, o in zip(expected_points, observed_points):
        assert e == o


def test_ck_mixin2():
    ckm = ConstructionKitMixin()
    ckm.pos = FineVector(56, 56, 56)

    assert ckm.pos.rotate('+x') == ckm.pos
    assert ckm.pos.rotate('-y') == ckm.pos.rotate(90)
    assert ckm.pos.rotate(90) == FineVector(-56, 56, 56)


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
        for pt in ckm.x_column(FineVector(1, 1, 0), ABOVE, 8):
            assert ckm.pos < pt < bounds


def test_ck_mixin_floorceil():
    ckm = ConstructionKitMixin()
    ckm.pos = FineVector(16, 8, 0)

    lower_bound = ckm.pos - FineVector(8, 8, 0)
    upper_bound = ckm.pos + FineVector(8, 8, 1)

    # Ok, let's test some invariants. Given a cube with a column along one
    # edge, no matter which way it is rotated, the voxels in the cube should
    # never leave the 8x8x8 space.

    for orientation in ('+x', '-x', '+y', '-y'):
        ckm.orientation = orientation
        # Column straight up from the southwest corner.
        for pt in ckm.x_floor(FineVector(0, 0, 0), 8):
            assert lower_bound <= pt <= upper_bound

    ckm.orientation = '+y'
    # Column straight up from the southwest corner.
    for pt in ckm.x_floor(FineVector(0, 0, 0), 8):
        assert lower_bound <= pt <= upper_bound


def test_ck_unknown_func():
    ckm = ConstructionKitMixin()

    with pytest.raises(Exception):
        ckm.x('asdf', None)


def test_ck_known_func_floor():
    """
    This test states that no matter what orientation a room is placed in,
    assuming it is in the same coarse vector, it should occupy the same
    space, (8, 16) on x and y.
    """
    vox = VoxelWorld(size=4)
    ckm = ConstructionKitMixin()
    ckm.pos = CoarseVector(1, 1, 1).fine()
    for orientation in ('+x', '-x', '+y', '-y'):
        vox = VoxelWorld(size=4)
        ckm.orientation = orientation
        ckm.x('floor', vox, SELF, size=8)
        for (x, y, z) in vox.world.keys():
            assert 8 <= x < 16
            assert 8 <= y < 16
            assert 8 == z
