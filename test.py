def test_rec(a):
    if a is not None:
        a += 1
    else:
        print("a is None")
    if a == 10:
        a -= 100
        return None

    