import os
import tempfile

def test_master():
    # override the db_path
    from website import master_key as mk

    master_key = mk.MasterKey(None)
    master_key.salt_fd, master_key.salt_path = tempfile.mkstemp()

    pw_samples = [
        ""
        " ",
        "       ",
        " 1234 ",
        " 1234567 ",
        "123456"
    ]
    for pw_sample in pw_samples:
        encrypted_secret = master_key.set_pw(pw_sample)
        assert isinstance(encrypted_secret, bytes)
        assert master_key.unlock(pw_sample, encrypted_secret)

    os.close(master_key.salt_fd)
    os.unlink(master_key.salt_path)