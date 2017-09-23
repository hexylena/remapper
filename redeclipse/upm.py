import math
import random
import copy
from redeclipse.cli import weighted_choice
from redeclipse.vector.orientations import NORTH, SOUTH, EAST, WEST
import logging


class UnusedPositionManager:
    """Class for maintaining a quick-lookup list of which 8x8x8 cubes are in-use

    This is closely tied to our prefab model
    """
    def __init__(self, world_size, mirror=False, noclip=False):
        # Disable occupation tests.
        self.noclip = noclip
        # Set of occupied positions
        self.occupied = set()
        # Set of doors that we can connect to
        self.unoccupied = []
        self.world_size = world_size
        # Special restrictions on mirror-mode
        self.mirror = mirror

    def is_legal(self, position):
        """Is the position within the bounds of the map.

        :param position: A vector representing the position of the room
        :type position: `redeclipse.vector.CoarseVector`

        :returns: Whether or not that position is legal to occuply.
        :rtype: boolean
        """
        return 0 <= position.x <= 16 and \
            0 <= position.y <= 16 and \
            0 <= position.z <= 16

    def preregister_rooms(self, *rooms):
        """
        Register positions occupied by this room, but don't *actually*
        do it, only attempt to do it in a temporary manner. Useful for
        validating that multi-room rooms work OK even under mirrored
        circumstances.

        :param rooms: An array of redeclipse.prefabs.Room that are to be pre-registered.
        :type rooms: list(redeclipse.prefabs.Room)

        :returns: Whether or not it is OK to register this room.
        :rtype: boolean
        """
        # logging.info("Prereg: %s", '|'.join([x.__class__.__name__ for x in rooms]))
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

        :param room: A single room that is to be added to the world.
        :type room: redeclipse.prefabs.Room

        :rtype: None
        """
        used = room.get_positions()
        # print('used', used)
        # First, we need to check that ALL of those positions are
        # unoccupied.
        # logging.info("Registering %s which occupies %s", room.__class__.__name__, '|'.join(map(str, used)))
        for position in used:
            if position in self.occupied and not self.noclip:
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
            # logging.info("  pos: %s => leg:%s occ:%s", position['offset'], self.is_legal(position['offset']), position['offset'] in self.occupied)
            # If that door position is not occupied by something else
            if self.is_legal(position['offset']):
                # and cache in our doorway list
                self.unoccupied.append((position['offset'], room, position['orientation']))

    def random_position(self):
        """Select a random doorway to use

        :returns: a doorway from the set of unoccupied doorways.
        :rtype: tuple of (position, room, orientation), whatever the heck those are.
        """
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
        # TODO: dependent on self.size
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

    def mirror(cls, d):
        if isinstance(d, dict):
            d['orientation'] = d['orientation'].rotate(180)
            return d
        else:
            return CoarseVector(
                room_counts - d[0],
                room_counts - d[1],
                d[2]
            )
