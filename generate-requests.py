# Author:                   TheScriptGuy
# Date:                     2023-11-10
# Version:                  0.08
# Description:              Generate a random number of requests to a random sample of hostnames.

import argparse
import sys

from FileManager import FileManager
from ConnectionManager import ConnectionManager
from ThreadManager import ThreadManager
from StatisticsManager import StatisticsManager

from datetime import datetime, timedelta

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Connect to random hostnames with multiple threads.')
    parser.add_argument('--cleanup', action='store_true', help='Clean up downloaded files and exit.')
    parser.add_argument('num_connections', type=int, nargs='?', default=100, help='Number of connections to establish. Default 100.')
    parser.add_argument('num_workers', type=int, nargs='?', default=3, help='Number of worker threads. Default 3.')
    parser.add_argument('--insecure', action='store_true', help='Allow insecure connections.')

    args = parser.parse_args()

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

    # Define a connection_manager object.
    connection_manger = ConnectionManager(secure=not(args.insecure))

    # Define a statistics_manager object
    statistics_manager = StatisticsManager()

    # Define a thread_manager object.
    thread_manager = ThreadManager(args.num_workers, connection_manger.make_request, statistics_manager)

    # Create the queues and threads to work through.
    thread_manager.start(file_manager.random_sample, "hostnames_queue", "hostnames_thread_list")

    # Wait until all the threads have finished.
    thread_manager.join_threads()

    print("All worker threads have completed.")

    # Print the statistics from all the work that has been done.
    statistics_manager.print_statistics()