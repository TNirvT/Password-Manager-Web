def test_index(client):
    assert client.get("/").status_code == 200

home = "http://localhost/"
content = "http://localhost/content"

def _unlock_db(cli):
    # set master password, or unlock. and generate a master_key object
    resp = cli.post(
        "/login",
        data={"master_pw": "test123"}
    )
    assert resp.headers["Location"] == content

def test_login(client):
    assert client.get("/login").status_code == 405
    # database initialized and empty, attempts to create new master password
    _unlock_db(client)
    
    pw_samples = [
        ("wrong*password", home),
        ("test123", content),
    ]
    for sample in pw_samples:
        resp = client.get("/lock")
        assert resp.headers["Location"] == home
        resp = client.post(
            "/login",
            data={"master_pw": sample[0]}
        )
        assert resp.headers["Location"] == sample[1]

def test_change_masterpw(client):
    assert client.get("/change_pw").status_code == 405
    _unlock_db(client)
    resp = client.post(
        "/change_pw",
        data={"master_pw": "test_new_pw"}
    )
    assert resp.headers["Location"] == content
    pw_samples = [
        ("wrong*password", home),
        ("test123", home),
        ("test_new_pw", content),
    ]
    for sample in pw_samples:
        resp = client.get("/lock")
        assert resp.headers["Location"] == home
        resp = client.post(
            "/login",
            data={"master_pw": sample[0]}
        )
        assert resp.headers["Location"] == sample[1]

def test_content(client):
    _unlock_db(client)
    assert client.get("/content").status_code == 200

def test_search(client):
    url_samples=[
        ("", content),
        (" ", content),
        ("abc.com", "http://localhost/add/abc.com"),
        ("abc.com/login/user", "http://localhost/add/abc.com"),
        ("something.io", "http://localhost/add/something.io"),
        ("thisthat.xyz", "http://localhost/add/thisthat.xyz"),
    ]
    for sample in url_samples:
        resp = client.post(
            "/search",
            data={"url_read": sample[0]}
        )
        assert resp.headers["Location"] == sample[1]
    
    _unlock_db(client)
    resp = client.post(
        "/insert_db/sillydomainname.com",
        data={
            "url_read": "sillydomainname.com",
            "password": ""}
    )
    assert resp.headers["Location"] == content + "/1001"
    resp = client.post(
        "/search",
        data={"url_read": "sillydomainname.com"}
    )
    assert resp.headers["Location"] == content + "/1001"
    resp = client.get("/content/1001")
    assert resp.status_code == 200
    result_pw = resp.data.split(b"""id="btn-copyPass" value=""")[1].split(b""">Copy Password""")[0]

    resp = client.post(
        "/generate_new",
        data={"generate_new": 1001}
    )
    result_pw_new = resp.data.split(b"""id="btn-copyPass" value=""")[1].split(b""">Copy Password""")[0]
    assert result_pw != result_pw_new

    resp = client.get("/update/1001")
    assert resp.status_code == 200

    resp = client.post(
        "/update_db/1001",
        data={
            "login": "new@email.com",
            "password": "",
        }
    )
    assert resp.headers["Location"] == content + "/1001"
    resp = client.get("/content/1001")
    assert b'new@email.com' in resp.data