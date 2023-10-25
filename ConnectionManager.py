# Author:                   TheScriptGuy
# Date:                     2023-10-25
# Version:                  0.02
# Description:              ConnectionManager class used for URL connectivity operations (multithreaded)

import threading
import queue
import signal
import requests
from typing import List, Optional

class ConnectionManager:
    def __init__(self, num_connections: int, num_workers: int, outputfile: Optional[str]):
        self.CLASS_VERSION = "0.02"
        self.num_connections = num_connections
        self.num_workers = num_workers
        self.outputfile = outputfile

        # Define a global exit event for all threads to track on.
        self.exit_event = threading.Event()

    def make_request(self, hostname: str, thread_id: int) -> str:
        """
        Attempt to connect to a hostname using HTTPS and then HTTP, logging the results.
        """
        protocols = ['https', 'http']
        for protocol in protocols:
            if self.exit_event.is_set():  # Check if the exit signal is set
                return

            # Attempting to connect to the hostname
            try:
                response = requests.get(f"{protocol}://{hostname}", timeout=5)
                output = f"Thread ID: {thread_id}, Status Code: {response.status_code} ({response.reason: <20}), Hostname: {hostname}"
                print(output)
                return output

            except requests.exceptions.ConnectionError as e:
                if "Name or service not known" in str(e):
                    error_detail = "DNS resolution issue"
                elif "Connection refused" in str(e):
                    error_detail = "Connection refused"
                else:
                    error_detail = "Connection error"
                error_output = f"Thread ID: {thread_id}, Status Code: 000 ({error_detail: <20}), Hostname: {protocol}://{hostname}"
                print(error_output)

            except requests.exceptions.ReadTimeout:
                error_output = f"Thread ID: {thread_id}, Status Code: 000 (Read timeout         ), Hostname: {protocol}://{hostname}"
                print(error_output)

            except requests.exceptions.TooManyRedirects:
                error_output = f"Thread ID: {thread_id}, Status Code: 000 (Too many redirects   ), Hostname: {protocol}://{hostname}"
                print(error_output)

            except requests.exceptions.ConnectTimeoutError:
                error_output = f"Thread ID: {thread_id}, Status Code: 000 (Connection Timeout   ), Hostname: {protocol}://{hostname}"
                print(error_output)
 
            except requests.exceptions.ConnectTimeout:
                error_output = f"Thread ID: {thread_id}, Status Code: 000 (Connection Timeout   ), Hostname: {protocol}://{hostname}"
                print(error_output)

            except requetss.exceptions.SSLError:
                error_output = f"Thread ID: {thread_id}, Status Code: 000 (SSL Error            ), Hostname: {protocol}://{hostname}"
               
            except requests.exceptions.RequestException as e:
                error_output = f"Thread ID: {thread_id}, An error occurred while connecting to {protocol}://{hostname}: {e}"
                print(error_output)
            
            return error_output


    def worker(self, hostnames_queue: queue.Queue) -> None:
        """
        Worker thread to process hostnames from the queue.
        """
        thread_id = threading.get_ident()

        while not self.exit_event.is_set():  # Continue processing until an exit signal is received
            try:
                hostname = hostnames_queue.get_nowait()
                output = self.make_request(hostname, thread_id)
                if self.outputfile:  # Save the output to a file if specified
                    with open(self.outputfile, 'a') as file:
                        file.write(output + "\n")
                hostnames_queue.task_done()
            except queue.Empty:  # Break the loop if the queue is empty
                break

        remaining_threads = threading.active_count() - 1  # Excluding the main thread
        print(f"Thread ID: {thread_id} is exiting. Remaining threads: {remaining_threads} of {self.num_workers}")

    def exit_signal_handler(self, signum: int, frame) -> None:
        """
        Handle exit signal to terminate the application gracefully.
        """
        print("Exiting due to Ctrl+C")
        self.exit_event.set()

    def main(self, __random_hostnames) -> None:
        """
        Main function to execute the multi-threaded connection script.
        """
        signal.signal(signal.SIGINT, self.exit_signal_handler)

        # Create a queue and add the contents of selected_hostnames to it.
        hostnames_queue = queue.Queue()
        [hostnames_queue.put(host) for host in __random_hostnames]

        # Create a threads list
        threads = []
        for _ in range(self.num_workers):
            t = threading.Thread(target=self.worker, args=(hostnames_queue,))
            threads.append(t)
            t.start()

        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            exit_event.set()
            for t in threads:
                t.join()

        print("All worker threads have completed.")
