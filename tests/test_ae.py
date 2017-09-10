from redeclipse import aftereffects as ae
from redeclipse.voxel import VoxelWorld
from redeclipse.upm import UnusedPositionManager
from redeclipse.vector import FineVector


def test_vertical_gradient():
    assert ae.vertical_gradient(0, 0, 0) == 1.0
    assert ae.vertical_gradient(0, 0, 256) == 0.0


def test_gradient3():
    assert ae.gradient3(0, 0, 0) == 1.0
    assert 0.87 < ae.gradient3(0, 0, 256) < 0.88


def test_vg2():
    assert ae.vertical_gradient2(0, 0, 0) == 1.0
    assert 0.02 < ae.vertical_gradient2(0, 0, 256) < 0.03

    assert ae.vertical_gradient2(0, 0, 1024) == 0


def test_vg2_inv():
    assert 0.97 < ae.vertical_gradient2inv(0, 0, 256) < 0.98
    assert ae.vertical_gradient2inv(0, 0, 0) == 0


def test_grid():
    v = VoxelWorld(size=10)
    # grid only goes to zmax
    v.set_point(0, 0, 0, True)
    v.set_point(0, 0, 10, True)
    ae.grid(v, size=9)

    for (x, y, z) in v.world.keys():
        assert x % 9 == 0 or y % 9 == 0 or z % 9 == 0


def test_decay():
    v = VoxelWorld(size=10)
    # Fill the cube
    for i in range(10):
        for j in range(10):
            for k in range(10):
                v.set_point(i, j, k, True)

    # Decay 0.5 on average.
    def tmp_pos_fun(x, y, z):
        return 0.5

    ae.decay(v, tmp_pos_fun)
    assert 400 < len(v.world.keys()) < 600


def test_growth():
    v = VoxelWorld(size=10)
    # Decay 0.5 on average.
    def tmp_pos_fun(x, y, z):
        return 0.5

    v.set_point(0, 0, 0, True)
    v.set_point(10, 10, 10, True)

    ae.growth(v, tmp_pos_fun)
    assert 400 < len(v.world.keys()) < 600


def test_box():
    world_size = 10
    v = VoxelWorld(size=world_size)
    ae.box(v)

    for (x, y, z) in v.world.keys():
        assert x == 0 or y == 0 or z == 0 or \
            x == world_size - 1 or \
            y == world_size - 1 or \
            z == world_size - 1


def test_endcap():
    upm = UnusedPositionManager(10)
    upm.unoccupied = [
        (FineVector(4, 4, 4), None, None),
    ]

    world_size = 10
    v = VoxelWorld(size=world_size)
    ae.endcap(v, upm)

    assert (0, 0, 0) not in v.world.keys()
