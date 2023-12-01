from typing import Union, List
import time

class MessageManager:
    def __init__(self):
        """Initialize the Output class with an empty queue."""
        self.queue: List[Union[str, List[str]]] = []
        self.message_exit_event = False

    def add_to_queue(self, item: Union[str, List[str]]) -> None:
        """
        Add an item to the queue. The item can be a string or a list of strings.

        :param item: The item to be added to the queue.
        """
        self.queue.append(item)

    def monitor_queue(self) -> None:
        """
        Monitor the queue and print items as they are added.
        The function runs in a loop and should be called in a way that doesn't block the main program.
        """
        while not self.message_exit_event:
            while self.queue:
                item = self.queue.pop(0)  # Get the first item from the queue
                if isinstance(item, list):
                    for sub_item in item:
                        print(sub_item)
                else:
                    if item == "QUIT":
                        self.message_exit_event = True
                    else:
                        print(item)
            time.sleep(0.5)  # Sleep to prevent constant CPU usage, adjust as needed
