from netutils import *
from worker import *


def test_is_alive():
    assert(is_alive("8.8.8.8"))
    assert(is_alive("127.0.0.1"))
    assert(not is_alive("128.0.0.1"))


def prime_tests():
    w = Worker()
    assert(w._is_prime(7))
    assert(w._is_prime(3))
    assert(w._is_prime(199))

    assert(not w._is_prime(8))
    assert(not w._is_prime(10))
    assert(not w._is_prime(200))

def tests():
    test_is_alive()
    prime_tests()
    print("Tests passed")


