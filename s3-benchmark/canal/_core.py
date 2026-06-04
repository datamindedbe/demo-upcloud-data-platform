from __future__ import annotations

import multiprocessing
from multiprocessing.reduction import HAVE_SEND_HANDLE
from multiprocessing import Queue, Process, current_process
from queue import Empty
import os
from types import GeneratorType
import psutil
import traceback
import logging
import sys
import signal
from threading import Thread, Timer
from typing import Callable, Generator, Optional, Iterator, Union, Iterable, Type

from typing import Generic
from canal.libs.types import T, U

from canal.libs.forking_pickler_dill import PickleDillReducer

# Override the default class in charge of pickling
from canal.sink import foreach


reducer = PickleDillReducer()
setattr(reducer, "HAVE_SEND_HANDLE", HAVE_SEND_HANDLE)
multiprocessing.get_context().reducer = reducer


def die_if_parent_dies(parent_pid: int, timer_reference: dict) -> None:
    """
    When a parent is killed, we need the child processes to be killed as well. Unfortunately, all the daemon=True and
    other features of python do not work like you would like. To handle the external killing of the parent process,
    we must have the children monitor themselves the status of the parent.

    Note that nothing is done to handle the external killing of a child.

    @param parent_pid: The pid of the parent to monitor, we assume it will not re-used super quickly
    @return:
    """
    if psutil.pid_exists(parent_pid):
        if 'disabled' not in timer_reference:
            timer_reference['timer'] = Timer(5, die_if_parent_dies, args=[parent_pid, timer_reference])
            timer_reference['timer'].start()
    else:
        os.kill(os.getpid(), signal.SIGTERM)

def stop_timer(timer_reference: dict) -> None:
    if timer_reference['timer'] is not None:
        timer_reference['disabled'] = True # To avoid concurrency issues, must be set before the timer is canceled
        timer_reference['timer'].cancel()


class EndOfQueue:
    """Internal message used to detect the end of the queue being processed"""


class ThreadedGeneratorToQueue(Generic[T]):
    """
    Take data from an iterator an put them in the provided queue, without blocking the main thread.
    No intensive computation needs to be done here, so we can use the Thread interface
    """

    def __init__(self, iterable: Iterable[T], output: Queue[Union[T, Type[EndOfQueue]]], consumers: int):
        assert consumers >= 1

        self._iterable = iterable
        self._queue = output
        self._thread = Thread(name=repr(iterable), target=self._run)
        self._ended = False
        self._consumers = consumers

    def _run(self) -> None:
        """
        Pull the iterable and put every value into the multiprocessing queue
        """
        try:
            for value in self._iterable:
                self._queue.put(value)
        finally:
            self._ended = True
            for _ in range(0, self._consumers):
                self._queue.put(EndOfQueue)

    def start(self) -> None:
        """
        Start the thread pulling the generator
        """
        self._thread.start()

    def end(self) -> None:
        """
        Close the thread pulling the generator
        """
        if self._ended is False:
            logging.warning('Processing stopped before the end of the incoming data')
        self._thread.join()


def _worker_process(input_queue: Queue[T],
                    output_queue: Queue[Union[U, Exception, Type[EndOfQueue]]],
                    func: Callable[[T], Iterator[U]],
                    input_queue_timeout: float = 0,
                    input_queue_timeout_fallback: Optional[T] = None,
                    parent_pid: int = -1) -> None:
    """
    Method used as target to our multiprocessing wrapper. Read data from the input_queue, apply the func method on
    each element, and put the result (unwind) to the output_queue
    @param input_queue: incoming stream of data
    @param output_queue: stream of data constituted of the result of 'func' applied to each element of input_queue
    @param func: method to apply to each element of the stream
    @param input_queue_timeout: amount of seconds to wait to receive something from the input_queue. If 0, there
                                is no timeout
    @param input_queue_timeout_fallback: if input_queue_timeout is reached, we call the method 'func' with this default
                                value, IF this value is different than None.
    """
    timeout = input_queue_timeout if input_queue_timeout > 0 else None
    timer_reference = {'timer': None}
    if parent_pid >= 0:
        die_if_parent_dies(parent_pid=parent_pid, timer_reference=timer_reference)

    name = f'[Job {current_process().name}]'
    while True:
        try:

            try:
                element: Optional[T] = input_queue.get(timeout=timeout)
            except Empty:
                element = input_queue_timeout_fallback

            if element == EndOfQueue:
                stop_timer(timer_reference)
                logging.info(f'{name} End of queue')
                output_queue.put(EndOfQueue)
                break

            if element is not None:
                result = func(element)
                logging.debug(f'{name} From {element}, generated {result}')
                for result_element in result:
                    if isinstance(result_element, GeneratorType):
                        raise Exception(f'Impossible to pickle the generator element from {func}')
                    output_queue.put(result_element)
        except KeyboardInterrupt:
            stop_timer(timer_reference)
            logging.warning(f'{name} Received keyboard interruption stop job here')
            sys.exit(1)
        except Exception as exc:
            stop_timer(timer_reference)
            logging.error(f'{name} Exception while running worker method: {exc}')
            traceback.print_exc()
            output_queue.put(exc)


def _map_async_unwind(func: Callable[[T], Iterable[U]], incoming: Iterable[T], processes: Optional[int] = None,
                      input_queue_timeout: float = 0, input_queue_timeout_fallback: Optional[T] = None) \
        -> Generator[U, None, None]:
    """
    Receive a generator, consume the data and execute the provided method on each element. Recover the result and yield
    it as a normal generator.
    To properly handle typing, we always output an unwind result, so you should avoid exposing this method to
    the external world, and use proper intermediate methods which will hide this mandatory unwinding

    :param func: Method to execute on each element
    :param incoming: Iterator containing all elements.
    :param processes: Number of threads to use. If not provided, use the amount of threads provided to our system,
                     which can smaller than the total number of threads on the machine
    :param input_queue_timeout: Amount of time to block fetching data from the 'incoming' input
    :param input_queue_timeout_fallback: If there was a provided input_queue_timeout and it was reached, we still call
                            the 'func' method with this default value
    :return:
    """
    processes = processes or len(os.sched_getaffinity(0))
    assert processes >= 1

    # We want to buffer a reasonable amount of data in RAM
    input_queue: Queue[Union[T, Type[EndOfQueue]]] = Queue(maxsize=processes * 20)
    output_queue: Queue[U] = Queue(maxsize=processes * 20)

    parent_pid = os.getpid()
    workers = []
    for _ in range(0, processes):
        proc = Process(target=_worker_process, args=(input_queue, output_queue, func,
                                                     input_queue_timeout, input_queue_timeout_fallback,
                                                     parent_pid),
                       daemon=True)
        proc.start()
        workers.append(proc)

    incoming_to_queue = ThreadedGeneratorToQueue[T](iterable=incoming, output=input_queue, consumers=processes)
    incoming_to_queue.start()

    stopped_workers = 0
    received_outputs = 0
    while stopped_workers < processes:
        next_output = output_queue.get()

        received_outputs += 1
        logging.debug(f'Output received from the queue: {next_output}')
        if next_output == EndOfQueue:
            stopped_workers += 1
        elif isinstance(next_output, Exception):
            foreach(lambda w: w.terminate(), (w for w in workers if w.is_alive()))
            logging.error(f'Exception occurred within a worker, we stop here every worker due to {next_output}')
            incoming_to_queue.end()
            raise next_output
        else:
            yield next_output

    try:
        for worker in workers:
            worker.join()
    except KeyboardInterrupt:
        logging.warning('Terminate all workers')
        foreach(lambda w: w.terminate(), (w for w in workers if w.is_alive()))
    finally:
        incoming_to_queue.end()
