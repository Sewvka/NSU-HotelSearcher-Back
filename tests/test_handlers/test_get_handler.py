from uuid import uuid4


async def test_get_user(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "email": "lol@kek.com",
        "password": "SampleHashedPass",
    }
    await create_user_in_database(**user_data)
    resp = client.get(
        f"/user/?user_id={user_data['user_id']}",
    )
    assert resp.status_code == 200
    user_from_response = resp.json()
    assert user_from_response["user_id"] == str(user_data["user_id"])
    assert user_from_response["email"] == user_data["email"]
