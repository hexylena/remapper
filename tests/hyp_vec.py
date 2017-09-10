from redeclipse.vector import rotate_yaw, BaseVector, AbsoluteVector, CoarseVector, FineVector
from hypothesis import given
import hypothesis.strategies as st


@given(st.integers(), st.integers())
def test_vec_addition(a, b):
    x = BaseVector(a, a, a)
    y = BaseVector(b, b, b)
    z = BaseVector(a + b, a + b, a + b)
    assert x + y == z

@given(st.integers(), st.integers())
def test_vec_mul(a, b):
    x = BaseVector(a, a, a)
    z = BaseVector(a * b, a * b, a * b)
    assert x * b == z

if __name__ == '__main__':
    test_vec_addition()
    test_vec_mul()
