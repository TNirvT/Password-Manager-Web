import string
from random import choice, randint, sample

# default values
pw_config = {
    "length_min": 10,
    "length_max": 14,
    "caps_min": 1,
    "caps_max": 3,
    "num_min": 2,
    "num_max": 3
}

def phrase_gen(min_len, max_len):
    characters = string.ascii_letters + string.digits
    phrase =  "".join(choice(characters) for x in range(randint(min_len, max_len)))
    return phrase

# empty input: password may include the most common punctuations
# punctuations-only input: password with these input choices
# mixed input: directly return input as password
def pwgen(in_put):
    in_put = str(in_put).replace(" ","")
    if in_put != "" and not _allpunct(in_put):
        return pwgen_direct_input(in_put)
    if in_put == "":
        return pwgen_general()
    else:
        return pwgen_custom_punct(in_put)

def _allpunct(in_put):
    for chara in in_put:
        if chara not in string.punctuation:
            return False
    return True

def pwgen_direct_input(in_put):
    if len(in_put) < pw_config["length_min"]:
        raise ValueError(f"Direct input password must be {pw_config['length_min']} characters or longer.")
    return in_put

def _pwgen_base(pw_punct):
    pw_length = randint(pw_config["length_min"], pw_config["length_max"])
    pw_uppercase = "".join(choice(string.ascii_uppercase) for _ in range(randint(1,3)))
    pw_numbers = "".join(choice(string.digits) for _ in range(randint(2,3)))
    pw_low = "".join(choice(string.ascii_lowercase) for _ in range(pw_length-len(pw_uppercase)-len(pw_numbers)-len(pw_punct)))
    return "".join(sample(pw_uppercase+pw_low+pw_numbers+pw_punct, pw_length))

def pwgen_general():
    pw_punct = "".join(choice("!@#$%^&*-_+=<>,./?") for _ in range(randint(1, 3)))
    return _pwgen_base(pw_punct)

def pwgen_custom_punct(in_put):
    pw_punct = "".join(choice(in_put) for _ in range(randint(1,3)))
    return _pwgen_base(pw_punct)