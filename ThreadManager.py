# Author:                   TheScriptGuy
# Date:                     2023-11-10
# Version:                  0.01
# Description:              ThreadManager class to help manage the workers..

import threading
import queue
import signal
from typing import Callable, List, Any

class ThreadManager:
    """ThreadManager Class. Used for managing threads."""
    def __init__(self,
                num_workers: int,
                worker_function: Callable[[Any, int], None],
                statistics_manager
                ) -> None:
        """
        Initialize the ThreadManager with the specified number of worker threads and a worker function.
        The worker function should take an item to process and a thread id.
        """
        self.CLASS_VERSION = "0.01"
        self.num_workers = num_workers
        self.worker_function = worker_function
        self.exit_event = threading.Event()
        self.queues = {}  # Stores queues by their names
        self.thread_lists = {}  # Stores threads by their names
        self.statistics_manager = statistics_manager

    def print_variables(self) -> None:
        """
        Print variables.
        """
        print(f"Number of workers = {self.num_workers}")
        print(f"Number of items to test = {self.items_to_test}")
        print("-" * 30)

    def create_queue(self, name_of_queue: str) -> queue.Queue:
        """Creates a queue and stores it by the given name."""
        self.queues[name_of_queue] = queue.Queue()
        return self.queues[name_of_queue]

    def add_to_queue(self, name_of_queue: str, item_list: List[Any]) -> None:
        """Adds a list of items to the specified queue."""
        if name_of_queue in self.queues:
            for item in item_list:
                self.queues[name_of_queue].put(item)
        else:
            raise ValueError(f"No queue found with the name: {name_of_queue}")

    def create_thread_list(self, name_of_thread_list: str, queue_name: str) -> None:
        """Creates and starts a list of threads to process tasks from the given queue."""
        if queue_name not in self.queues:
            raise ValueError(f"No queue found with the name: {queue_name}")

        threads = []
        for _ in range(self.num_workers):
            thread = threading.Thread(target=self.worker, args=(self.queues[queue_name],))
            threads.append(thread)
            thread.start()

        self.thread_lists[name_of_thread_list] = threads

    def worker(self, queue_instance: queue.Queue) -> None:
        """Worker thread to process items from the queue until the exit event is set."""
        thread_id = threading.get_ident()

        while not self.exit_event.is_set():
            try:
                item = queue_instance.get_nowait()
                self.worker_function(item, thread_id, self.statistics_manager)
                queue_instance.task_done()
            except queue.Empty:
                break

        remaining_threads = threading.active_count() - 1  # Excluding the main thread
        print(f"Thread ID: {thread_id} is exiting. Remaining threads: {remaining_threads} of {self.num_workers}")

    def start(self, item_list: List[Any], queue_name: str, thread_name: str) -> None:
        """
        Starts the ThreadManager, creating a queue and threads, adding items from item_list to the queue,
        and setting up signal handling.
        """
        signal.signal(signal.SIGINT, self.exit_signal_handler)
        self.items_to_test = len(item_list)

        # Creating a queue, adding elements in item_list to it, and starting threads
        item_queue = self.create_queue(queue_name)
        self.add_to_queue(queue_name, item_list)
        self.create_thread_list(thread_name, queue_name)

        # Print the variables
        self.print_variables()

    def exit_signal_handler(self, signum: int, frame) -> None:
        """
        Handle exit signal to terminate the application gracefully.
        """
        print("Exiting due to Ctrl+C")
        self.exit_event.set()
        self.join_threads()

    def join_threads(self) -> None:
        """Join all the threads."""
        # Join all threads to make sure they have finished before exiting the program.
        for thread_list in self.thread_lists.values():
            for thread in thread_list:
                thread.join()
