import re
from typing import Tuple

import aiohttp.web
from pytest_aiohttp.plugin import AiohttpClient  # type: ignore

from telebot_constructor.app import TelebotConstructorApp


async def test_serve_index(
    constructor_app: Tuple[TelebotConstructorApp, aiohttp.web.Application], aiohttp_client: AiohttpClient
) -> None:
    constructor, web_app = constructor_app
    client = await aiohttp_client(web_app)

    resp = await client.get("/")
    assert resp.status == 404
    assert re.match(r"^404: Static path /.*/index\.html does not exist$", await resp.text("utf-8"))

    (constructor.static_files_dir / "index.html").write_text("hello world")

    resp = await client.get("/")
    assert resp.status == 200
    assert await resp.text("utf-8") == "hello world"
    assert resp.content_type == "text/html"

    resp = await client.get("/whatever/weird/path/we/use/in/client/side/routing")
    assert resp.status == 200
    assert await resp.text("utf-8") == "hello world"
    assert resp.content_type == "text/html"


async def test_serve_static_files(
    constructor_app: Tuple[TelebotConstructorApp, aiohttp.web.Application], aiohttp_client: AiohttpClient
) -> None:
    constructor, web_app = constructor_app
    client = await aiohttp_client(web_app)

    assets_dir = constructor.static_files_dir / "assets"
    assets_dir.mkdir()
    (assets_dir / "some-asset.js").write_text("console.log(foo);")

    resp = await client.get("/assets/some-asset.js")
    assert resp.status == 200
    assert await resp.text("utf-8") == "console.log(foo);"
    assert resp.content_type == "application/javascript"


async def test_cors(
    constructor_app: Tuple[TelebotConstructorApp, aiohttp.web.Application], aiohttp_client: AiohttpClient
) -> None:
    _, web_app = constructor_app
    client = await aiohttp_client(web_app)

    resp = await client.options("/whatever", headers={"Origin": "http://example.com"})

    assert resp.status == 200
    headers = dict(resp.headers)
    headers.pop("Date")
    headers.pop("Server")
    assert headers == {
        "Access-Control-Allow-Origin": "http://localhost:8081",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Max-Age": "300",
        "Content-Length": "0",
        "Content-Type": "text/plain; charset=utf-8",
        # "Date": "Mon, 23 Oct 2023 17:59:37 GMT",
        # "Server": "Python/3.10 aiohttp/3.8.6",
    }
