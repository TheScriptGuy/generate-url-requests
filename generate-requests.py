import requests
import csv
import zipfile
import threading
import queue
import argparse
import random
import signal

from typing import List, Optional
from datetime import datetime, timedelta

exit_event = threading.Event()

def download_and_extract_file(date: str) -> None:
    """
    Download and extract the ZIP file containing hostnames.
    """
    url = f"http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m-{date}.csv.zip"
    zip_path = "top-1m.csv.zip"
    
    # Downloading the zip file
    response = requests.get(url)
    with open(zip_path, 'wb') as file:
        file.write(response.content)
    
    # Extracting the contents of the zip file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall()

def load_csv() -> List[str]:
    """
    Load the hostnames from the CSV file into a list.
    """
    hostnames = []
    with open("top-1m.csv", mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            hostnames.append(row[1])
    return hostnames

def make_request(hostname: str, thread_id: int) -> str:
    """
    Attempt to connect to a hostname using HTTPS and then HTTP, logging the results.
    """
    protocols = ['https', 'http']
    for protocol in protocols:
        if exit_event.is_set():  # Check if the exit signal is set
            return
        
        # Attempting to connect to the hostname
        try:
            response = requests.get(f"{protocol}://{hostname}", timeout=5)
            output = f"Thread ID: {thread_id}, Hostname: {hostname}, Status Code: {response.status_code} ({response.reason})"
            print(output)
            return output
        except requests.exceptions.RequestException as e:
            error_output = f"Thread ID: {thread_id}, Error connecting to {protocol}://{hostname}: {e}"
            print(error_output)
            return error_output

def worker(hostnames_queue: queue.Queue) -> None:
    """
    Worker thread to process hostnames from the queue.
    """
    thread_id = threading.get_ident()

    while not exit_event.is_set():  # Continue processing until an exit signal is received
        try:
            hostname = hostnames_queue.get_nowait()
            output = make_request(hostname, thread_id)
            if args.outputfile:  # Save the output to a file if specified
                with open(args.outputfile, 'a') as file:
                    file.write(output + "\n")
            hostnames_queue.task_done()
        except queue.Empty:  # Break the loop if the queue is empty
            break
    
    remaining_threads = threading.active_count() - 1  # Excluding the main thread
    print(f"Thread ID: {thread_id} is exiting. Remaining threads: {remaining_threads} of {args.num_workers}")

def exit_signal_handler(signum: int, frame) -> None:
    """
    Handle exit signal to terminate the application gracefully.
    """
    print("Exiting due to Ctrl+C")
    exit_event.set()

def main(num_connections: int, num_workers: int, outputfile: Optional[str]) -> None:
    """
    Main function to execute the multi-threaded connection script.
    """
    signal.signal(signal.SIGINT, exit_signal_handler)
    
    # Getting the hostnames
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    download_and_extract_file(yesterday)
    hostnames = load_csv()
    
    selected_hostnames = random.sample(hostnames, num_connections)
    
    hostnames_queue = queue.Queue()
    [hostnames_queue.put(host) for host in selected_hostnames]
    
    threads = []
    for _ in range(num_workers):
        t = threading.Thread(target=worker, args=(hostnames_queue,))
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Connect to random hostnames with multiple threads.')
    parser.add_argument('num_connections', type=int, nargs='?', default=100, help='Number of connections to establish. Default 100.')
    parser.add_argument('num_workers', type=int, nargs='?', default=10, help='Number of worker threads. Default 10.')
    parser.add_argument('--outputfile', type=str, help='Save output to a file.')
    
    args = parser.parse_args()
    
    main(args.num_connections, args.num_workers, args.outputfile)
