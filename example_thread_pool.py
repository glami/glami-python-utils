import time
from concurrent.futures import ThreadPoolExecutor

def loop_function():
    while True:
        print("hello world!")
        time.sleep(1)

def get_task_result_function():
    return 1


if __name__ == "__main__":
    # WARNING will run forever due to lack of thread stopping implementation. Would have to implement custom.
    with ThreadPoolExecutor(max_workers=1) as pool:
        pool.submit(loop_function)
        # prints: "1"
        print(pool.submit(get_task_result_function).result())
        # prints: "hello world!" forever .
        pool.submit(loop_function())
        time.sleep(1)

        # This will not help. Running threads continue forever.
        pool.shutdown(cancel_futures=True)