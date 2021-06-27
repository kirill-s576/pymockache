from typing import Union


class AbstractAsyncCachingBackend:

    async def get(self, key: Union[str, int]):
        raise NotImplementedError("Method 'get' should be reimplemented in child classes")

    async def set(self, key: Union[str, int], value: Union[str, int], expire_milliseconds: int):
        raise NotImplementedError("Method 'set' should be reimplemented in child classes")