#!/usr/bin/env python
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.entities import Sunlight
from redeclipse import prefabs as p
from redeclipse.upm import UnusedPositionManager
from redeclipse.vector.orientations import EAST
import argparse
import random


def main(mpz_in, mpz_out, size=2**7, seed=42, rooms=200, debug=False):
    random.seed(seed)
    mymap = parse(mpz_in.name)
    v = VoxelWorld(size=size)

    def weighted_choice(choices):
        """Weighted random distribution. Given a list like [('a', 1), ('b', 2)]
        will return a 33% of the time and b 66% of the time."""
        # http://stackoverflow.com/a/3679747
        total = sum(w for c, w in choices)
        r = random.uniform(0, total)
        upto = 0
        for c, w in choices:
            if upto + w >= r:
                return c
            upto += w
        assert False, "Shouldn't get here"

    def random_room(connecting_room):
        """Pick out a random room based on the connecting room and the
        transition probabilities of that room."""
        possible_rooms = [
            p.Room,
            p.SpawnRoom,
            # p.JumpCorridor3,
            # p.Corridor4way,
            # p.Stair,
            # p.PoleRoom,
            # p.Corridor2way,
            # p.AltarRoom,
            # p.ImposingRingRoom,
            # p.ImposingBlockRoom,
            # p.JumpCorridorVertical,
            p.NLongCorridor,
            p.MultiPlatform,
            p.DigitalRoom,
            p.CrossingWalkways,
            p.JumpCorridorVerticalCenter,
            p.PlusPlatform,
        ]

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
    upm = UnusedPositionManager(size)

    # Insert a starting room. We move it vertically downward from center since
    # we have no way to build stairs downwards yet.
    starting_position = p.m(6, 6, 3)
    # We use the spawn room as our base starting room
    b = p.SpawnRoom(pos=starting_position, orientation="+y")
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
    while True:
        # Continually try and place rooms until we hit 200.
        if room_count >= rooms:
            break
        # Pick a random position for this notional room to go
        try:
            (position, prev_room, orientation) = upm.random_position()
        except Exception as e:
            # If we have no more positions left, break.
            print(e)
            break

        # If we are here, we do have a position + orientation to place in
        kwargs = {'orientation': orientation}
        # Get a random room, influenced by the prev_room
        roomClass = random_room(prev_room)
        kwargs.update(roomClass.randOpts(prev_room))
        # Initialize room, required to correctly calculate get_positions()
        r = roomClass(pos=position, **kwargs)
        # Try adding it
        try:
            # This step might raise an exception
            upm.register_room(r)
            # If we get here, we've placed successfully so bump count + render
            room_count += 1
            r.render(v, mymap)
            print("[%s] Placing %s at %s (%s) Variant:%s" % (room_count, roomClass.__name__, position, orientation, '|'.join(['1' if x else '0' for x in kwargs.get('randflags', [])])))
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

    # Standard code to render octree to file.
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
