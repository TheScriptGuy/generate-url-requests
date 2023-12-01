# Author:                   TheScriptGuy
# Date:                     2023-11-30
# Version:                  0.02
# Description:              ThreadManager class to help manage the workers..

import threading
import queue
import signal
import time
from typing import Callable, List, Any


class ThreadManager:
    """ThreadManager Class. Used for managing threads."""
    def __init__(self,
                num_workers: int,
                worker_function: Callable[[Any, int], None],
                statistics_manager,
                message_manager
                ) -> None:
        """
        Initialize the ThreadManager with the specified number of worker threads and a worker function.
        The worker function should take an item to process and a thread id.
        """
        self.CLASS_VERSION = "0.02"
        
        # Define the number of workers in the class.
        self.num_workers = num_workers
        
        # Define the worker_function that will be used
        self.worker_function = worker_function
        
        # Define exit events
        self.exit_event = threading.Event()
        self.message_exit_event = threading.Event()
        self.finished_event = threading.Event()

        # Create a dict for the queues and thread_lists
        self.queues = {}  # Stores queues by their names
        self.thread_lists = {}  # Stores threads by their names

        # Define a statistics_manager object
        self.statistics_manager = statistics_manager

        # Define the message_manager object
        self.message_manager = message_manager

        # Set the messages_queue to None
        self.messages_queue = None

    def print_variables(self) -> None:
        """
        Print variables.
        """
        self.message_manager.add_to_queue(f"Number of workers = {self.num_workers}")
        self.message_manager.add_to_queue(f"Number of items to test = {self.items_to_test}")
        self.message_manager.add_to_queue("-" * 30)

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

    def create_thread_list(self, name_of_thread_list: str, queue_name: str, _target, number_of_workers: int) -> None:
        """Creates and starts a list of threads to process tasks from the given queue."""
        if queue_name not in self.queues:
            raise ValueError(f"No queue found with the name: {queue_name}")

        threads = []
        for _ in range(number_of_workers):
            thread = threading.Thread(target=_target, args=(self.queues[queue_name],))
            threads.append(thread)
            thread.start()

        self.thread_lists[name_of_thread_list] = threads

    def worker(self, queue_instance: queue.Queue) -> None:
        """Worker thread to process items from the queue until the exit event is set."""
        thread_id = threading.get_ident()

        while not self.exit_event.is_set():
            try:
                item = queue_instance.get_nowait()
                result = self.worker_function(item, thread_id, self.statistics_manager)
                self.message_manager.add_to_queue(result)
                queue_instance.task_done()
            except queue.Empty:
                break

        remaining_threads = threading.active_count() - 3  # Excluding the main thread and the messages thread and the thread that just exited.
        #print(f"Thread ID: {thread_id} is exiting. Remaining threads: {remaining_threads} of {self.num_workers}")
        self.message_manager.add_to_queue(f"Thread ID: {thread_id} is exiting. Remaining threads: {remaining_threads} of {self.num_workers}")
        if remaining_threads == 0:
            self.message_manager.add_to_queue("QUIT")

    def message_worker(self, queue_instance: queue.Queue) -> None:
        """Message worker thread."""
        self.message_manager.monitor_queue()

    def start(self, item_list: List[Any], queue_name: str, thread_name: str) -> None:
        """
        Starts the ThreadManager, creating a queue and threads, adding items from item_list to the queue,
        and setting up signal handling.
        """
        signal.signal(signal.SIGINT, self.exit_signal_handler)
        self.items_to_test = len(item_list)
        self.worker_thread_name = thread_name

        # Create a message queue.
        message_queue = self.create_queue('messages')
        
        # Add an empty object to the messages queue.
        self.message_manager.add_to_queue([])

        # Create the messages thread list. Given that we're only displaying to one stdout, only one thread is required.
        self.create_thread_list('messages_thread', 'messages', self.message_worker, 1)

        # Print the variables
        self.print_variables()

        # Creating a queue, adding elements in item_list to it, and starting threads
        item_queue = self.create_queue(queue_name)
        self.add_to_queue(queue_name, item_list)
        self.create_thread_list(thread_name, queue_name, self.worker, self.num_workers)

        self.join_threads("messages_thread")

    def exit_signal_handler(self, signum: int, frame) -> None:
        """
        Handle exit signal to terminate the application gracefully.
        """
        print("Exiting due to Ctrl+C")
        
        # Set the exit_event and join threads.
        self.exit_event.set()
        self.join_threads(self.worker_thread_name)

        # Set the message_exit_event and join threads.
        self.message_exit_event.set()
        self.message_manager.message_exit_event = True
        self.join_threads('messages_thread')

    def join_threads(self, name_of_thread: str) -> None:
        """Join all the threads."""
        # Join all threads to make sure they have finished before exiting the program.
        for thread in self.thread_lists[name_of_thread]:
            thread.join()
