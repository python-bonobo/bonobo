from bonobo.structs.tokens import Token


def test_token_repr():
    t = Token("Acme")
    assert repr(t) == "<Acme>"
