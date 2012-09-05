def dict_array_equal(d1, d2):
    # Compares two dicts that have v
    for k, v in d1.iteritems():
        d1[k] = sorted(v)
    for k, v in d2.iteritems():
        d2[k] = sorted(v)
    assert d1 == d2
