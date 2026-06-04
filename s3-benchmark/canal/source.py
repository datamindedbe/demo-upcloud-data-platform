from __future__ import annotations
import os
import time
from typing import Callable, Optional, Sequence, Iterator

from canal.libs.types import T
from canal.flow import map_async_unwind


def infinite_polling(polling_method: Callable[[], Sequence[T]],
                     interval_s: float = 1,
                     poll_again_on_non_empty: bool = False) -> Iterator[Sequence[T]]:
    """
    Wrapper around a polling method to hide a scheduled polling behind a normal generator.
    :param polling_method provide results as a List[any]. If this method crashes, the generator crashes.
    :param interval_s minimum amount of seconds between each polling. Polling + yielding time will be deducted from it
    :param poll_again_on_non_empty if the polling_method returns a non-empty list, we might want to directly re-poll
            the data (until we see nothing more to poll). Typically useful for sqs-s3 polling.
            Default is False, so we act like a real polling method without caring about the polling_method return
    """

    while True:
        start_time = time.time()
        elements = polling_method()
        yield elements

        waiting_time = interval_s - (time.time() - start_time)

        # len > 0 && poll_again_on_non_empty is True  -> poll -> No waiting time. All the other combinations lead to
        # a waiting time
        if waiting_time > 0 and not(len(elements) > 0 and poll_again_on_non_empty is True):
            time.sleep(waiting_time)


def merge_generators(func: Callable[[], Iterator[T]], amount: Optional[int] = None) -> Iterator[T]:
    """
    Launch x generators on multiple threads, and output a aggregated generator of all the data together
    :param func:
    :param method: Method creating a generator
    :param amount: Number of generators we want in parallel. This will be mapped to the number of processes we want
    :return:
    """
    def wrapper(_: int) -> Iterator[T]:
        return func()

    amount = amount or len(os.sched_getaffinity(0))
    res = map_async_unwind(func=wrapper, incoming=(i for i in range(0, amount)), processes=amount)

    return res
