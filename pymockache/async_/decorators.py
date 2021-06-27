from typing import List
import hashlib
import functools
import inspect
from .backends.abstract import AbstractAsyncCachingBackend


class AsyncCachingWrapper:
    """
    How to use:
    @AsyncCachingWrapper(
        backend=caching_backend,
        sign_variables=["test_param"],
        expire_milliseconds=100000,
        logger=logger,
        log_active=True
    )
    async def test_func(test_param) -> str:
        ...

    Properties:
    - backend: AbstractAsyncCachingBackend - your initialized backend for caching.
    - sign_variables: List[str] - List of variables, which will be use for detecting the same call of function.
        P.S.: Function can have a lot of properties, but only 1-2 will be important for caching...
        Even If not-in-list properties will be changed - Library will return cached result.
    """

    def __init__(self,
                 backend: AbstractAsyncCachingBackend,
                 sign_variables: List[str],
                 expire_milliseconds: int=60,
                 logger=None,
                 log_active=False):
        self.sign_variables = sign_variables
        self.backend = backend
        self.expire_min = expire_milliseconds
        self.logger = logger
        self.log_active = log_active

    @classmethod
    def get_function_default_kwargs(cls, function) -> dict:
        function_default_kwargs = {}
        function_variables_dict = dict(inspect.signature(function).parameters)
        for key, value in function_variables_dict.items():
            if hasattr(value.default, "__name__") and value.default.__name__ == "_empty":
                function_default_kwargs[key] = None
            else:
                function_default_kwargs[key] = value.default
        return function_default_kwargs

    @classmethod
    def get_function_variables_tuple(self, function) -> tuple:
        function_variables_tuple = tuple(inspect.signature(function).parameters)
        return function_variables_tuple

    @classmethod
    def args_to_kwargs(cls, variables_args: tuple, values_args: tuple) -> dict:
        zipped = list(zip(variables_args, values_args))
        args_to_kwargs = {
            item[0]: item[1] for item in zipped
        }
        return args_to_kwargs

    @classmethod
    def get_md_5_hashed_string(cls, string: str):
        hashed = hashlib.md5(string.encode()).hexdigest()
        return hashed

    def get_pattern(self, function, arguments_list: list) -> str:
        return f"{function.__module__}:{function.__name__}:{':'.join(str(x) for x in arguments_list)}"

    async def get_value_from_backend(self, key):
        return await self.backend.get(key)

    async def set_value_to_backend(self, key, value):
        return await self.backend.set(key, value, expire_milliseconds=self.expire_min)

    def __call__(self, fn):

        @functools.wraps(fn)
        async def decorated(*args, **kwargs):

            function_default_kwargs = self.get_function_default_kwargs(fn)
            function_variables_tuple = self.get_function_variables_tuple(fn)
            args_to_kwargs = self.args_to_kwargs(function_variables_tuple, args)

            function_default_kwargs.update(kwargs)
            function_default_kwargs.update(args_to_kwargs)

            to_caching_arguments = [
                function_default_kwargs[item] for item in self.sign_variables
            ]

            key = self.get_pattern(fn, to_caching_arguments)
            hashed_key = self.get_md_5_hashed_string(key)

            value = await self.get_value_from_backend(hashed_key)
            if value:
                if self.logger and self.log_active:
                    self.logger.info(f"MethodCachingResult: {fn.__name__} : Cached value returned")
                return value
            else:
                result = await fn(*args, **kwargs)
                await self.set_value_to_backend(hashed_key, result)
                if self.logger and self.log_active:
                    self.logger.info(f"MethodCachingResult: {fn.__name__} : Computed value returned")
                return result
        return decorated
