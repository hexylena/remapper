import copy
from collections import OrderedDict
from tqdm import tqdm
import math
import random
from redeclipse.vector import CoarseVector
from redeclipse.vector.orientations import EAST, CARDINALS
from redeclipse.prefabs import TestRoom
import logging
log = logging.getLogger(__name__)


class UnusedPositionManager:
    """Class for maintaining a quick-lookup list of which 8x8x8 cubes are in-use

    This is closely tied to our prefab model
    """

    def __init__(self, world_size, mirror=1, noclip=False):
        # Disable occupation tests.
        self.noclip = noclip
        # Set of occupied positions
        self.occupied = set()
        # Set of doors that we can connect to
        self.unoccupied = []
        self.world_size = world_size
        # Mirror mode, only defined for values 1, 2, 4
        self.mirror = mirror
        if self.mirror == 1:
            self.mirror_rotations = [0]
        elif self.mirror == 2:
            self.mirror_rotations = [0, 180]
        elif self.mirror == 4:
            self.mirror_rotations = [0, 90, 180, 270]

    def is_legal(self, position):
        """Is the position within the bounds of the map.

        :param position: A vector representing the position of the room
        :type position: `redeclipse.vector.CoarseVector`

        :returns: Whether or not that position is legal to occuply.
        :rtype: boolean
        """
        # TODO: dependent on world size.
        return 0 <= position.x <= 32 and \
            0 <= position.y <= 32 and \
            0 <= position.z <= 32

    def _yield_mirrored(self, room):
        for orientation in self.mirror_rotations:
            room_copy = copy.deepcopy(room)
            # Offset rotate around the center of the map
            room_copy.pos = room_copy.pos.offset_rotate(orientation, offset=CoarseVector(-16, -16, 0))
            room_copy.orientation = room_copy.orientation.rotate(orientation)
            yield room_copy

    def preregister_room(self, room):
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
        new_rooms = self._yield_mirrored(room)
        return self._preregister_room(new_rooms)

    def _preregister_room(self, rooms):
        # logging.info("Prereg: %s", '|'.join([x.__class__.__name__ for x in rooms]))
        added_occupied = set()
        for room in rooms:
            used = room.get_positions()
            # First, we need to check that ALL of those positions are
            # unoccupied.
            for position in used:
                if position in self.occupied or position in added_occupied:
                    return False
            added_occupied = added_occupied.union(set(used))
            # Don't add the room if the door is off the edge.
            for door in room.get_doorways():
                if not self.is_legal(door['offset']):
                    return False
        return True

    def register_room(self, room):
        """
        Register positions occupied by this room

        :param room: A single room that is to be added to the world.
        :type room: redeclipse.prefabs.Room

        :rtype: None
        """
        for r in self._yield_mirrored(room):
            self._register_room(r)
            yield r

    def _register_room(self, room):
        used = room.get_positions()
        # First, we need to check that ALL of those positions are
        # unoccupied.
        for position in used:
            if position in self.occupied and not self.noclip:
                raise Exception("Occupado %s" % position)
        # Otherwise, all positions are fine to use.

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
            if self.is_legal(position['offset']) and not position['offset'] in self.occupied:
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
        wc = self.weighted_choice(choices)
        if len(self.unoccupied) > 0:
            return self.unoccupied[wc]
        else:
            raise Exception("No more space!")

    @classmethod
    def weighted_choice(cls, choices):
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
        return None

    def random_room(self, connecting_room, room_options):
        """Pick out a random room based on the connecting room and the
        transition probabilities of that room."""
        choices = []
        probs = connecting_room.get_transition_probs()
        for room in room_options:
            # Append to our possibilities
            choices.append((
                # The room, and the probability of getting that type of room
                # based on the current room type
                room, probs.get(room.room_type, 0.1)
            ))
        return self.weighted_choice(choices)

    def random_room_stream(self, connecting_room, room_options):
        # We need to get the complete set of rooms, in a randomly shuffled
        # fashion. Previously we'd just try again and again on a position to
        # fit a room on there. Sometimes this would succeed, sometimes it would
        # failure and we'd have unbounded execution time.
        choices = []
        probs = connecting_room.get_transition_probs()

        # We'll need integer probabilities for the shuffling, so use min and mult everything.
        minimum_prob = min([probs.get(room.room_type, 0.1) for room in room_options])

        for room in room_options:
            # Number of times we'd like to see this room.
            frequency = int(probs.get(room.room_type, 0.1) / minimum_prob)
            # Append that many rooms
            for n in range(frequency):
                choices.append(room)

        # >>> OrderedDict([(x,  True) for x in [1,2,23,3,5,34,5,5, 6]])
        # OrderedDict([(1, True), (2, True), (23, True), (3, True), (5, True), (34, True), (6, True)])

        # Now that we've got a set of rooms with many dupes, we'll shuffle it.
        choices = OrderedDict([(room, True) for room in random.sample(choices, len(choices))]).keys()
        return choices

    def room_localization(self, possible_rooms, prev_room_door, prev_room, prev_room_orientation):
        """
        Given a set of possible rooms, this will randomly choose a
        location, and emit a stream of orientations for rooms that could
        be attached.
        """

        # If we are here, we do have a position + orientation to place in
        # Get the COMPLETE set of rooms, influenced by the prev_room
        for roomClass in self.random_room_stream(prev_room, possible_rooms):
            # We loop over a (random permutation) of the possible orientations in
            # order to identify at least one with a plausible door. Shuffling *may*
            # not be necessary but it doesn't hurt anything.
            for orientation in random.sample(CARDINALS, 4):
                kwargs = {'orientation': orientation}
                # Initialize room, required to correctly calculate get_positions()/get_doorways()
                r = roomClass(pos=CoarseVector(2, 2, 3), **kwargs)
                # We've already picked a prev_room_door (and we know its orientation)
                # Now we pick a door on the new room we'll place.
                roomClass_doors = r.get_doorways()
                # Find a door that is facing in the opposite direction as prev_room_orientation
                options = [x for x in roomClass_doors if x['orientation'] == prev_room_orientation.rotate(180)]
                # If we don't have any options, continue, let's try a different orientation.
                if len(options) == 0:
                    continue
                # If we do have doors though, choose a door on our new room that's
                # in the correct orientation
                for chosen_door in options:
                    # Room offset
                    room_offset = chosen_door['offset'] - prev_room_door + prev_room_orientation
                    # Add our random options
                    kwargs.update(roomClass.randOpts(prev_room))
                    # Last, we yield all possible versions of this room (in case
                    # some of them don't fit.)
                    r = roomClass(pos=CoarseVector(2, 2, 3) - room_offset, **kwargs)
                    # If the room can be registered in this position, safely, ONLY
                    # then do we yield it.
                    if self.preregister_room(r):
                        yield r

    def _room_cap_debug(self, pos, typ, ori):
        return TestRoom(pos, orientation=EAST)

    def _room_cap_real(self, prev_room_door, prev_room, prev_room_orientation, possible_endcaps=None):
        # Pick a random room class
        for roomClass in random.sample(possible_endcaps, len(possible_endcaps)):
            # Test all the orientations
            for c in CARDINALS:
                r = roomClass(pos=CoarseVector(2, 2, 3), orientation=c)
                # There will only be one door.
                roomClass_doors = r.get_doorways()
                options = [x for x in roomClass_doors if x['orientation'] == prev_room_orientation.rotate(180)]
                if len(options) == 0:
                    continue
                chosen_door = options[0]
                room_offset = chosen_door['offset'] - prev_room_door + prev_room_orientation
                r = roomClass(pos=CoarseVector(2, 2, 3) - room_offset, orientation=c)
                # Make sure it fits!
                for pos in r.get_positions():
                    if not self.is_legal(pos) and pos not in self.occupied:
                        continue
                return r

    def endcap(self, debug=False, possible_endcaps=[]):
        if debug:
            for (pos, typ, ori) in tqdm(self.unoccupied):
                yield self._room_cap_debug(pos, typ, ori)
        else:
            for (pos, typ, ori) in tqdm(self.unoccupied):
                r = self._room_cap_real(pos, typ, ori, possible_endcaps=possible_endcaps)
                if r:
                    yield r

    def place_rooms(self, v, mymap, debug, possible_rooms, rooms=10):
        room_count = 0
        logging.info("Placing rooms")
        with tqdm(total=rooms) as pbar:
            while True:
                # Continually try and place rooms until we hit 200.
                if room_count >= rooms:
                    logging.info("Placed enough rooms")
                    break

                if len(self.unoccupied) == 0:
                    logging.info("Ran out of unoccupied positions")
                    break

                # Pick a random position for this notional room to go
                (prev_room_door, prev_room, prev_room_orientation) = self.nonrandom_position(self.nrp_flavour_vertical)
                for r in self.room_localization(possible_rooms, prev_room_door, prev_room, prev_room_orientation):
                    to_render = self.register_room(r)
                    [m.render(v, mymap) for m in to_render]

                    pbar.update(self.mirror)
                    pbar.set_description('z:%3d u:%d o:%d' % (v.zmax, len(self.unoccupied), len(self.occupied)))
                    # If we get here, we've placed successfully so bump count + render
                    room_count += self.mirror
                    # After we place the first one, break out of this
                    # for loop since the rest of the options are just
                    # different orientations of the same thing.
                    break
                else:
                    # There are NO rooms which fit here, so we need to remove
                    # this from our positions so we don't bother trying again.
                    self.unoccupied = [
                        (d, r, o) for (d, r, o) in self.unoccupied
                        if (d, r, o) != (prev_room_door, prev_room, prev_room_orientation)
                    ]
                    logging.info("No rooms fit here, removing")
