import asyncio
from unittest import TestCase

from asyncio_thread_loop import AsyncioThreadLoop


class TestSimpleAsyncioThreadLoop(TestCase):
    def test_submit(self):
        async def get_task_result_coroutine():
            return 1

        async def loop_coroutine():
            while True:
                print("hello world!")
                await asyncio.sleep(1)

        with AsyncioThreadLoop(exit_timeout=3) as loop:
            print(loop.submit(get_task_result_coroutine()).result())
            loop.submit(loop_coroutine())
