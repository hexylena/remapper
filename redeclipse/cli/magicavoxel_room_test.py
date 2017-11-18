#!/usr/bin/env python
import argparse
import logging

from redeclipse import prefabs
# We must override this ASAP since everyone else (e.g. prefabs) also imports the TEXMAN from prefab.
# Back to our normally scheduled imports.
from redeclipse.cli import parse
from redeclipse.entities import Sunlight
from redeclipse.magicavoxel.writer import to_magicavoxel
from redeclipse.prefabs import castle, dungeon, spacestation, original  # noqa
from redeclipse.upm import UnusedPositionManager
from redeclipse.vector import CoarseVector
from redeclipse.vector.orientations import EAST
from redeclipse.voxel import VoxelWorld
# from redeclipse.skybox import MinecraftSky

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(magica=False, redeclipse=False):
    # Override texman
    magica_classes = [
        # # Original
        # original.spawn_room
        # # Castle
        # castle.castle_gate, castle.castle_gate_simple,
        # castle.castle_large, castle.castle_wall_corner,
        # castle.castle_wall_end_cliff, castle.castle_wall_entry,
        # castle.castle_wall_section, castle.castle_wall_section_long,
        # castle.castle_wall_section_long_damaged,
        # castle.castle_wall_section_tjoint, castle.castle_wall_tower,
        # castle.wooden_bridge,
        # castle.castle_wall_section_x
        # castle.castle_flag_room,
        # # Dungeon
        # dungeon.dungeon_2x2, dungeon.dungeon_junction, dungeon.dungeon_stair2,
        # dungeon.dungeon_walkway, dungeon.dungeon_walkway3,
        # # Space
        # spacestation.station_tube1, spacestation.station_tube3, spacestation.station_tube_jumpx,
        # spacestation.station_tubeX, spacestation.station_endcap, spacestation.station_right, spacestation.station_ring,
        # spacestation.station_ring_vertical, spacestation.station_sphere, spacestation.station_sphere_slice,
        # spacestation.station_stair2,
        spacestation.station_uturn,
        spacestation.station_tubeX_variant,
        spacestation.station_tube3layered,
        spacestation.station_sbend,
        spacestation.station_flagroom,
    ]

    for idx, Room in enumerate(magica_classes):
        mymap = parse('maps/empty-day.mpz')

        upm = UnusedPositionManager(2**8, mirror=4, noclip=True)
        v = VoxelWorld(size=2**8)
        logging.info("Processing %s" % Room.__name__)

        kwargs = Room.randOpts(None)
        e = Room(pos=CoarseVector(8 + 3, 8, 1), orientation=EAST, **kwargs)
        upm.register_room(e)
        upm.endcap(debug=True, possible_endcaps=[])

        for room in upm.rooms:
            room.render(v, mymap)

        if magica:
            with open('%03d_%s.vox' % (idx, Room.__name__), 'wb') as handle:
                to_magicavoxel(v, handle, prefabs.TEXMAN)

        if redeclipse:
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
    parser.add_argument('--magica', action='store_true', help='Output magica .vox files')
    parser.add_argument('--redeclipse', action='store_true', help='Output redeclipse .mpz files')
    args = parser.parse_args()
    main(**vars(args))
