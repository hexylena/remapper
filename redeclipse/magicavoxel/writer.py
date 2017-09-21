import struct


def to_magicavoxel(voxel_world, handle, texman):
    cs = 4 * (1 + len(voxel_world.world))
    handle.write(struct.pack('4s', b'VOX '))
    handle.write(struct.pack('i', 150))
    handle.write(struct.pack('4s', b'MAIN'))
    handle.write(struct.pack('i', 0))  # Chunk size
    handle.write(struct.pack('i', cs + 36 + 1024))  # child chunk size TODO
    # Size chunk
    handle.write(struct.pack('4s', b'SIZE'))
    handle.write(struct.pack('i', 12))
    handle.write(struct.pack('i', 0))
    handle.write(struct.pack('i', int(voxel_world.xmax)))  # x
    handle.write(struct.pack('i', int(voxel_world.ymax)))  # y
    handle.write(struct.pack('i', int(voxel_world.zmax)))  # z
    # xyzi chunk
    handle.write(struct.pack('4s', b'XYZI'))
    handle.write(struct.pack('i', cs))  # chunk size TODO
    handle.write(struct.pack('i', 0))  # child chunk size
    handle.write(struct.pack('i', len(voxel_world.world)))  # numvoxels

    def m(x):
        return int(x)

    for ((x, y, z), value) in voxel_world.world.items():
        if x > 255 or y > 255 or z > 255 or x < 0 or y < 0 or z < 0:
            continue
        handle.write(struct.pack('BBBB', m(x), m(y), m(z), m(value.texture[0] + 1)))
        # handle.write(struct.pack('BBBB', m(x), m(y), m(z), 1))

    # colour chunk
    handle.write(struct.pack('4s', b'RGBA'))
    handle.write(struct.pack('i', 1024))  # chunk size
    handle.write(struct.pack('i', 0))  # child chunk size

    def n(x):
        return int(255 * x)

    for idx, (tex_key, tex) in enumerate(texman.atlas.items()):
        handle.write(struct.pack('BBBB', n(tex.r), n(tex.g), n(tex.b), 255)) # white

    for i in range(255 - len(texman.atlas)):
        handle.write(struct.pack('BBBB', 0, 0, 0, 255)) # white
