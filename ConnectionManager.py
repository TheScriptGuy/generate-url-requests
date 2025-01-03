# Author:                   TheScriptGuy
# Date:                     2025-01-03
# Version:                  0.11
# Description:              ConnectionManager class used for URL connectivity operations (multithreaded)
import requests
import random
import time
from urllib3.exceptions import InsecureRequestWarning, NewConnectionError, MaxRetryError
from datetime import datetime
from typing import Dict, Optional

class ConnectionManager:
    def __init__(self, 
                secure: bool = True,
                use_proxy: bool = False,
                proxy_settings: Optional[Dict[str, str]] = None,
                http_headers: Optional[Dict[str, str]] = None,
                delay: Optional[int] = None,
                random_delay_max: Optional[int] = None
                ):
        self.CLASS_VERSION = "0.11"
        self.secure = secure
        self.use_proxy = use_proxy
        self.proxy_settings = proxy_settings if use_proxy else None
        self.http_headers = http_headers or {}
        self.delay = delay
        self.random_delay_max = random_delay_max

        # Validate delay parameters
        if delay is not None and (delay < 0 or delay > 10):
            raise ValueError("Delay must be between 0 and 10 seconds")
        if random_delay_max is not None and (random_delay_max < 0 or random_delay_max > 10):
            raise ValueError("Random delay maximum must be between 0 and 10 seconds")

        # Print the startup metrics
        self.print_variables()

    def print_variables(self) -> None:
        """
        Print variables.
        """
        print(f"Secure/Verify Connections = {self.secure}, Use Proxy = {self.use_proxy}, "
              f"Proxy Settings = {self.proxy_settings}, HTTP Headers = {self.http_headers}, "
              f"Delay = {self.delay}s, Random Delay Max = {self.random_delay_max}s")

    def make_request(self, hostname: str, thread_id: int, statistics_manager) -> str:
        """
        Attempt to connect to a hostname using HTTPS and then HTTP, logging the results.
        """
        # Calculate and apply delay if needed
        applied_delay = 0
        if self.delay is not None:
            applied_delay = self.delay
            time.sleep(applied_delay)
        elif self.random_delay_max is not None:
            applied_delay = random.randint(0, self.random_delay_max)
            time.sleep(applied_delay)

        # Format delay for output
        delay_str = f"{applied_delay:02d}"

        final_output = ""  # Variable to store the final output

        thread_info = f"TID: {thread_id}, D: {delay_str}s"

        # Suppress only the single warning from urllib3 needed.
        if not self.secure:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

        protocols = ['https', 'http']
        for protocol in protocols:
            # Lets assume an exception won't be triggered.
            exception_triggered = False
            exception_error = ""
            output = ""
            error_detail = None
            error_output = None

            start_time = datetime.now()  # Start the timer

            # Attempting to connect to the hostname
            try:
                request_kwargs = {
                    "timeout": 5,
                    "verify": self.secure,
                    "headers": self.http_headers
                }

                if self.use_proxy and self.proxy_settings:
                    request_kwargs["proxies"] = self.proxy_settings
                response = requests.get(f"{protocol}://{hostname}", **request_kwargs)

                # Lets check the HTTP Response code first.
                if response.status_code == 400:
                    if "query parameters specified" in response.reason:
                        # This is the response: Value for one of the query parameters specified in the request URI is invalid.
                        # Let us adjust that to Invalid query parm.
                        output = f"{thread_info}, SC: (Invalid query parm ), Hostname: {protocol}://{hostname}"
                    else:
                        # Format the result
                        output = f"{thread_info}, SC: {response.status_code} ({response.reason: <20}), Hostname: {protocol}://{hostname}"
                elif response.status_code == 503:
                    output = f"{thread_info}, SC: {response.status_code} (Service Unavailable ), Hostname: {protocol}://{hostname}"
                else:  # Handling other status codes here
                    output = f"{thread_info}, SC: {response.status_code} ({response.reason: <20}), Hostname: {protocol}://{hostname}"

            except requests.exceptions.ConnectionError as e:
                if "Name or service not known" in str(e):
                    error_detail = "DNS resolution issue"
                elif "Connection refused" in str(e):
                    error_detail = "Connection refused"
                else:
                    error_detail = "Connection error"

                error_output = f"{thread_info}, SC: 000 ({error_detail: <20}), Hostname: {protocol}://{hostname}"
                exception_triggered = True

            except requests.exceptions.InvalidSchema:
                error_output = f"{thread_info}, SC: 000 (Invalid Schema       ), Hostname: {protocol}://{hostname}"
                exception_triggered = True
                exception_error = "Invalid Schema"

            except requests.exceptions.ReadTimeout:
                error_output = f"{thread_info}, SC: 000 (Read timeout        ), Hostname: {protocol}://{hostname}"
                exception_triggered = True
                exception_error = "Read timeout"

            except requests.exceptions.TooManyRedirects:
                error_output = f"{thread_info}, SC: 000 (Too many redirects   ), Hostname: {protocol}://{hostname}"
                exception_triggered = True
                exception_error = "Too many redirects"

            except requests.exceptions.ChunkedEncodingError:
                error_output = f"{thread_info}, SC: 000 (Chunk Encoding Error ), Hostname {protocol}://{hostname}"
                exception_triggered = True
                exception_error = "Chunked Encoding Error"

            except requests.exceptions.ConnectTimeout:
                error_output = f"{thread_info}, SC: 000 (Connection Timeout   ), Hostname: {protocol}://{hostname}"
                exception_triggered = True
                exception_error = "Connection Timeout"            

            except urllib3.exceptions.ProtocolError:
                error_output = f"{thread_info}, SC: 000 (Protocol Error       ), Hostname: {protocol}://{hostname}"
                exception_triggered = True
                exception_error = "Protocol Error"

            except requetss.exceptions.SSLError:
                if protocol == 'https':  # If HTTPS fails due to SSLError, let it retry with HTTP
                    error_output = f"{thread_info}, SC: 000 (SSL Error            ), Hostname: {protocol}://{hostname}"
                    continue

            # Additional exception handling for proxy errors
            except (NewConnectionError, MaxRetryError) as e:
                error_output = f"{thread_info}, SC: 000 (Proxy Connection Error), Hostname: {protocol}://{hostname}"
                exception_triggered = True

            except requests.exceptions.RequestException as e:
                error_output = f"{thread_info}, An error occurred while connecting to {protocol}://{hostname}: {e}"
                exception_triggered = True

            end_time = datetime.now()  # Stop the timer

            if not exception_triggered:
                # Calculate the response time
                response_time = end_time - start_time

                # Update the statistics
                statistics_manager.add_data(hostname, response.status_code, response.reason, response_time)
            else:
                response_time = 0
                statistics_manager.add_data(hostname, 0, error_detail or exception_error, response_time)
                exception_error = ""
                exception_triggered = False

            # Store the output to return after the loop ends
            final_output = output or error_output

            # Display the output or error_output.
            #print(final_output)

            # If it is a successful HTTPS request, no need to try HTTP
            if output:
                break

        return final_output
