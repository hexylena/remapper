from redeclipse.voxel import VoxelWorld
from redeclipse.objects import cube, cubext, SurfaceInfo

v = VoxelWorld(size=2**5)

for i in range(0, 2**5):
    c = cube.newtexcube(tex=2)
    v.set_point(i, i, i, c)

print(v.to_octree())
