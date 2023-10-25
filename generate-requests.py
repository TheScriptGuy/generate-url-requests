# Author:                   TheScriptGuy
# Date:                     2023-10-25
# Version:                  0.03
# Description:              Generate a random number of requests to a random sample of hostsnames.

import argparse
import sys
from FileManager import FileManager
from ConnectionManager import ConnectionManager

from datetime import datetime, timedelta

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Connect to random hostnames with multiple threads.')
    parser.add_argument('--cleanup', action='store_true', help='Clean up downloaded files and exit.')
    parser.add_argument('num_connections', type=int, nargs='?', default=100, help='Number of connections to establish. Default 100.')
    parser.add_argument('num_workers', type=int, nargs='?', default=10, help='Number of worker threads. Default 10.')
    parser.add_argument('--outputfile', type=str, help='Save output to a file.')

    args = parser.parse_args()

    if args.cleanup:
        FileManager.cleanup_files(["top-1m.csv", "top-1m.csv.zip"])
        sys.exit(0)

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    file_manager = FileManager(yesterday)
    file_manager.download_and_extract_file(yesterday)
    file_manager.load_csv()
    file_manager.get_random_sample(args.num_connections)

    connection_manger = ConnectionManager(num_connections=args.num_connections, num_workers=args.num_workers, outputfile=args.outputfile if args.outputfile else None)
    connection_manger.main(file_manager.random_sample)
