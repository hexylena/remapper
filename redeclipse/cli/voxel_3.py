#!/usr/bin/env python
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse
from redeclipse.prefabs import m, BaseRoom, AltarRoom, \
    Corridor2way, Corridor2way_A, \
    Corridor4way_A, \
    Stair, SpawnRoom, NLongCorridor, JumpCorridor3
import argparse
import random
random.seed(42)

# Scale of map, 2**7 individual cubes.
IJ_SIZE = 2**7


class UnusedPositionManager:
    """Class for maintaining a quick-lookup list of which 8x8x8 cubes are in-use

    This is closely tied to our prefab model
    """
    def __init__(self):
        # Set of occupied positions
        self.occupied = set()
        # Set of doors that we can connect to
        self.unoccupied = []

    def getOrientationToManhattanRoom(self, p, used):
        """Get the orientation from the previous room to the door.

        This informs which orientation we should place the next piece in, in
        order to have it line up. If the door is in the X axis previously, the
        next piece placed should also be in the X axis
        """
        for u in used:
            # For a set of "used" positions, only ONE block should be directly
            # next to the previous one (we don't do crazy U shaped things yet.)
            if u[1] == p[1]:
                # If the Y position is the same, must be in X direction
                if u[0] < p[0]:
                    return '-x'
                else:
                    return '+x'
            elif u[0] == p[0]:
                # If the X position is the same, must be in Y direction
                if u[1] < p[1]:
                    return '-y'
                else:
                    return '+y'
            # NO SUPPORT for joining parts on a z-axis, joins must be X/Y
            # elif u[0] == p[0] and u[1] == p[1]:
                # if u[2] < p[2]:
                    # return '-z'
                # else:
                    # return '+z'
        raise Exception("UNKNOWN")

    def is_legal(self, position):
        """Is the position within the bounds of the map"""
        return all([x >= 0 and x < IJ_SIZE for x in position])

    def register_room(self, room):
        # Register positions occupied by this room
        used = room.get_positions()
        # First, we need to check that ALL of those positions are
        # unoccupied.
        for position in used:
            if position in self.occupied:
                raise Exception("Occupado")
        # Otheriwse, all positions are fine to use.

        self.occupied = self.occupied.union(used)
        # Remove occupied positions from possibilities
        self.unoccupied = [(p, r, o) for (p, r, o) in self.unoccupied if p not in used]

        # Get doorways
        doors = room.get_doorways()
        for position in doors:
            # If that door position is not occupied by something else
            if position not in self.occupied and self.is_legal(position):
                # Get the orientation to the previous room
                orientation = self.getOrientationToManhattanRoom(position, used)
                # and cache in our doorway list
                self.unoccupied.append((position, room, orientation))

    def random_position(self):
        """Select a random doorway to use"""
        if len(self.occupied) > 0:
            return random.choice(self.unoccupied)
        else:
            raise Exception("No more space!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add trees to map')
    parser.add_argument('input', help='Input .mpz file')
    parser.add_argument('output', help='Output .mpz file')
    args = parser.parse_args()

    mymap = parse(args.input)
    v = VoxelWorld(size=2**7)

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
        possible_rooms =  [
            BaseRoom,
            # Corridor4way,
            SpawnRoom,
            JumpCorridor3,
            Corridor4way_A,
            Stair,
            Corridor2way,
            Corridor2way_A,
            AltarRoom,
            NLongCorridor,
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
    upm = UnusedPositionManager()

    # Insert a starting room. We move it vertically downward from center since
    # we have no way to build stairs downwards yet.
    starting_position = m(6, 6, 3)
    # We use the spawn room as our base starting room
    b = SpawnRoom(pos=starting_position, orientation="-x")
    # Register our new room
    upm.register_room(b)
    # Render it to the map
    b.render(v, mymap)

    room_count = 0
    while True:
        # Continualyl try and place rooms until we hit 200.
        if room_count > 200:
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
        print("[%s] Placing %s at %s (%s)" % (room_count, roomClass.__name__, position, orientation))
        # Initialize room, required to correctly calculate get_positions()
        r = roomClass(pos=position, **kwargs)
        # Try adding it
        try:
            # This step might raise an exception
            upm.register_room(r)
            # If we get here, we've placed successfully so bump count + render
            room_count += 1
            r.render(v, mymap)
        except Exception as e:
            # We have failed to register the room because
            # it does not fit here.
            # So, we continue.
            continue

    # Standard code to render octree to file.
    mymap.world = v.to_octree()
    mymap.world[0].octsav = 0
    mymap.write(args.output)
