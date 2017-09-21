#!/usr/bin/env python
import copy
import argparse
import random
import logging
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.entities import Sunlight
from redeclipse import prefabs as p
from redeclipse.upm import UnusedPositionManager
from redeclipse.cli import weighted_choice
from redeclipse.magicavoxel import autodiscover, TEXMAN
from redeclipse.magicavoxel.writer import to_magicavoxel
from redeclipse.prefabs import STARTING_POSITION

from redeclipse.vector import CoarseVector, FineVector, AbsoluteVector
from redeclipse.vector.orientations import rotate_yaw, SELF, \
    SOUTH, NORTH, WEST, EAST, ABOVE, \
    ABOVE_FINE, NORTHWEST, \
    NORTHEAST, SOUTHWEST, SOUTHEAST, TILE_CENTER, HALF_HEIGHT
# from redeclipse.skybox import MinecraftSky
from redeclipse.vector import CoarseVector, FineVector

from tqdm import tqdm
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mpz_in, mpz_out, size=2**7, seed=42, rooms=200, debug=False):
    random.seed(seed)
    mymap = parse(mpz_in.name)
    v = VoxelWorld(size=size)
    room_counts = 32
    possible_rooms = autodiscover()

    def mirror(d):
        if isinstance(d, dict):
            kwargs['orientation'] = kwargs['orientation'].rotate(180)
            return kwargs
        else:
            return CoarseVector(
                room_counts - d[0],
                room_counts - d[1],
                d[2]
            )

    def random_room(connecting_room):
        """Pick out a random room based on the connecting room and the
        transition probabilities of that room."""
        choices = []
        probs = connecting_room.get_transition_probs()
        for room in possible_rooms:
            # Append to our possibilities
            choices.append((
                # The room, and the probability of getting that type of room
                # based on the current room type
                room, probs.get(room.room_type, 0.1)
            ))

        return weighted_choice(choices)

    # Initialize
    upm = UnusedPositionManager(size, mirror=True)

    # Insert a starting room. We move it vertically downward from center since
    # we have no way to build stairs downwards yet.
    # We use the spawn room as our base starting room
    b = copy.copy(possible_rooms[0])
    b_m = copy.copy(possible_rooms[0])
    b.re_init(pos=STARTING_POSITION, orientation=EAST)
    b_m.re_init(pos=mirror(STARTING_POSITION), orientation=EAST)
    print(b)
    print(b._get_positions())
    # Register our new room
    upm.register_room(b)
    upm.register_room(b_m)
    # Render it to the map
    b.render(v, mymap)
    b_m.render(v, mymap)
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
            # Pick a random position for this notional room to go
            try:
                (position, prev_room, orientation) = upm.nonrandom_position(upm.nrp_flavour_center_hole)
            except Exception as e:
                # If we have no more positions left, break.
                print("Possibly run out of positions before placing all rooms. Try a different seed?")
                print(e)
                break

            # If we are here, we do have a position + orientation to place in
            kwargs = {'orientation': orientation}
            # Get a random room, influenced by the prev_room
            _roomClass = random_room(prev_room)
            # Then safe to work with it.
            kwargs.update(_roomClass.randOpts(prev_room))
            # Copy them here, not sure if makes sense.
            r = copy.copy(_roomClass)
            r_m = copy.copy(_roomClass)
            # Initialize room, required to correctly calculate get_positions()
            r.re_init(pos=position, **kwargs)
            r_m.re_init(pos=mirror(position), **mirror(kwargs))
            # Try adding it
            try:
                if not upm.preregister_rooms(r, r_m):
                    log.info("would fail on one or more rooms")
                    continue

                # This step might raise an exception
                upm.register_room(r)
                upm.register_room(r_m)

                pbar.update(2)
                pbar.set_description('%3d' % v.zmax)
                # If we get here, we've placed successfully so bump count + render
                room_count += 2
                r.render(v, mymap)
                r_m.render(v, mymap)
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
    TEXMAN.emit_conf(mpz_out)
    TEXMAN.copy_data()
    # mymap.skybox(MinecraftSky('/home/hxr/games/redeclipse-1.5.3/'))

    # Standard code to render octree to file.

    with open('tmp.vox', 'wb') as handle:
        to_magicavoxel(v, handle, TEXMAN)
    print('voxle')
    mymap.world = v.to_octree()
    mymap.world[0].octsav = 0
    mymap.write(mpz_out.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('mpz_in', type=argparse.FileType('r'), help='Input .mpz file')
    parser.add_argument('mpz_out', type=argparse.FileType('w'), help='Output .mpz file')

    parser.add_argument('--size', default=2**8, type=int, help="World size. Danger!")
    parser.add_argument('--seed', default=42, type=int, help="Random seed")
    parser.add_argument('--rooms', default=200, type=int, help="Number of rooms to place")
    parser.add_argument('--debug', action='store_true', help="Debugging")
    args = parser.parse_args()
    main(**vars(args))
