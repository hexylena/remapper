import math
import random
import copy
from redeclipse.cli import weighted_choice
import logging


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

        :param used: array of used positions
        :type used: list

        :param p: previous room
        :type p: ???
        """
        for u in used:
            # For a set of "used" positions, only ONE block should be directly
            # next to the previous one (we don't do crazy U shaped things yet.)
            if u[1] == p[1]:
                # If the Y position is the same, must be in X direction
                if u[0] < p[0]:
                    return '+x'
                else:
                    return '-x'
            elif u[0] == p[0]:
                # If the X position is the same, must be in Y direction
                if u[1] < p[1]:
                    return '+y'
                else:
                    return '-y'
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
            lowest = 1
        return all([x >= lowest and x < 31 for x in position])

    def preregister_rooms(self, *rooms):
        """
        Register positions occupied by this room, but don't *actually*
        do it, only attempt to do it in a temporary manner.
        """
        logging.info("Prereg: %s", '|'.join([x.__class__.__name__ for x in rooms]))
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
        """
        Register positions occupied by this room
        """
        used = room.get_positions()
        # First, we need to check that ALL of those positions are
        # unoccupied.
        logging.info("Registering %s which occupies %s", room.__class__.__name__, '|'.join(map(str, used)))
        for position in used:
            print(position, self.occupied, position in self.occupied)
            if position in self.occupied:
                raise Exception("Occupado %s" % position)
        # Otheriwse, all positions are fine to use.

        self.occupied = self.occupied.union(used)
        # Remove occupied positions from possibilities
        self.unoccupied = [(p, r, o) for (p, r, o) in self.unoccupied if p not in used]

        # logging.info("  OCC: %s", list(map(str, self.occupied)))
        # logging.info("UNOCC: %s", list(map(str, self.unoccupied)))

        # Get doorways
        doors = room.get_doorways()
        # logging.info("DOORS: %s", list(map(str, doors)))
        for position in doors:
            # logging.info("  pos: %s %s", position, self.is_legal(position))
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
        """
        A 'flavour' which avoids placing rooms in the center

        :param x: x position
        :type x: int
        :param y: y position
        :type y: int
        :param z: z position
        :type z: int

        :returns: a float which should be applied as the probability of
                  chosing this position
        :rtype: float
        """
        tmpx = abs(x - 128)
        tmpy = abs(y - 128)
        return math.pow(tmpx, 5) + math.pow(tmpy, 5)

    def nrp_flavour_vertical(self, x, y, z):
        """
        A 'flavour' which strongly encourages verticality

        :param x: x position
        :type x: int
        :param y: y position
        :type y: int
        :param z: z position
        :type z: int

        :returns: a float which should be applied as the probability of
                  chosing this position
        :rtype: float
        """
        return math.pow(z, 5)

    def nrp_flavour_plain(self, x, y, z):
        """
        The base flavour which has no preferences

        :param x: x position
        :type x: int
        :param y: y position
        :type y: int
        :param z: z position
        :type z: int

        :returns: a float which should be applied as the probability of
                  chosing this position
        :rtype: float
        """
        return 1

    def nonrandom_position(self, flavour_function):
        """Non-randomly select doorway to use based on the flavour function.

        :param flavour_function: A function from this class (or a custom one)
        :type flavour_function: function
        """
        choices = [
            (idx, flavour_function(*posD[0]))
            for idx, posD in enumerate(self.unoccupied)
        ]

        wc = weighted_choice(choices)
        if len(self.occupied) > 0:
            return self.unoccupied[wc]
        else:
            raise Exception("No more space!")
