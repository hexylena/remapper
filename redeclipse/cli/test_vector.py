#!/usr/bin/env python
import argparse
import random
import logging
from redeclipse.voxel import VoxelWorld
from redeclipse.cli import parse, weighted_choice
from redeclipse.entities import Sunlight
from redeclipse import prefabs as p
from redeclipse.upm import UnusedPositionManager
#from redeclipse.skybox import MinecraftSky
from redeclipse.prefabs import StartingPosition
from redeclipse.prefabs.vector import CoarseVector
from tqdm import tqdm
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(mpz_in, mpz_out, size=2**7, seed=42, rooms=200, debug=False):
    random.seed(seed)
    mymap = parse(mpz_in.name)
    v = VoxelWorld(size=size)
    room_counts = 32

    def mirror(d):
        if isinstance(d, dict):
            if '-' in kwargs['orientation']:
                kwargs['orientation'] = kwargs['orientation'].replace('-', '+')
            else:
                kwargs['orientation'] = kwargs['orientation'].replace('+', '-')
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
        possible_rooms = [
            p.BaseRoom,
            p.SpawnRoom,
            p.JumpCorridor3,
            p.JumpCorridorVertical,
            #p.Stair,
            #p.DigitalRoom,
            #p.JumpCorridorVerticalCenter,
            #p.PlusPlatform,

            p.NLongCorridor,
            #p.FlatSpace,
            #p.DoricTemple,
            #p.ImposingRingRoom,
            #p.ImposingBlockRoom,
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
    upm = UnusedPositionManager(size, mirror=True)

    # Insert a starting room. We move it vertically downward from center since
    # we have no way to build stairs downwards yet.
    starting_position = StartingPosition
    # We use the spawn room as our base starting room
    orientations = ['+x', '+y', '-x', '-y']

    for i in range(32):
        b = p.SpawnRoom(pos=CoarseVector(i, i, i), orientation=orientations[i % 4])
        upm.register_room(b)
        b.render(v, mymap)

    sunlight = Sunlight(
        red=128,
        green=128,
        blue=128,
        offset=45, # top
    )
    mymap.ents.append(sunlight)

    if debug:
        for (pos, typ, ori) in upm.unoccupied:
            r = p.TestRoom(pos, orientation='+x')
            r.render(v, mymap)

    # Emit config + textures
    p.TEXMAN.emit_conf(mpz_out)
    p.TEXMAN.copy_data()

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

