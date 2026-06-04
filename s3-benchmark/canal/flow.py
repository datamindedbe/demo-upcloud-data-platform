from __future__ import annotations
from typing import Callable, Optional, Sequence, Iterator
import multiprocessing

from canal._core import _map_async_unwind
from canal.libs.types import T, U


def map_async_unwind(func: Callable[[T], Iterator[U]], incoming: Iterator[T],
                     processes: Optional[int] = None) -> Iterator[U]:
    """
    Apply a method (func) to each element of the data stream (incoming). The func is serialized and applied in a
    specific process. After applying the method in the process, the result are unwind from the same process directly,
    before reaching the main process.
    You must be careful that your method must be thread safe, and ideally be very limited in its scope.
    @param func: method to apply to each element of the incoming stream
    @param incoming: the stream of data
    @param processes: number of processes to launch. If not provided, or 0, it will be set to the number of existing
                      cores
    @return:
    """
    return _map_async_unwind(func=func, incoming=incoming, processes=processes)


def map_async(func: Callable[[T], U], incoming: Iterator[T], processes: Optional[int] = None) -> Iterator[U]:
    """
    Apply a method (func) to each element of the data stream (incoming). The func is serialized and applied in a
    specific process. Contrarily to map_async_unwind, the result are not unwind from the specific process directly, so
    it is not suitable if your 'func' is returning a Generator for example.
    You must be careful that your method must be thread safe, and ideally be very limited in its scope.
    @param func: method to apply to each element of the incoming stream
    @param incoming: the stream of data
    @param processes: number of processes to launch. If not provided, or 0, it will be set to the number of existing
                      cores
    @return:
    """
    def wrapper(element: T) -> Sequence[U]:
        return [func(element)]
    return _map_async_unwind(func=wrapper, incoming=incoming, processes=processes)


def unwind(incoming: Iterator[Iterator[T]]) -> Iterator[T]:
    """
    Receive a Iterator of Iterator of T, and provide a single Iterator of T
    @param incoming: iterator stream
    """
    for element_group in incoming:
        for elem in element_group:
            yield elem


def map_async_default(func: Callable[[T], U], incoming: Iterator[T], processes: Optional[int] = None) -> Iterator[U]:
    """Try map_async, default to map"""
    try:
        if processes is None:
            processes = multiprocessing.cpu_count() * 3
        for record in map_async(func, incoming, processes=processes):
            yield record
    except AssertionError as e:
        if "daemonic processes are not allowed to have children" in e.args:
            # Airflow doesn't allow the creation of a thread pool from within a thread that is
            # already in a thread pool. We just default to a sequential map.
            # no logging atm -> circular import
            # logger.info("Parallel processing is not possible on this environment. " "Falling back to serial processing")
            for record in map(func, incoming):
                yield record
        else:
            raise e
