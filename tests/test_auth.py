def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_signup_page(client):
    response = client.get("/signup")
    assert response.status_code == 200


def test_about_page(client):
    response = client.get("/about")
    assert response.status_code == 200


def test_invalid_login(client):
    response = client.post(
        "/login",
        data={
            "username": "wronguser",
            "password": "wrongpassword"
        },
        follow_redirects=True
    )

    assert response.status_code == 400



def test_diary_requires_login(client):
    response = client.get("/diary")

    # should redirect to login page
    assert response.status_code == 302


def test_profile_requires_login(client):
    response = client.get("/profile")

    # should redirect to login page
    assert response.status_code == 302