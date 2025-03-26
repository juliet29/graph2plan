from graph2plan.dcel.examples import deberg_embedded, deberg
from graph2plan.dcel.create import (
    create_embedding
)


def test_deberg():
    known_embedding = deberg_embedded()
    G, pos = deberg()

    computed_embedding = create_embedding(G, pos)

    assert known_embedding.traverse_face(1,2) == computed_embedding.traverse_face(1,2)
    assert known_embedding.traverse_face(4,3) == computed_embedding.traverse_face(4,3)