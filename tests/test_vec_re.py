import pytest
from redeclipse.vector.re import ivec2, vec2, ivec3, vec3, cross


def test_ivec2():
    q = ivec2(1, 1.5)
    assert q.X() == 1
    assert q.Y() == 1
    w = q.to_dict()
    assert w[0] == 1
    assert w[1] == 1

def test_vec2():
    q = vec2(1, 1.5)
    assert q.X() == 1
    assert q.Y() == 1.5
    w = q.to_dict()
    assert w[0] == 1
    assert w[1] == 1.5


def test_ivec3():
    q = ivec3(1, 1.5, 1)
    assert q.X() == 1
    assert q.Y() == 1
    assert q.Z() == 1
    w = q.to_dict()
    assert w[0] == 1
    assert w[1] == 1
    assert w[2] == 1

    assert q.gg(0) == 1
    assert q.gg(1) == 1
    assert q.gg(2) == 1

def test_vec3():
    q = vec3(1, 1.5, 1)
    assert q.X() == 1
    assert q.Y() == 1.5
    assert q.Z() == 1
    w = q.to_dict()
    assert w[0] == 1
    assert w[1] == 1.5
    assert w[2] == 1

def test_cross():
    q = ivec3(1, 2, 3)
    w = ivec3(3, 2, 1)

    a = cross(q, w)
    b = ivec3(-4, 8, -4)
    assert a.X() == b.X() and a.Y() == b.Y() and a.Z() == b.Z()
