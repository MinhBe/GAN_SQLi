from gansqli.core import canonicalize_text, stable_hash

def test_canonicalize():
    assert canonicalize_text(' A   B ') == 'a b'

def test_hash():
    assert stable_hash('abc','p').startswith('p_')
