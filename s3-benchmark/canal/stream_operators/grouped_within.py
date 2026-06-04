from __future__ import annotations
import itertools
from itertools import chain
import time
from typing import List, Sequence, Iterator, Union

from typing import Generic

from canal._core import _map_async_unwind
from canal.libs.types import T


class TimeoutFallback:
    """
    Used by grouped_within if the .get from the generator takes too much time
    """


class GroupedWithinEndOfStream:
    """
    Used by grouped_within at the end of the queue (different than EndOfQueue as this object is handled only by the
    grouped_within related functions, not the general map_async method)
    """


def _grouped_within_without_time(incoming: Iterator[T], batch_size: int) -> Iterator[Sequence[T]]:
    """
    Specific map_grouped_within method when there is no timeout_s. Aggregate incoming data by a specific amount of
    entries. Use the main thread as there is no need to have a thread if there is no time handling.
    @param incoming: data stream
    @param batch_size: number of elements to group together
    """
    group = []
    for element in incoming:
        group.append(element)
        if len(group) >= batch_size:
            yield group
            group = []

    if len(group) > 0:
        yield group


class GroupBeingBuilt(Generic[T]):
    """
    Used by the _grouped_within_worker to create an group.
    We avoid using a simple dict as the typing would not be correct.
    We also avoid using a global.
    """

    def __init__(self, batch_size: int, timeout_s: float):
        self._elements: List[T] = []
        self._last_export = time.time()
        self._batch_size = batch_size
        self._timeout_s = timeout_s

    def must_export(self, end_of_stream: bool = False) -> bool:
        """Check if we should export the current data we have locally"""
        time_condition = time.time() - self._last_export >= self._timeout_s
        if len(self._elements) >= self._batch_size \
                or (time_condition and len(self._elements) > 0) \
                or (end_of_stream and len(self._elements) > 0):
            return True
        return False

    def export(self) -> List[T]:
        """Provide the list of elements and clean up afterwards"""
        exports = self._elements
        self._elements = []
        self._last_export = time.time()
        return exports

    def append(self, element: T) -> None:
        """Append an element to the current batch being built"""
        self._elements.append(element)


def _grouped_within_worker(group: GroupBeingBuilt[T],
                           element: Union[T, TimeoutFallback, GroupedWithinEndOfStream]) -> List[List[T]]:
    """
    Internal worker used by the map_grouped_within to aggregate data together when timeout_s is bigger than 0
    @param group: the current group object which is used to aggregate the data, and keep track of the last export
    @param element: the current object from the data stream. Can also be a specific fallback object (if nothing
                    was fetched from the stream in a specific time) or an end-of-queue signal to export the last
                    batch
    @return:
    """
    if not isinstance(element, TimeoutFallback) and not isinstance(element, GroupedWithinEndOfStream):
        group.append(element)

    result = []
    end_of_stream = isinstance(element, GroupedWithinEndOfStream)
    if group.must_export(end_of_stream=end_of_stream):
        result = [group.export()]

    return result


def grouped_within(incoming: Iterator[T], batch_size: int, timeout_s: float = 0) -> Iterator[Sequence[T]]:
    """
    Go through the incoming generator and group the data by 'batch_size' elements or if 'timeout_s' is reached, whatever
    happens first. If timeout_s is 0, the time is not used. Last iterator element will flush a batch of <= batch_size.
    Only non-empty batch will be returned
    @param incoming: data stream
    @param batch_size: number of elements to group together
    @param timeout_s: maximum time between each data batch. If 0, disable the feature
    @return:
    """
    assert timeout_s >= 0
    if timeout_s == 0:
        return _grouped_within_without_time(incoming=incoming, batch_size=batch_size)

    stream: chain[Union[T, GroupedWithinEndOfStream]] = itertools.chain(incoming, [GroupedWithinEndOfStream()])

    # We do not attempt to export batches exactly at the ms level, but within a specific range of the targeted timeout_s
    precision = 10
    input_queue_timeout = max(0.01, timeout_s / precision)

    # To easily have the proper Generic type for the group being built, and avoid using global or workaround, a small
    # wrapper is useful
    group = GroupBeingBuilt[T](batch_size=batch_size, timeout_s=timeout_s)

    def func(element: Union[T, TimeoutFallback, GroupedWithinEndOfStream]) -> List[List[T]]:
        return _grouped_within_worker(group, element)

    return _map_async_unwind(incoming=stream,
                             func=func, processes=1,
                             input_queue_timeout=input_queue_timeout,
                             input_queue_timeout_fallback=TimeoutFallback())
