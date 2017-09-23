import random
from redeclipse import MapParser


def parse(input):
    mp = MapParser()
    return mp.read(input)


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
    return None


def random_room(connecting_room, room_options):
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

    return weighted_choice(choices)
