#!/usr/bin/env python3
"""
Writing strings to Redis
"""
import redis
import uuid
from typing import Union, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    '''takes a single method Callable argument and returns a Callable'''
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''increments the count for that key every time the method
        is called and returns the value returned by the original method'''

        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


class Cache():
    def __init__(self):
        '''store an instance of the Redis client as a private variable
        named _redis (using redis.Redis())
        and flush the instance using flushdb'''
        self._redis = redis.Redis()
        self._redis.flushdb(asynchronous=False)

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        ''' The method should generate a random key (e.g. using uuid),
        store the input data in Redis using the random key
        and return the key'''
        key = str(uuid.uuid4())
        self._redis.mset({key: data})
        return key

    def get(self, key: str, fn: [Callable] = None) -> Union[str, bytes, int,
                                                            float]:
        '''Overwrite the original get method of Redis (highlevel abstraction
                of Redis instance)'''
        if (fn is None):
            return self._redis.get(key)
        if (self._redis.get(key) is None):
            return None
        return fn(self._redis.get(key))

    def get_str(self, value: bytes) -> str:
        '''convert value to str(its original type)'''
        return str(value.decode("utf-8"))

    def get_int(self, value: bytes) -> int:
        '''convert value to int(its original type)'''
        return int(value.decode("utf-8"))
