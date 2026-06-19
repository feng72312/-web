from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Any, Callable, TypeVar

T = TypeVar("T")

_executor: ThreadPoolExecutor | None = None


def init_cpu_pool(max_workers: int = 4) -> None:
    global _executor
    if _executor is not None:
        return
    workers = max(1, int(max_workers))
    _executor = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="bazi-cpu")


def shutdown_cpu_pool() -> None:
    global _executor
    if _executor is None:
        return
    _executor.shutdown(wait=False, cancel_futures=True)
    _executor = None


async def run_cpu(func: Callable[..., T], /, *args: Any, **kwargs: Any) -> T:
    loop = asyncio.get_running_loop()
    if _executor is None:
        if kwargs:
            return func(*args, **kwargs)
        return func(*args)
    if kwargs:
        bound: Callable[[], T] = partial(func, *args, **kwargs)
    elif args:
        bound = partial(func, *args)
    else:
        bound = func
    return await loop.run_in_executor(_executor, bound)
