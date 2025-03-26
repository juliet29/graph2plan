from hypothesis import given, example, strategies as st
from sympy import Line
from math import radians, cos, sin
import pytest


def create_point_from_angle(degree_angle:float):
    rad = radians(degree_angle)
    return (cos(rad), sin(rad))

@st.composite
def generate_angles(draw):
    deg_near =  draw(st.integers(min_value=0, max_value=350))
    deg_far =  draw(st.integers(min_value=deg_near+1, max_value=360))
    return deg_near, deg_far

# @st.composite
# def generate_points(draw):
#     deg_near =  draw(st.integers(min_value=0, max_value=350))
#     deg_far =  draw(st.integers(min_value=deg_near+1, max_value=360))
#     return deg_near, deg_far


@pytest.mark.skip(reason="Need to generate points instead of angles, but then have to test a bunch of cases...")
@given(input=generate_angles())
@example((8, 172))
def test_smallest_angle_between(input):
    deg_near, deg_far = input
    v_near, v_far = (create_point_from_angle(i) for i in (deg_near, deg_far))

    u = (0,0)
    v0 = (0,1)
    (lbase, lnear, lfar) = (Line(u, v0), Line(u, v_near), Line(u, v_far) )
    assert lbase
    assert lbase.smallest_angle_between(lnear) <= lbase.smallest_angle_between(lfar) # type: ignore
