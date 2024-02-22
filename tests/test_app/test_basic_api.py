import aiohttp.web
from pytest_aiohttp.plugin import AiohttpClient  # type: ignore

from telebot_constructor.app import TelebotConstructorApp


async def test_bot_config(
    constructor_app: tuple[TelebotConstructorApp, aiohttp.web.Application],
    aiohttp_client: AiohttpClient,
) -> None:
    _, web_app = constructor_app
    client = await aiohttp_client(web_app)

    bot_name = "test-bot-1312"
    resp = await client.post("/api/secrets/test-1312-token", data="token")
    assert resp.status == 200

    resp = await client.post(
        f"/api/config/{bot_name}",
        json={
            "display_name": "my bot",
            "token_secret_name": "test-1312-token",
            "user_flow_config": {"entrypoints": [], "blocks": [], "node_display_coords": {}},
        },
    )
    assert resp.status == 201

    resp = await client.get(f"/api/config/{bot_name}")
    assert resp.status == 200
    assert await resp.json() == {
        "display_name": "my bot",
        "token_secret_name": "test-1312-token",
        "user_flow_config": {"entrypoints": [], "blocks": [], "node_display_coords": {}},
    }

    resp = await client.get("/api/info")
    assert resp.status == 200
    resp_body = await resp.json()
    assert list(resp_body.keys()) == [bot_name]
    bot_info = resp_body[bot_name]
    assert bot_info["display_name"] == "my bot"
    assert bot_info["is_running"] is False
    assert bot_info["last_run_at"] is None

    resp = await client.post(f"/api/start/{bot_name}")
    assert resp.status == 201

    resp = await client.get("/api/info")
    assert resp.status == 200
    resp_body = await resp.json()
    assert list(resp_body.keys()) == [bot_name]
    bot_info = resp_body[bot_name]
    assert bot_info["is_running"] is True
