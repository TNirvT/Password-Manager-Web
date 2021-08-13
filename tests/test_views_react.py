import pytest
import json

def test_index(client):
    assert client.get("/").status_code == 200

home = "http://localhost/"
content = "http://localhost/content_react"

def _unlock_db(cli):
    # set master password, or unlock. and generate a master_key object
    resp = cli.post(
        "/login",
        data={"master_pw": "test123"}
    )
    assert resp.headers["Location"] == content

@pytest.mark.parametrize("pw_sample,expected", [
    ("wrong*password", home),
    ("test123", content)
])
def test_login(client, pw_sample, expected):
    assert client.get("/login").status_code == 405
    # database initialized and empty, attempts to create new master password
    _unlock_db(client)
    
    resp = client.get("/lock")
    assert resp.headers["Location"] == home
    resp = client.post(
        "/login",
        data={"master_pw": pw_sample}
    )
    assert resp.headers["Location"] == expected

@pytest.mark.parametrize("pw_sample,expected", [
    ("wrong*password", home),
    ("test123", home),
    ("test_new_pw", content)
])
def test_change_masterpw(client, pw_sample, expected):
    assert client.get("/change_pw").status_code == 405
    _unlock_db(client)
    resp = client.post(
        "/change_pw",
        data={"master_pw": "test_new_pw"}
    )
    assert resp.headers["Location"] == content
    resp = client.get("/lock")
    assert resp.headers["Location"] == home
    resp = client.post(
        "/login",
        data={"master_pw": pw_sample}
    )
    assert resp.headers["Location"] == expected

def test_content(client):
    _unlock_db(client)
    assert client.get("/content_react").status_code == 200

# @pytest.mark.parametrize("url_sample,expected,http_code", [
#     ("", b"Invalid URL", 400),
#     (" ", b"Invalid URL", 400),
#     ("abc.com", b"abc.com", 200),
#     ("abc.com/login/user", b"abc.com", 200),
#     ("something.io", b"something.io", 200),
#     ("thisthat.xyz", b"thisthat.xyz", 200)
# ])
# def test_search(client, url_sample, expected, http_code):
#     _unlock_db(client)
#     resp = client.get(
#         "/search_react",
#         query_string=url_sample,
#     )
#     assert expected in resp.data

def test_search_by_flow(client):
    _unlock_db(client)
    resp = client.post(
        "/insert_db_react",
        data=json.dumps({
            "url": "sillydomainname.com",
            "login": "",
            "remark": "",
            "password": ""
        }),
        content_type="application/json"
    )
    assert b'sillydomainname.com' in resp.get_data()
    
    resp = client.get(
        "/search_react",
        query_string="url_read=sillydomainname.com"
    )
    assert b'1001' in resp.data
    resp = client.get("/search_react/1001")
    assert resp.status_code == 200
    result_pw = resp.get_json()["password"]

    resp = client.post(
        "/generate_new_react",
        data=json.dumps({"generate_new": 1001}),
        content_type="application/json"
    )
    result_pw_new = resp.get_json()["password"]
    assert result_pw != result_pw_new

    resp = client.post(
        "/update_db_react",
        data=json.dumps({
            "id": 1001,
            "login": "new@email.com",
            "remark": "",
            "password": "",
        }),
        content_type="application/json"
    )
    assert resp.headers["Location"] == "http://localhost/search_react/1001"
    resp = client.get("/search_react/1001")
    assert b'new@email.com' in resp.data