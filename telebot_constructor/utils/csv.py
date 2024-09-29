from aiohttp.web import StreamResponse


class StreamResponseCsvEncodingAdapter:
    """Very thin adapter to pass aiohttp response to csv writer as file handle"""

    def __init__(self, sr: StreamResponse):
        self.sr = sr

    async def write(self, s: str) -> None:
        await self.sr.write(s.encode("utf-8"))
