import pytest
from redeclipse.vector import rotate_yaw, BaseVector, AbsoluteVector, CoarseVector, FineVector


def test_rotate():
    assert rotate_yaw(0, '+x') == 0
    assert rotate_yaw(90, '+x') == 90
    assert rotate_yaw(180, '+x') == 180
    assert rotate_yaw(270, '+x') == 270
    assert rotate_yaw(360, '+x') == 0
    assert rotate_yaw(450, '+x') == 90

    assert rotate_yaw(0, '+y') == 90
    assert rotate_yaw(90, '+y') == 180
    assert rotate_yaw(180, '+y') == 270
    assert rotate_yaw(270, '+y') == 0
    assert rotate_yaw(360, '+y') == 90
    assert rotate_yaw(450, '+y') == 180

    assert rotate_yaw(0, '-x') == 180
    assert rotate_yaw(90, '-x') == 270
    assert rotate_yaw(180, '-x') == 0
    assert rotate_yaw(270, '-x') == 90
    assert rotate_yaw(360, '-x') == 180
    assert rotate_yaw(450, '-x') == 270

    assert rotate_yaw(0, '-y') == 270
    assert rotate_yaw(90, '-y') == 0
    assert rotate_yaw(180, '-y') == 90
    assert rotate_yaw(270, '-y') == 180
    assert rotate_yaw(360, '-y') == 270
    assert rotate_yaw(450, '-y') == 0

    with pytest.raises(Exception):
        assert rotate_yaw(450, 'y') == 0


def test_basevector():
    for Class in (BaseVector, AbsoluteVector, CoarseVector, FineVector):
        v = Class(4, 2, 1)
        w = Class(4, 2, 1)
        u = Class(2, 4, 1)

        x = Class(1, 0, 0)
        y = Class(0, 1, 0)
        z = Class(0, 0, 1)

        # TODO: broken hash?
        exp = 4 << 20 + 2 << 10 + 1
        print(hash(v), exp)
        # assert hash(v) == exp
        assert v == w
        assert v != u

        # Multiplications
        assert x * 4 == Class(4, 0, 0)
        assert y * 2 == Class(0, 2, 0)
        # Mult + Additions
        assert x * 4 + y * 2 + z * 1 == v
        # Mult + Sub
        assert v - x * 3 - y * 2 - z * 1 == x

        # Rotations
        assert v.rotate('+x') == v
        assert v.rotate(0) == v
        assert v.rotate(360) == v
        assert v.rotate('+y') == v.rotate(90)
        assert v.rotate('-x') == v.rotate(90).rotate(90)
        assert v.rotate('-y') == v.rotate(90).rotate(90).rotate(90)

        with pytest.raises(Exception):
            assert x.a is False

        with pytest.raises(Exception):
            assert x - 3

        with pytest.raises(Exception):
            assert x + 3

        with pytest.raises(Exception):
            assert x[4]

        assert v.rotate(90) == v.rotate(90 - 360)

    assert CoarseVector(1, 1, 1) == FineVector(8, 8, 8)
    assert FineVector(8, 8, 8) == CoarseVector(1, 1, 1)
