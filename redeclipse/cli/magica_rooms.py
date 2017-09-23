#!/usr/bin/env python
import argparse
import random
import logging
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse, weighted_choice, random_room
from redeclipse.entities import Sunlight
from redeclipse import prefabs as p
from redeclipse.upm import UnusedPositionManager
from redeclipse.magicavoxel.writer import to_magicavoxel
from redeclipse.prefabs import STARTING_POSITION, TEXMAN
from redeclipse.prefabs import magica as m

from redeclipse.vector.orientations import EAST, n, CARDINALS, NORTH
from redeclipse.vector import CoarseVector

from tqdm import tqdm
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mpz_in, mpz_out, size=2**7, seed=42, rooms=200, debug=False, magica=None):
    random.seed(seed)
    mymap = parse(mpz_in.name)
    v = VoxelWorld(size=size)
    room_counts = 32

    magica_rooms = [
        'castle_small_deis', 'castle_wall_section', 'castle_wall_corner',
        'castle_wall_entry', 'castle_wall_tower', #'castle_gate'
    ]
    possible_rooms = [getattr(m, room_type) for room_type in magica_rooms]

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
    patience = 500

    room_count = 0

    logging.info("Placing rooms")
    with tqdm(total=rooms) as pbar:
        while True:
            # Continually try and place rooms until we hit 200.
            if room_count >= rooms:
                logging.info("Placed enough rooms")
                break

            # Pick a random position for this notional room to go
            try:
                (prev_room_door, prev_room, prev_room_orientation) = upm.nonrandom_position(upm.nrp_flavour_center_hole)
                # print('chosen door', prev_room_door, prev_room, n(prev_room_orientation))
            except Exception as e:
                # If we have no more positions left, break.
                print("Possibly run out of positions before placing all rooms. Try a different seed?")
                print(e)
                break

            # If we are here, we do have a position + orientation to place in
            # Get a random room, influenced by the prev_room
            roomClass = random_room(prev_room, possible_rooms)

            # This is TEMPORARY. We randomly orient a room first, hopefully we can find an acceptable door.
            kwargs = {'orientation': random.choice(CARDINALS)}
            kwargs.update(roomClass.randOpts(prev_room))
            # Initialize room, required to correctly calculate get_positions()/get_doorways()
            r = roomClass(pos=CoarseVector(2, 2, 3), **kwargs)

            # We've already picked a prev_room_door (and we know its orientation)
            # Now we pick a door on the new room we'll place.
            roomClass_doors = r.get_doorways()
            # print('possible doors on new ', [{'off': x['offset'], 'ori': n(x['orientation'])} for x in roomClass_doors])
            # Shuffle it.
            random.shuffle(roomClass_doors)
            # Find a door that is facing in the opposite direction as prev_room_orientation
            options = [x for x in roomClass_doors if x['orientation'] == prev_room_orientation.rotate(180)]
            # print('possible doors in dir ', [{'off': x['offset'], 'ori': n(x['orientation'])} for x in options])
            if len(options) == 0:
                # No match, continue
                # print("Nothing works here.")
                patience -= 1
                if patience < 0:
                    break

                continue

            # Chose a door on our new room that's in the correct orientation
            chosen_door = options[0]

            # print('old room pos', prev_room.pos)
            # print('new room pos', r.pos)

            # print('old chosen door', prev_room_door, n(prev_room_orientation))
            # print('new chosen door', chosen_door['offset'], n(chosen_door['orientation']))
            # Room offset
            room_offset = chosen_door['offset'] - prev_room_door + prev_room_orientation
            # print('must_shift', room_offset)
            r = roomClass(pos=CoarseVector(2, 2, 3) - room_offset, **kwargs)
            # print('old room pos', prev_room.pos)
            # print('new room pos', r.pos)

            try:
                if not upm.preregister_rooms(r):
                    # log.info("would fail on one or more rooms")
                    continue

                # This step might raise an exception
                upm.register_room(r)

                pbar.update(2)
                pbar.set_description('%3d' % v.zmax)
                # If we get here, we've placed successfully so bump count + render
                room_count += 1
                r.render(v, mymap)
            except Exception as e:
                # We have failed to register the room because
                # it does not fit here.
                # So, we continue.
                if debug:
                    print(e)
                continue

    if debug:
        for (pos, typ, ori) in upm.unoccupied:
            r = p.TestRoom(pos, orientation=EAST)
            r.render(v, mymap)

    # from redeclipse.aftereffects import grid, decay, gradient3, box
    # grid(v, size=48)
    # decay(v, gradient3)
    # box(v)

    # Emit config + textures
    # mymap.skybox(MinecraftSky('/home/hxr/games/redeclipse-1.5.3/'))

    # Standard code to render octree to file.

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
