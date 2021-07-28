from website import pw_gen

def test_phrase():
    for _ in range(1000):
        min_len = 2
        max_len = 100
        result = pw_gen.phrase_gen(min_len,max_len)
        assert isinstance(result, str)
        assert len(result) >= min_len and len(result) <= max_len

def test_pw_space():
    samples = [
        " ",
        "                                ",
    ]
    for sample in samples:
        for _ in range(1000):
            result = pw_gen.pwgen(sample)
            assert " " not in result
            assert isinstance(result, str)

def test_pw_directinput():
    samples = [
        "  123abc  ",
        "  @#$123abc  "
    ]
    for sample in samples:
        for _ in range(1000):
            result = pw_gen.pwgen(sample)
            assert " " not in result
            assert isinstance(result, str)
            assert sample.replace(" ","") == result