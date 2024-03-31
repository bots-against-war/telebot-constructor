import time

import aiohttp.web
from pytest_aiohttp.plugin import AiohttpClient  # type: ignore

from telebot_constructor.app import TelebotConstructorApp


async def test_get_logged_in_user(
    constructor_app: tuple[TelebotConstructorApp, aiohttp.web.Application],
    aiohttp_client: AiohttpClient,
) -> None:
    _, web_app = constructor_app
    client = await aiohttp_client(web_app)

    resp = await client.get("/api/logged-in-user")
    assert resp.status == 200
    assert await resp.json() == {
        "auth_type": "no_auth",
        "username": "no-auth",
        "name": "Anonymous user",
        "display_username": None,
        "userpic": None,
    }


async def test_bot_config(
    constructor_app: tuple[TelebotConstructorApp, aiohttp.web.Application],
    aiohttp_client: AiohttpClient,
) -> None:
    _, web_app = constructor_app
    client = await aiohttp_client(web_app)

    # saving secret
    bot_name = "test-bot-1312"
    resp = await client.post("/api/secrets/test-1312-token", data="token")
    assert resp.status == 200

    # saving first version of bot config
    bot_config_1 = {
        "token_secret_name": "test-1312-token",
        "user_flow_config": {"entrypoints": [], "blocks": [], "node_display_coords": {}},
    }
    resp = await client.post(
        f"/api/config/{bot_name}",
        json={
            "config": bot_config_1,
            "start": False,
            "version_message": "init message",
            "display_name": "my bot",
        },
    )
    assert resp.status == 201

    # checking that we can read it back
    resp = await client.get(f"/api/config/{bot_name}")
    assert resp.status == 200
    assert await resp.json() == bot_config_1

    # checking basic bot info
    resp = await client.get("/api/info")
    assert resp.status == 200
    resp_body = await resp.json()
    assert list(resp_body.keys()) == [bot_name]
    bot_info = resp_body[bot_name]
    assert bot_info["display_name"] == "my bot"
    assert bot_info["running_version"] is None
    versions = bot_info["last_versions"]
    assert len(versions) == 1
    version_index, version_meta = versions[0]
    assert version_index == 0
    assert time.time() - version_meta["timestamp"] < 1
    assert version_meta["message"] == "init message"
    assert len(bot_info["last_events"]) == 1
    bot_created_event = bot_info["last_events"][0]
    assert time.time() - bot_created_event["timestamp"] < 1
    assert bot_created_event["username"] == "no-auth"
    assert bot_created_event["event"] == "edited"
    assert bot_created_event["new_version"] == 0

    # starting bot
    resp = await client.post(f"/api/start/{bot_name}", json={"version": 0})
    assert resp.status == 201

    # checking info again, corresponding "started" event should be there
    resp = await client.get("/api/info")
    assert resp.status == 200
    resp_body = await resp.json()
    assert list(resp_body.keys()) == [bot_name]
    bot_info = resp_body[bot_name]
    assert bot_info["display_name"] == "my bot"
    assert bot_info["running_version"] == 0
    assert len(bot_info["last_versions"]) == 1
    assert len(bot_info["last_events"]) == 2
    assert bot_info["last_events"][0] == bot_created_event
    bot_started_events = bot_info["last_events"][1]
    assert time.time() - bot_started_events["timestamp"] < 1
    assert bot_started_events["username"] == "no-auth"
    assert bot_started_events["event"] == "started"

    # checking same info but with a bot-specific endpoint
    resp = await client.get(f"/api/info/{bot_name}")
    assert resp.status == 200
    resp_body = await resp.json()
    assert isinstance(resp_body, dict)
    assert resp_body["display_name"] == "my bot"
    assert resp_body["running_version"] == 0

    # update display name and check it's changed in the info
    resp = await client.put(f"/api/display-name/{bot_name}", json={"display_name": "changed display name"})
    assert resp.status == 200
    resp = await client.get(f"/api/info/{bot_name}")
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body["display_name"] == "changed display name"

    # updating bot config
    bot_config_2 = {
        "token_secret_name": "test-1312-token",
        "user_flow_config": {
            "entrypoints": [
                {
                    "command": {
                        "entrypoint_id": "123",
                        "command": "start",
                        "next_block_id": None,
                        "scope": "private",
                        "short_description": None,
                    },
                    "catch_all": None,
                    "regex": None,
                },
            ],
            "blocks": [],
            "node_display_coords": {},
        },
    }
    resp = await client.post(
        f"/api/config/{bot_name}",
        json={
            "config": bot_config_2,
            "start": True,
            "version_message": "bot config update",
        },
    )
    assert resp.status == 200

    # checking that it's saved indeed, however we request last version...
    for url in [f"/api/config/{bot_name}", f"/api/config/{bot_name}?version=-1", f"/api/config/{bot_name}?version=1"]:
        resp = await client.get(url)
        assert resp.status == 200
        assert await resp.json() == bot_config_2

    # ...but we can always retrieve the old version too!
    resp = await client.get(f"/api/config/{bot_name}?version=0")
    assert resp.status == 200
    assert await resp.json() == bot_config_1

    # and this update must be reflected in bot info
    resp = await client.get(f"/api/info/{bot_name}")
    assert resp.status == 200
    bot_info = await resp.json()
    assert bot_info["display_name"] == "changed display name"
    assert bot_info["running_version"] == 1
    assert len(bot_info["last_versions"]) == 2
    assert len(bot_info["last_events"]) == 5
    assert bot_info["last_events"][0] == bot_created_event
    assert bot_info["last_events"][1] == bot_started_events
    bot_edited_event, bot_stopped_event, bot_started_again_event = bot_info["last_events"][2:]
    for event in bot_info["last_events"]:
        assert time.time() - event["timestamp"] < 1
        assert event["username"] == "no-auth"
    assert bot_edited_event["event"] == "edited"
    assert bot_stopped_event["event"] == "stopped"
    assert bot_started_again_event["event"] == "started"

    # now let's stop the bot
    resp = await client.post(f"/api/stop/{bot_name}")
    assert resp.status == 200

    # check it's reflected in the info
    resp = await client.get(f"/api/info/{bot_name}")
    assert resp.status == 200
    bot_info = await resp.json()
    assert bot_info["display_name"] == "changed display name"
    assert bot_info["running_version"] is None
    assert len(bot_info["last_events"]) == 6
    assert bot_info["last_events"][0] == bot_created_event
    assert bot_info["last_events"][1] == bot_started_events
    assert bot_info["last_events"][2] == bot_edited_event
    assert bot_info["last_events"][3] == bot_stopped_event
    assert bot_info["last_events"][4] == bot_started_again_event
    bot_stopped_finally_event = bot_info["last_events"][5]
    assert time.time() - bot_stopped_finally_event["timestamp"] < 1
    assert bot_stopped_finally_event["username"] == "no-auth"
    assert bot_stopped_finally_event["event"] == "stopped"

    # let's delete this bot for good
    resp = await client.delete(f"/api/config/{bot_name}")
    assert resp.status == 200
    assert await resp.json() == bot_config_2
