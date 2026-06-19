from __future__ import annotations

import asyncio


class InterpretQueueBusyError(Exception):
    def __init__(
        self,
        *,
        active: int,
        waiting: int,
        max_concurrent: int,
    ) -> None:
        self.active = active
        self.waiting = waiting
        self.max_concurrent = max_concurrent
        super().__init__("interpret queue busy")


class InterpretConcurrencyLimiter:
    """Global cap on concurrent AI interpret requests with bounded queue wait."""

    def __init__(self, max_concurrent: int, max_wait_seconds: float) -> None:
        self._max_concurrent = max(1, int(max_concurrent))
        self._max_wait = max(0.0, float(max_wait_seconds))
        self._sem = asyncio.Semaphore(self._max_concurrent)
        self._lock = asyncio.Lock()
        self._active = 0
        self._waiting = 0

    @property
    def max_concurrent(self) -> int:
        return self._max_concurrent

    async def acquire(self) -> None:
        queued = False
        async with self._lock:
            if self._active >= self._max_concurrent:
                self._waiting += 1
                queued = True
        try:
            if self._max_wait <= 0:
                await self._sem.acquire()
            else:
                await asyncio.wait_for(self._sem.acquire(), timeout=self._max_wait)
        except asyncio.TimeoutError as err:
            if queued:
                async with self._lock:
                    self._waiting = max(0, self._waiting - 1)
            async with self._lock:
                active = self._active
                waiting = self._waiting
            raise InterpretQueueBusyError(
                active=active,
                waiting=waiting,
                max_concurrent=self._max_concurrent,
            ) from err
        async with self._lock:
            if queued:
                self._waiting = max(0, self._waiting - 1)
            self._active += 1

    def release(self) -> None:
        self._active = max(0, self._active - 1)
        self._sem.release()

    def snapshot(self) -> dict[str, int]:
        return {
            "active": self._active,
            "waiting": self._waiting,
            "maxConcurrent": self._max_concurrent,
        }
