# Author:                   TheScriptGuy
# Date:                     2025-01-03
# Version:                  0.02
# Description:              Generate a random number of requests to a random sample of hostnames.

import argparse
import sys

from FileManager import FileManager
from ConnectionManager import ConnectionManager
from ThreadManager import ThreadManager
from StatisticsManager import StatisticsManager
from MessageManager import MessageManager

from datetime import datetime, timedelta

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Connect to random hostnames with multiple threads.')
    parser.add_argument('--cleanup', action='store_true', help='Clean up downloaded files and exit.')
    parser.add_argument('num_connections', type=int, nargs='?', default=100, help='Number of connections to establish. Default 100.')
    parser.add_argument('num_workers', type=int, nargs='?', default=3, help='Number of worker threads. Default 3.')
    parser.add_argument('--insecure', action='store_true', help='Allow insecure connections.')

    # Add delay argument group (mutually exclusive)
    delay_group = parser.add_mutually_exclusive_group()
    delay_group.add_argument('--delay', type=int, help='Constant delay in seconds (0-10) before each request.')
    delay_group.add_argument('--random-delay', type=int, dest='random_delay_max',
                           help='Random delay between 0 and specified seconds (max 10) before each request.')

    args = parser.parse_args()

    # Add validation for delay arguments
    if args.delay is not None and (args.delay < 0 or args.delay > 10):
        print("Error: Delay must be between 0 and 10 seconds")
        sys.exit(1)
    if args.random_delay_max is not None and (args.random_delay_max < 0 or args.random_delay_max > 10):
        print("Error: Random delay maximum must be between 0 and 10 seconds")
        sys.exit(1)

    if args.cleanup:
        FileManager.cleanup_files(["top-1m.csv", "top-1m.csv.zip"])
        sys.exit(0)

    # Work out what yesterday's date was.
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    # Define a file_manager object based off yesterday's date
    file_manager = FileManager(yesterday)

    # Download and extract the csv file from Umbrella
    file_manager.download_and_extract_file(yesterday)

    # Load the csv into memory
    file_manager.load_csv()

    # Get a random sample based off the number of connections we need to establish
    file_manager.get_random_sample(args.num_connections)

    # Define a proxy setting
    proxy_settings = {
        "https": "http://proxy1.domain.com:8080",
        "http": "http://proxy1.domain.com:8080"
    }

    # Custom HTTP Headers
    http_headers = {
        "X-Authenticated-User": "",
        "User-Agent": "MyTestUserAgent/1.0"
    }

    # Define a connection_manager object.
    connection_manger = ConnectionManager(
            secure=not(args.insecure),
            use_proxy=True,
            proxy_settings=proxy_settings,
            http_headers=http_headers
            delay=args.delay,
            random_delay_max=args.random_delay_max
    )

    # Define a statistics_manager object
    statistics_manager = StatisticsManager()

    # Define a message_manager object.
    message_manager = MessageManager()

    # Define a thread_manager object.
    thread_manager = ThreadManager(args.num_workers, connection_manger.make_request, statistics_manager, message_manager)

    # Create the queues and threads to work through.
    thread_manager.start(file_manager.random_sample, "hostnames_queue", "hostnames_thread_list")

    # Wait until all the threads have finished.
    thread_manager.join_threads("hostnames_thread_list")

    print("All worker threads have completed.")

    # Set the message_manager exit event
    thread_manager.message_manager.message_exit_event = True

    # Print the statistics from all the work that has been done.
    statistics_manager.print_statistics()
