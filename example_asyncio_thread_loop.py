import asyncio
from time import sleep

from asyncio_thread_loop import AsyncioThreadLoop


async def get_task_result_coroutine():
    return 1

async def loop_coroutine():
    while True:
        print("hello world!")
        await asyncio.sleep(1)

if __name__ == "__main__":
    with AsyncioThreadLoop() as loop:
        # prints: "hello world!" twice due to sleep and immediate task cancellation.
        loop.submit(loop_coroutine())
        # prints: "1"
        print(loop.submit(get_task_result_coroutine()).result())
        sleep(1)
