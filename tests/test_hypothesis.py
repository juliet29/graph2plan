from hypothesis import given, strategies as st




@st.composite
def pair_gen(draw):
    a = draw(st.integers(0, 20))
    b = draw(st.integers(0, 20).map(lambda x: x + a))
    return (a, b)

@given(pair=pair_gen())
def test_generate_pair(pair):
    a, b = pair
    assert b >= a
