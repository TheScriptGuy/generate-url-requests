# Multi-threaded URL Accessor

This script is a multi-threaded URL accessor. It downloads a list of top URLs from Umbrella (Top 1 million hosts), selects a random subset of them, and attempts to connect to each URL via HTTP and HTTPS protocols.

## Features

- Multi-threading to speed up the checking process
- Handles both HTTP and HTTPS protocols
- Graceful termination upon receiving Ctrl+C
- Option to output results to a file

## Dependencies

- `requests`

## Installation

Before running the script, ensure that you have the `requests` library installed in your Python environment. You can install it using `pip`:

```bash
pip install requests
```

## Usage

You can run this script from the command line using the following syntax:

```bash
$ python generate-requests.py [num_connections] [num_workers] [--outputfile OUTPUTFILE]
```

# Establishing 200 connections using 20 worker threads, with output saved to output.txt
```bash
$ python script_name.py 200 20 --outputfile output.txt
```