import asyncio
import concurrent.futures
from asyncio import AbstractEventLoop
from threading import Thread
from typing import Optional, Coroutine, Any, Iterable, List, TypeVar


T = TypeVar("T")


class AsyncioThreadLoop:
    def __init__(self, exit_timeout=None):
        """
        This object allows you to run multiple coroutines to a single loop and return their results.
        The coroutines can create other tasks into the loop, for which the method does not wait.
        """

        self.loop: Optional[AbstractEventLoop] = None
        self.thread: Optional[Thread] = None
        self.exit_timeout = exit_timeout

    @staticmethod
    def _run_loop_in_thread(loop):
        try:
            loop.run_forever()
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.run_until_complete(loop.shutdown_default_executor())
            loop.close()

    def __enter__(self):
        assert self.thread is None
        assert self.loop is None
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self._run_loop_in_thread, args=(self.loop,), daemon=True)

        assert not self.thread.is_alive()
        self.thread.start()
        return self

    def submit(self, coro: Coroutine[Any, Any, T]) -> concurrent.futures.Future[T]:
        assert self.loop is not None, "Not available outside context."
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def evaluate(self, coro: Coroutine[Any, Any, T], timeout=None) -> T:
        assert self.loop is not None, "Not available outside context."
        fut = self.submit(coro)
        return fut.result(timeout=timeout)

    def evaluate_many(self, coros: Iterable[Coroutine], timeout=None) -> List:
        assert self.loop is not None, "Not available outside context."
        futs = [self.submit(coro) for coro in coros]
        concurrent.futures.wait(futs, timeout=timeout)
        # If something "not done", this raises TimeoutError
        return [fut.result(0) for fut in futs]

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        try:
            self.loop.call_soon_threadsafe(self.loop.stop)
        except RuntimeError:
            pass  # Raises RuntimeError if called on a loop that’s been closed.
        # Thread will stop once the loop exits `run_forever` method.
        self.thread.join(timeout=self.exit_timeout)
        self.thread = None
        self.loop = None

    @staticmethod
    def submit_in_new_loop(coro: Coroutine, exit_timeout=None) -> "AsyncioThreadLoop":
        loop = AsyncioThreadLoop(exit_timeout=exit_timeout)
        loop.__enter__()
        loop.submit(coro)
        return loop


class SimpleAsyncioThreadLoop:
    def __init__(self):
        self.loop: Optional[AbstractEventLoop] = None
        self.thread: Optional[Thread] = None

    @staticmethod
    def _run_loop_in_thread(loop):
        try:
            loop.run_forever()
        finally:
            loop.close()

    def __enter__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self._run_loop_in_thread, args=(self.loop,), daemon=True)
        self.thread.start()
        return self

    def submit(self, coro: Coroutine[Any, Any, T]) -> concurrent.futures.Future[T]:
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        try:
            self.loop.call_soon_threadsafe(self.loop.stop)
        except RuntimeError:
            pass  # Raises RuntimeError if called on a loop that’s been closed.
        # Thread will stop once the loop exits `run_forever` method.
        self.thread.join(timeout=None)
