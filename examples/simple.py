from pymockache.async_.decorators import AsyncCachingWrapper
from pymockache.async_.backends.redis import AsyncRedisCachingBackend
import aiohttp
import asyncio
import logging
import time


logger = logging.getLogger(__name__)
caching_backend = AsyncRedisCachingBackend(
    redis_host="redis://localhost:6379/0"
)


@AsyncCachingWrapper(
    backend=caching_backend,
    sign_variables=["page_url"],
    expire_milliseconds=100000,
    logger=logger,
    log_active=True
)
async def get_page_text(page_url) -> str:
    """
    Function returns text of http response from page_url.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(page_url) as response:
            await asyncio.sleep(2)
            html = await response.text()
            return html


async def main():
    urls_list = [
        "https://www.google.com/",
        "https://www.python.org",
        "https://www.google.com/",
        "https://www.python.org"
    ]
    for url in urls_list:
        t0 = time.time()
        text = await get_page_text(page_url=url)
        t1 = time.time()
        delta = t1 - t0
        print(f"Url: {url}. Text length: {len(text)}. Total time: {str(delta)}")


if __name__ == '__main__':
    asyncio.run(main())