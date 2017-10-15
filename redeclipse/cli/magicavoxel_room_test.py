#!/usr/bin/env python
import argparse
import logging

from redeclipse import prefabs, Map
from redeclipse.cli import parse
from redeclipse.entities import Sunlight
from redeclipse.prefabs import magica
from redeclipse.magicavoxel.writer import to_magicavoxel
from redeclipse.upm import UnusedPositionManager
from redeclipse.vector import CoarseVector
from redeclipse.vector.orientations import SOUTH, NORTH, WEST, EAST
from redeclipse.voxel import VoxelWorld
# from redeclipse.skybox import MinecraftSky

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main():
    magica_rooms = [
        # 'castle_gate', 'castle_gate_simple',  'castle_large',
        # 'castle_small_deis', 'castle_wall_corner',
        # 'castle_wall_end_cliff', 'castle_wall_entry',
        # 'castle_wall_section', 'castle_wall_section_endcap',
        # 'castle_wall_section_long', 'castle_wall_section_long_damaged',
        # 'castle_wall_section_tjoint', 'castle_wall_tower',
        'dungeon_2x2', 'dungeon_junction', 'dungeon_stair2',
        'dungeon_walkway', 'dungeon_walkway3',
        'station_tube1', 'station_tube3', 'station_tube_jumpx',
        'station_tubeX', 'station_endcap', 'station_right', 'station_ring',
        'station_ring_vertical', 'station_sphere', 'station_sphere_slice',
        'station_stair2',
    ]
    magica_classes = [getattr(magica, room_type) for room_type in magica_rooms]

    for idx, Room in enumerate(magica_classes):
        # mymap = Map('MAPZ', 150, 0, None, 0, [], [], None, None, None)
        mymap = parse('maps/empty-day.mpz')

        upm = UnusedPositionManager(2**8, mirror=True, noclip=True)
        v = VoxelWorld(size=2**8)
        logging.info("Processing %s" % Room.__name__)

        kwargs = Room.randOpts(None)
        e = Room(pos=CoarseVector(8 + 3, 8, 1), orientation=EAST, **kwargs)
        kwargs = Room.randOpts(None)
        w = Room(pos=CoarseVector(8 - 3, 8, 1), orientation=WEST, **kwargs)
        kwargs = Room.randOpts(None)
        n = Room(pos=CoarseVector(8, 8 + 3, 1), orientation=NORTH, **kwargs)
        kwargs = Room.randOpts(None)
        s = Room(pos=CoarseVector(8, 8 - 3, 1), orientation=SOUTH, **kwargs)

        upm.register_room(n)
        upm.register_room(s)
        upm.register_room(e)
        upm.register_room(w)

        n.render(v, mymap)
        s.render(v, mymap)
        e.render(v, mymap)
        w.render(v, mymap)

        for (pos, typ, ori) in upm.unoccupied:
            r = prefabs.TestRoom(pos, orientation=EAST)
            r.render(v, mymap)

        with open('%03d_%s.vox' % (idx, Room.__name__), 'wb') as handle:
            to_magicavoxel(v, handle, prefabs.TEXMAN)

        with open('/home/hxr/.redeclipse/maps/%03d_%s.mpz' % (idx, Room.__name__), 'wb') as mpz_out:
            sunlight = Sunlight(
                red=128,
                green=128,
                blue=128,
                offset=45,  # top
            )
            mymap.ents.append(sunlight)

            prefabs.TEXMAN.emit_conf(mpz_out)
            prefabs.TEXMAN.copy_data()

            mymap.world = v.to_octree()
            mymap.world[0].octsav = 0
            mymap.write(mpz_out.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    args = parser.parse_args()
    main(**vars(args))
