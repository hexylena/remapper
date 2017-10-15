#!/usr/bin/env python
import argparse
import random
import logging

from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.entities import Sunlight
from redeclipse.upm import UnusedPositionManager
from redeclipse.magicavoxel.writer import to_magicavoxel
from redeclipse.prefabs import STARTING_POSITION, TEXMAN
from redeclipse.prefabs import magica as m

from redeclipse.vector.orientations import EAST

from tqdm import tqdm
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mpz_in, mpz_out, size=2**8, seed=42, rooms=200, debug=False, magica=None):
    random.seed(seed)
    mymap = parse(mpz_in.name)
    v = VoxelWorld(size=size)

    magica_rooms = [
        # 'castle_gate', 'castle_gate_simple', 'castle_large',
        # 'castle_wall_corner',  # 'castle_small_deis',
        # 'castle_wall_end_cliff', 'castle_wall_entry',
        # 'castle_wall_section', 'castle_wall_section_endcap',
        # 'castle_wall_section_long', 'castle_wall_section_long_damaged',
        # 'castle_wall_section_tjoint', 'castle_wall_tower', 'wooden_bridge',
        # 'dungeon_2x2', 'dungeon_junction', 'dungeon_stair2',
        # 'dungeon_walkway', 'dungeon_walkway3',
        'station_tube1', 'station_tube3', 'station_tube_jumpx',
        'station_tubeX', 'station_endcap', 'station_right', 'station_ring',
        'station_ring_vertical', 'station_sphere', 'station_sphere_slice',
        'station_stair2',
    ]
    possible_rooms = [getattr(m, room_type) for room_type in magica_rooms]

    # magica_endcaps = ['castle_wall_end_cliff', 'castle_wall_section_endcap']
    magica_endcaps = ['station_endcap']
    possible_endcaps = [getattr(m, room_type) for room_type in magica_endcaps]

    # Initialize
    upm = UnusedPositionManager(size, mirror=True)

    # Insert a starting room. We move it vertically downward from center since
    # we have no way to build stairs downwards yet.
    # We use the spawn room as our base starting room
    Room = m.castle_small_deis
    b = Room(pos=STARTING_POSITION, orientation=EAST)
    # Register our new room
    upm.register_room(b)
    # Render it to the map
    b.render(v, mymap)
    # Convert rooms to int
    rooms = int(rooms)
    sunlight = Sunlight(
        red=128,
        green=128,
        blue=128,
        offset=45,  # top
    )
    mymap.ents.append(sunlight)

    room_count = 0

    logging.info("Placing rooms")
    with tqdm(total=rooms) as pbar:
        while True:
            # Continually try and place rooms until we hit 200.
            if room_count >= rooms:
                logging.info("Placed enough rooms")
                break

            try:
                notional_rooms = upm.room_localization(possible_rooms)

                for r in notional_rooms:
                    upm.register_room(r)
                    pbar.update(1)
                    pbar.set_description('z:%3d u:%d o:%d' % (v.zmax, len(upm.unoccupied), len(upm.occupied)))
                    # If we get here, we've placed successfully so bump count + render
                    room_count += 1
                    r.render(v, mymap)
                    break
                else:
                    pass
                    # print("No rooms returned.")
            except Exception:
                # If we have no more positions left, break.
                print("Possibly run out of positions before placing all rooms. Try a different seed?")
                break

    # Apply endcaps
    for room in upm.endcap(debug=debug, possible_endcaps=possible_endcaps):
        room.render(v, mymap)

    from redeclipse.aftereffects import box_outline
    box_outline(v, height=48)

    # Emit config + textures
    # mymap.skybox(MinecraftSky('/home/hxr/games/redeclipse-1.5.3/'))

    if magica:
        to_magicavoxel(v, magica, TEXMAN)

    if mpz_out:
        TEXMAN.emit_conf(mpz_out)
        TEXMAN.copy_data()

        mymap.world = v.to_octree()
        mymap.world[0].octsav = 0
        mymap.write(mpz_out.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('mpz_in', type=argparse.FileType('r'), help='Input .mpz file')
    parser.add_argument('--mpz_out', type=argparse.FileType('w'), help='Output .mpz file')

    parser.add_argument('--magica', type=argparse.FileType('wb'), help='Output .vox file')

    parser.add_argument('--size', default=2**8, type=int, help="World size. Danger!")
    parser.add_argument('--seed', default=42, type=int, help="Random seed")
    parser.add_argument('--rooms', default=200, type=int, help="Number of rooms to place")
    parser.add_argument('--debug', action='store_true', help="Debugging")
    args = parser.parse_args()
    main(**vars(args))
