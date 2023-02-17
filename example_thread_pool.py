import time
from concurrent.futures import ThreadPoolExecutor, CancelledError


# Custom stopping mechanism to work around lack of thread stopping implementation.
stop_threads_flag = False

def sleep_stoppable(time_secs: float):
    if stop_threads_flag:
        raise CancelledError()

    time.sleep(time_secs)

def loop_function():
    while True:
        print("hello world!")
        sleep_stoppable(1)


def get_task_result_function():
    return 1


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=2) as pool:
        pool.submit(loop_function)
        # prints: "1"
        print(pool.submit(get_task_result_function).result())
        # prints: "hello world!" twice.
        time.sleep(1)
        stop_threads_flag = True