# Multi-threaded URL Accessor

This script is a multi-threaded URL accessor. It downloads a list of top URLs from Umbrella (Top 1 million hosts), selects a random subset of them, and attempts to connect to each URL via HTTP and HTTPS protocols.

## Features

- Multi-threading to speed up the checking process
- Handles both HTTPS (preferred) and HTTP protocols
- Graceful termination upon receiving Ctrl+C
- Allow insecure connections

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
$ python generate-requests.py [num_connections] [num_workers] [--insecure]
```

# Establishing 200 connections using 20 worker threads
(as a side note here, unless you have a fairly resource friendly host to run this on, this could very quickly exhaust all resources on the server, or make too many DNS requests to your DNS providers.
```bash
$ python generate-requests.py 200 20
```

# To establish an insecure connection
(To allow certificate warnings - useful for when you do not have the correct certificates installed.)
```bash
$ python generate-requests.py 200 20 --insecure
```