# Author:                   TheScriptGuy
# Date:                     2023-11-08
# Version:                  0.08
# Description:              ConnectionManager class used for URL connectivity operations (multithreaded)

import threading
import queue
import signal
import requests
from urllib3.exceptions import InsecureRequestWarning

from typing import List, Optional
from StatisticsManager import StatisticsManager
from datetime import datetime

class ConnectionManager:
    def __init__(self, num_connections: int, num_workers: int, outputfile: Optional[str], secure = True):
        self.CLASS_VERSION = "0.08"
        self.num_connections = num_connections
        self.num_workers = num_workers
        self.outputfile = outputfile
        self.secure = secure

        # Print the startup metrics
        self.print_variables()

        # Define a global exit event for all threads to track on.
        self.exit_event = threading.Event()

        # Define a StatisticsManager Object
        self.statistics_manager = StatisticsManager()

    def print_variables(self) -> None:
        """
        Print variables.
        """
        print(f"Number of connections to establish = {self.num_connections}")
        print(f"Number of workers = {self.num_workers}")
        print(f"Secure/Verify Conections = {self.secure}")

    def make_request(self, hostname: str, thread_id: int) -> str:
        """
        Attempt to connect to a hostname using HTTPS and then HTTP, logging the results.
        """

        final_output = ""  # Variable to store the final output

        # Suppress only the single warning from urllib3 needed.
        if not self.secure:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        protocols = ['https', 'http']
        for protocol in protocols:
            if self.exit_event.is_set():  # Check if the exit signal is set
                return

            # Lets assume an exception won't be triggered.
            exception_triggered = False
            exception_error = ""
            output = ""
            error_detail = None
            error_output = None

            start_time = datetime.now()  # Start the timer

            # Attempting to connect to the hostname
            try:
                response = requests.get(f"{protocol}://{hostname}", timeout=5, verify=self.secure)
               
                # Lets check the HTTP Response code first.
                if response.status_code == 400:
                    if "query parameters specified" in response.reason:
                        # This is the response: Value for one of the query parameters specified in the request URI is invalid.
                        # Let us adjust that to Invalid query parm.
                        output = f"Thread ID: {thread_id}, Status Code: {response.status_code} (Invalid query parm ), Hostname: {protocol}://{hostname}"
                    else:
                        # Format the result
                        output = f"Thread ID: {thread_id}, Status Code: {response.status_code} ({response.reason: <20}), Hostname: {protocol}://{hostname}"
                elif response.status_code == 503:
                    output = f"Thread ID: {thread_id}, Status Code: {response.status_code} (Service Unavailable), Hostname: {protocol}://{hostname}"
                else:  # Handling other status codes here
                    output = f"Thread ID: {thread_id}, Status Code: {response.status_code} ({response.reason: <20}), Hostname: {protocol}://{hostname}"

            except requests.exceptions.ConnectionError as e:
                if "Name or service not known" in str(e):
                    error_detail = "DNS resolution issue"
                elif "Connection refused" in str(e):
                    error_detail = "Connection refused"
                else:
                    error_detail = "Connection error"
               
                error_output = f"Thread ID: {thread_id}, Status Code: 000 ({error_detail: <20}), Hostname: {protocol}://{hostname}"
                exception_triggered = True

            except requests.exceptions.InvalidSchema:
                error_output = f"Thread ID: {thread_id}, Status Code: 000 (Invalid Schema       ), Hostname: {protocol}://{hostname}"
                exception_triggered = True
                exception_error = "Invalid Schema"

            except requests.exceptions.ReadTimeout:
                error_output = f"Thread ID: {thread_id}, Status Code: 000 (Read timeout         ), Hostname: {protocol}://{hostname}"
                exception_triggered = True
                exception_error = "Read timeout"

            except requests.exceptions.TooManyRedirects:
                error_output = f"Thread ID: {thread_id}, Status Code: 000 (Too many redirects   ), Hostname: {protocol}://{hostname}"
                exception_triggered = True
                exception_error = "Too many redirects"

            except requests.exceptions.ConnectTimeoutError:
                error_output = f"Thread ID: {thread_id}, Status Code: 000 (Connection Timeout   ), Hostname: {protocol}://{hostname}"
                exception_triggered = True
                exception_error = "Connection Timeout"

            except requests.exceptions.ConnectTimeout:
                error_output = f"Thread ID: {thread_id}, Status Code: 000 (Connection Timeout   ), Hostname: {protocol}://{hostname}"
                exception_triggered = True
                exception_error = "Connection Timeout"

            except requetss.exceptions.SSLError:
                if protocol == 'https':  # If HTTPS fails due to SSLError, let it retry with HTTP
                    error_output = f"Thread ID: {thread_id}, Status Code: 000 (SSL Error            ), Hostname: {protocol}://{hostname}"
                    continue
            except requests.exceptions.RequestException as e:
                error_output = f"Thread ID: {thread_id}, An error occurred while connecting to {protocol}://{hostname}: {e}"
                exception_triggered = True

            end_time = datetime.now()  # Stop the timer
           
            if not exception_triggered:
                # Calculate the response time
                response_time = end_time - start_time
               
                # Update the statistics
                self.statistics_manager.add_data(hostname, response.status_code, response.reason, response_time)
            else:
                response_time = 0
                self.statistics_manager.add_data(hostname, 0, error_detail or exception_error, response_time)
                exception_error = ""
                exception_triggered = False

            # Store the output to return after the loop ends
            final_output = output or error_output

            # Display the output or error_output.
            print(final_output)

            # If it is a successful HTTPS request, no need to try HTTP
            if output:
                break

        return final_output

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
        self.statistics_manager.print_statistics()
