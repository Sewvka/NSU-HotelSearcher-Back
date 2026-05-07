import json

import pytest


async def test_create_user(client, get_user_from_database):
    user_data = {
        "email": "some.email@mail.ru",
        "password": "123"
    }
    resp = client.post("/user/", data=json.dumps(user_data))
    data_from_resp = resp.json()
    assert resp.status_code == 200
    assert data_from_resp["email"] == user_data["email"]
    user_from_db = await get_user_from_database(data_from_resp["user_id"])
    assert len(user_from_db) == 1
    user_from_db = dict(user_from_db[0])
    assert user_from_db["email"] == user_data["email"]
    assert str(user_from_db["user_id"]) == data_from_resp["user_id"]
