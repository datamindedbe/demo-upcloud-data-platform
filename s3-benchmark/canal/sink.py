from __future__ import annotations

from typing import Callable, Iterator

from canal.libs.types import T, U


def foreach(func: Callable[[T], U], incoming: Iterator[T]) -> None:
    """
    Apply a func on each element of a data stream, without returning the output
    @param func: The method to apply
    @param incoming: The data stream
    @return:
    """
    for element in incoming:
        func(element)
