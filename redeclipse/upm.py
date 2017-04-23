import math
import sys
import random
import copy
from redeclipse.cli import weighted_choice


class UnusedPositionManager:
    """Class for maintaining a quick-lookup list of which 8x8x8 cubes are in-use

    This is closely tied to our prefab model
    """
    def __init__(self, world_size, mirror=False):
        # Set of occupied positions
        self.occupied = set()
        # Set of doors that we can connect to
        self.unoccupied = []
        self.world_size = world_size
        # Special restrictions on mirror-mode
        self.mirror = mirror

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
        lowest = 0
        if self.mirror:
            lowest = 8
        return all([x >= lowest and x < self.world_size - 8 for x in position])

    def preregister_rooms(self, *rooms):
        # Register positions occupied by this room
        tmp_occupied = copy.deepcopy(self.occupied)
        for room in rooms:
            used = room.get_positions()
            # First, we need to check that ALL of those positions are
            # unoccupied.
            for position in used:
                if position in tmp_occupied:
                    return False
            tmp_occupied = tmp_occupied.union(used)
        return True

    def register_room(self, room):
        # Register positions occupied by this room
        used = room.get_positions()
        # First, we need to check that ALL of those positions are
        # unoccupied.
        for position in used:
            if position in self.occupied:
                raise Exception("Occupado %s %s %s" % position)
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

    def nrp_flavour_center_hole(self, x, y, z):
        return math.pow(z, 5) #+ math.log10(math.pow(x, 4))

    def nonrandom_position(self, flavour_function):
        """Non-randomly select doorway to use"""
        choices = [
            (idx, flavour_function(*posD[0]))
            for idx, posD in enumerate(self.unoccupied)
        ]

        if len(self.occupied) > 0:
            return self.unoccupied[weighted_choice(choices)]
        else:
            raise Exception("No more space!")
