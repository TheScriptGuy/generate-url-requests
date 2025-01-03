# Multi-threaded URL Accessor

This script is a multi-threaded URL accessor. It downloads a list of top URLs from Umbrella (Top 1 million hosts), selects a random subset of them, and attempts to connect to each URL via HTTP and HTTPS protocols.

## Features

- Multi-threading to speed up the checking process
- Handles both HTTPS (preferred) and HTTP protocols
- Graceful termination upon receiving Ctrl+C
- Allow insecure connections
- Allow fixed delays or random delays for each worker thread.

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

# Using a web proxy
First edit the `generate-requests-proxy.py` file and adjust the proxy_settings variable:
```python
# Define a proxy setting
proxy_settings = {
    "https": "http://proxy1.domain.com:8080",
    "http": "http://proxy1.domain.com:8080"
}
```

```bash
$ python generate-requests-proxy.py 200 20
```

# Configuring custom HTTP Headers
Edit either the `generate-requests-proxy.py` or `generate-requests.py` and set http_headers appropriately.
```python
# Custom HTTP Headers
http_headers = {
    "X-Authenticated-User": "",
    "User-Agent": "MyTestUserAgent/1.0"
}
```

# Adding delays to requests
## To add a fixed delay
Use the `--delay` argument to indicate a fixed amount of time (in seconds) that a worker thread will pause before requesting a URL.
In this example, it'll establish 100 connections to URLs using 20 workers with a fixed 5 second delay between each request.
```bash
$ python generate-requests.py --delay 5 100 20
```

## To add a random delay
Use the `--random-delay` argument to indicate a random amount of time (in seconds) that a worker thread will pause before requesting a URL.
In this example, it'll establish 100 connections to URLs using 20 workers with a random delay of up to 10 seconds.
```bash
$ python generate-requests.py --random-delay 10 100 20
```


