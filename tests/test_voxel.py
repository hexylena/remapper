from redeclipse.voxel import VoxelWorld
from redeclipse.objects import cube


def test_octree():
    v = VoxelWorld(size=4)
    v.set_point(0, 0, 0, True)
    v.set_point(3, 3, 3, True)

    q = v.to_octree()
    for i in range(8):
        assert isinstance(q[i], cube)

    assert q[0].children[0] == True
    assert q[7].children[7] == True
