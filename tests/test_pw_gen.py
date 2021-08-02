import pytest
from website import pw_gen

def test_phrase():
    for _ in range(1000):
        min_len = 2
        max_len = 100
        result = pw_gen.phrase_gen(min_len,max_len)
        assert isinstance(result, str)
        assert len(result) >= min_len and len(result) <= max_len

@pytest.mark.parametrize("sample",[" ", "       "])
def test_pw_space(sample):
    for _ in range(1000):
        result = pw_gen.pwgen(sample)
        assert " " not in result
        assert isinstance(result, str)
        assert len(result) >= pw_gen.pw_config["length_min"] and len(result) <= pw_gen.pw_config["length_max"]

@pytest.mark.parametrize("sample",["  12345abcde  ", "  @#$1234abc  "])
def test_pw_directinput(sample):
    result = pw_gen.pwgen(sample)
    assert " " not in result
    assert isinstance(result, str)
    assert sample.replace(" ","") == result

@pytest.mark.parametrize("sample",["12@", " @#$abc123"])
def test_pw_ditectinput_error(sample):
    with pytest.raises(ValueError):
        pw_gen.pwgen(sample)