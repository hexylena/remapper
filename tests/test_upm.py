import pytest

from redeclipse.upm import UnusedPositionManager
from redeclipse.prefabs import Room
from redeclipse.vector import CoarseVector
from redeclipse.vector.orientations import NORTH, SOUTH, EAST, WEST


def test_upm():
    upm = UnusedPositionManager(16)
    with pytest.raises(Exception):
        upm.random_position()
    with pytest.raises(Exception):
        upm.nonrandom_position(upm.nrp_flavour_plain)

    room_a = Room(pos=CoarseVector(0, 0, 0))
    room_b = Room(pos=CoarseVector(16, 0, 0))

    assert not upm.is_legal(CoarseVector(-1, -1, -1))
    assert upm.is_legal(CoarseVector(0, 0, 0))
    assert upm.is_legal(CoarseVector(4, 4, 4))
    assert upm.is_legal(CoarseVector(16, 16, 16))
    assert not upm.is_legal(CoarseVector(33, 33, 33))

    # assert upm.preregister_room(room_a)
    # assert not upm.preregister_room(room_a, room_a)

    # upm.register_room(room_a)
    # with pytest.raises(Exception):
        # upm.register_room(room_a)

    # print(room_a.get_doorways())

    # assert len(upm.occupied) == 1
    # # [(CV(BV(1, 0, 0)), <redeclipse.prefabs.Room object at 0x7ff4ac1bbda0>, EAST), (CV(BV(0, 1, 0)), <redeclipse.prefabs.Room object at 0x7ff4ac1bbda0>, NORTH)]
    # assert len(upm.unoccupied) == 2

    # upm.register_room(room_b)
    # assert len(upm.occupied) == 2
    # assert len(upm.unoccupied) == 4
    # q = upm.random_position()
    # assert q in upm.unoccupied

    # q = upm.nonrandom_position(upm.nrp_flavour_plain)
    # assert q in upm.unoccupied

def test_flavours():
    upm = UnusedPositionManager(16)
    assert upm.nrp_flavour_center_hole(128, 128, 128) == 0
    assert upm.nrp_flavour_center_hole(129, 129, 129) == 2

    assert upm.nrp_flavour_vertical(0, 0, 0) == 0
    assert upm.nrp_flavour_vertical(0, 0, 1) == 1

    assert upm.nrp_flavour_plain(0, 0, 1) == 1
