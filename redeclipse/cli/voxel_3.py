#!/usr/bin/env python
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.prefabs import m, mv, BaseRoom, AltarRoom, \
    Corridor2way, Corridor2way_A, \
    Corridor4way, Corridor4way_A, \
    Stair, SpawnRoom, NLongCorridor
import argparse
import sys
import random
random.seed(82)

IJ_SIZE = 2**7
K_SIZE = 50
MAP_SEED = 0

octaves = 1
noise_scaling = 32

# import random

class UnusedPositionManager:
    def __init__(self):
        self.occupied = set()
        self.unoccupied = []

    def getOrientationToManhattanRoom(self, p, used):
        for u in used:
            if u[1] == p[1]:# and u[2] == p[2]:
                if u[0] < p[0]:
                    return '-x'
                else:
                    return '+x'
            elif u[0] == p[0]:# and u[2] == p[2]:
                if u[1] < p[1]:
                    return '-y'
                else:
                    return '+y'
            # elif u[0] == p[0] and u[1] == p[1]:
                # if u[2] < p[2]:
                    # return '-z'
                # else:
                    # return '+z'
        raise Exception("UNKNOWN")

    def is_legal(self, position):
        return all([x >= 0 and x < IJ_SIZE for x in position])

    def CoM(self, positions):
        x = 0
        y = 0
        z = 0
        for q in positions:
            x += q[0]
            y += q[1]
            z += q[2]
        return (
            x / len(positions),
            y / len(positions),
            z / len(positions)
        )

    def register_room(self, room):
        # Register positions occupied by this room
        used = room.get_positions()
        self.occupied = self.occupied.union(used)
        # print('rr occ CoM', self.CoM(used), used)
        # Remove occupied positions from possibilities
        self.unoccupied = [(p, r, o) for (p, r, o) in self.unoccupied if p not in used]
        # print('rr unocc', self.unoccupied)

        # Get doorways
        doors = room.get_doorways()
        # print('rr door', doors)
        for position in doors:
            # If that door position is not occupied by something else
            if position not in self.occupied and self.is_legal(position):
                orientation = self.getOrientationToManhattanRoom(position, used)
                self.unoccupied.append((position, room, orientation))

    def random_position(self):
        if len(self.occupied) > 0:
            return random.choice(self.unoccupied)
        else:
            raise Exception("No more space!")

    def print(self):
        # print('Unused', pprint.pformat([(x, y.__class__.__name__, z) for (x, y, z) in self.unoccupied]))
        # print('  used', self.occupied)
        print('  Unus', [x for (x, y, z) in self.unoccupied])
        print('  used', self.occupied)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('input', help='Input .mpz file')
    parser.add_argument('output', help='Output .mpz file')
    args = parser.parse_args()

    mymap = parse(args.input)
    v = VoxelWorld(size=2**7)

    def weighted_choice(choices):
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
        possible_rooms =  [
            # BaseRoom,
            # Corridor4way,
            # Corridor4way_A,
            # Stair,
            # SpawnRoom,
            # Corridor2way,
            # Corridor2way_A,
            AltarRoom,
            NLongCorridor
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


    # Insert a starting room
    starting_position = m(6, 6, 6)
    # b = BaseRoom(v, mymap, pos=starting_position, tex=5)
    b = SpawnRoom(v, mymap, pos=starting_position, orientation='-y')
    print("Starting: ", starting_position)
    upm = UnusedPositionManager()
    upm.register_room(b)
    upm.print()

    for i in range(20):
        # Pick a random position for this room to ugo
        try:
            (position, prev_room, orientation) = upm.random_position()
        except Exception as e:
            print(e)
        kwargs = {'orientation': orientation}
        # Get a random room, influence with prev_room
        roomClass = random_room(prev_room)
        print(position, prev_room, orientation, roomClass)
        # print("[%s] Placing %s at %s" % (i, roomClass.__name__, position))
        # Place the room
        r = roomClass(v, mymap, pos=position, **kwargs)
        upm.register_room(r)
        upm.print()

    mymap.world = v.to_octree()
    mymap.world[0].octsav = 0
    mymap.write(args.output)
