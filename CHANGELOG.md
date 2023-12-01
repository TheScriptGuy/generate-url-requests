# 2023-11-30
# Version 0.11
* Created a messages queue to help with displaying output to stdout.

# 2023-11-11
## Version 0.10
* Fixing [traceback errors](https://github.com/TheScriptGuy/generate-url-requests/issues/1)

# 2023-11-09
## Version 0.09
* Adding a dedicated ThreadManager class to align with better coding practices.
* Temporarily removing the outputfile argument.

# 2023-11-08
## Version 0.08
* Changing default workers from 10 to 3.
* Adding an `--insecure` argument to allow for insecure connections.

# 2023-10-26
## Version 0.07
* Adding a Statistics calcuation at the end.
* Adding a HttpStatusCodes class to help with error code output.

## Version 0.06
* Fixing logic with HTTP status codes and displaying correct errors.
* Fixing logic with HTTPS and HTTP requests.
* Adding a StatisticsManager class to help calculate some small statistics based off the requests.

# 2023-10-25
## Version 0.05
* Fixing minor print bug for when a site is working

## Version 0.04
* Fixing minor print bug for `num_workers`

## Version 0.03
* Adding printing of startup variables.

## Version 0.02
* Improved handling of errors when requesting websites and they're Unavailable
    * `ConnectionError`, `ReadTimeout`, `TooManyRedirects`, `ConnectTimeoutError`, `ConnectTimeout`, `SSLError`, `RequestException`

# 2023-10-24
## Version 0.01
* Initial push of python code.
