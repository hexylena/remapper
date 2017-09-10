import struct


def to_magicavoxel(voxel_world, handle):
    cs = 4 * (1 + len(voxel_world.world))
    handle.write(struct.pack('4s', b'VOX '))
    handle.write(struct.pack('i', 150))
    handle.write(struct.pack('4s', b'MAIN'))
    handle.write(struct.pack('i', 0)) # Chunk size
    handle.write(struct.pack('i', cs + 36)) # child chunk size TODO
    # Size chunk
    handle.write(struct.pack('4s', b'SIZE'))
    handle.write(struct.pack('i', 12))
    handle.write(struct.pack('i', 0))
    handle.write(struct.pack('i', voxel_world.boundaries['xmax'])) # x
    handle.write(struct.pack('i', voxel_world.boundaries['ymax'])) # y
    handle.write(struct.pack('i', voxel_world.boundaries['zmax'])) # z
    # xyzi chunk
    handle.write(struct.pack('4s', b'XYZI'))
    handle.write(struct.pack('i', cs)) # chunk size TODO
    handle.write(struct.pack('i', 0)) # child chunk size
    handle.write(struct.pack('i', len(voxel_world.world))) # numvoxels
    m = lambda x: bytes(chr(x), 'ascii')
    for ((x, y, z), value) in voxel_world.world.items():
        handle.write(struct.pack('cccc', m(x), m(y), m(z), m(1)))
