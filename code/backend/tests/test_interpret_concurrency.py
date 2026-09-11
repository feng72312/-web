from __future__ import annotations

import asyncio

import pytest

from app.core.concurrency.interpret_limit import InterpretConcurrencyLimiter, InterpretQueueBusyError


def test_limiter_allows_up_to_max_concurrent() -> None:
    async def _run() -> None:
        limiter = InterpretConcurrencyLimiter(max_concurrent=2, max_wait_seconds=1.0)
        await limiter.acquire()
        await limiter.acquire()
        assert limiter.snapshot()["active"] == 2
        limiter.release()
        limiter.release()
        assert limiter.snapshot()["active"] == 0

    asyncio.run(_run())


def test_limiter_queue_timeout_raises_busy() -> None:
    async def _run() -> None:
        limiter = InterpretConcurrencyLimiter(max_concurrent=1, max_wait_seconds=0.05)
        await limiter.acquire()

        with pytest.raises(InterpretQueueBusyError) as exc:
            await limiter.acquire()

        err = exc.value
        assert err.max_concurrent == 1
        assert err.active >= 1
        limiter.release()

    asyncio.run(_run())


def test_limiter_third_waits_then_enters() -> None:
    async def _run() -> None:
        limiter = InterpretConcurrencyLimiter(max_concurrent=2, max_wait_seconds=2.0)
        await limiter.acquire()
        await limiter.acquire()

        entered = asyncio.Event()

        async def waiter() -> None:
            await limiter.acquire()
            entered.set()
            limiter.release()

        task = asyncio.create_task(waiter())
        await asyncio.sleep(0.05)
        assert not entered.is_set()

        limiter.release()
        await asyncio.wait_for(entered.wait(), timeout=1.0)
        await task

        limiter.release()
        limiter.release()

    asyncio.run(_run())


def test_limiter_rejects_when_waiting_queue_is_full() -> None:
    async def _run() -> None:
        limiter = InterpretConcurrencyLimiter(
            max_concurrent=1,
            max_wait_seconds=2.0,
            max_waiting=1,
        )
        await limiter.acquire()

        queued = asyncio.create_task(limiter.acquire())
        await asyncio.sleep(0.05)
        assert limiter.snapshot() == {
            "active": 1,
            "waiting": 1,
            "maxConcurrent": 1,
            "maxWaiting": 1,
        }

        with pytest.raises(InterpretQueueBusyError) as exc:
            await limiter.acquire()

        assert exc.value.reason == "full"
        assert exc.value.max_waiting == 1

        limiter.release()
        await queued
        limiter.release()

    asyncio.run(_run())


def test_limiter_cancelled_waiter_releases_queue_position() -> None:
    async def _run() -> None:
        limiter = InterpretConcurrencyLimiter(
            max_concurrent=1,
            max_wait_seconds=2.0,
            max_waiting=1,
        )
        await limiter.acquire()

        queued = asyncio.create_task(limiter.acquire())
        await asyncio.sleep(0.05)
        assert limiter.snapshot()["waiting"] == 1

        queued.cancel()
        with pytest.raises(asyncio.CancelledError):
            await queued

        assert limiter.snapshot()["waiting"] == 0
        limiter.release()

    asyncio.run(_run())
