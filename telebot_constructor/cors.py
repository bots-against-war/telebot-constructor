import logging

from aiohttp import hdrs, web
from aiohttp.typedefs import Handler

from telebot_constructor.constants import FILENAME_HEADER

logger = logging.getLogger(__name__)


def setup_cors(app: web.Application) -> None:
    @web.middleware
    async def cors_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
        try:
            resp = await handler(request)
        except web.HTTPException as e:
            resp = e

        allowed_origins = ["http://localhost:8081", "http://127.0.0.1:8081"]  # local dev server origin
        request_origin = request.headers.get(hdrs.ORIGIN)
        logger.debug(f"CORS: request origin = {request_origin}")
        if request_origin is not None:
            resp.headers[hdrs.ACCESS_CONTROL_ALLOW_ORIGIN] = (
                request_origin if request_origin in allowed_origins else allowed_origins[0]
            )
            resp.headers[hdrs.ACCESS_CONTROL_ALLOW_HEADERS] = f"{hdrs.CONTENT_TYPE}, {FILENAME_HEADER}"
            resp.headers[hdrs.ACCESS_CONTROL_ALLOW_METHODS] = "GET,POST,PUT,DELETE,OPTIONS"
            resp.headers[hdrs.ACCESS_CONTROL_MAX_AGE] = "300"
            logger.debug(
                "Set Access-Control-* headers on response: %s",
                {name: value for name, value in resp.headers.items() if name.lower().startswith("access-control")},
            )

        if isinstance(resp, web.HTTPException):
            raise resp
        else:
            return resp

    app.middlewares.insert(0, cors_middleware)

    async def preflight(request: web.Request) -> web.Response:
        return web.Response(text="")

    app.router.add_options("/{wildcard:.*}", preflight)
