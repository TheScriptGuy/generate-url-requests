# Author:                   TheScriptGuy
# Date:                     2023-10-29
# Version:                  0.01
# Description:              HTTP Status Codes class

class HttpStatusCode:
    """
    A class that contains mappings of HTTP status codes to their respective messages
    as per the RFC, and provides a method to retrieve the message based on the status code.
    """
    _STATUS_CODES = {
        000: "None",
        100: "Continue",
        101: "Switching Protocols",
        102: "Processing",
        103: "Early Hints",
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        207: "Multi-Status",
        208: "Already Reported",
        226: "IM Used",
        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        305: "Use Proxy",
        306: "Switch Proxy",
        307: "Temporary Redirect",
        308: "Permanent Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Timeout",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Payload Too Large",
        414: "URI Too Long",
        415: "Unsupported Media Type",
        416: "Range Not Satisfiable",
        417: "Expectation Failed",
        418: "I'm a teapot",
        421: "Misdirected Request",
        422: "Unprocessable Entity",
        423: "Locked",
        424: "Failed Dependency",
        425: "Too Early",
        426: "Upgrade Required",
        428: "Precondition Required",
        429: "Too Many Requests",
        431: "Request Header Fields Too Large",
        451: "Unavailable For Legal Reasons",
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
        505: "HTTP Version Not Supported",
        506: "Variant Also Negotiates",
        507: "Insufficient Storage",
        508: "Loop Detected",
        510: "Not Extended",
        511: "Network Authentication Required"
    }
    def __init__(self):
        """Initializing the class."""
        self.CLASS_VERSION = "0.01"

    @classmethod
    def get_status_message(cls, code: int) -> str:
        """
        Retrieve the message associated with a status code.

        Parameters:
        - code (int): The HTTP status code.

        Returns:
        - str: A message string associated with the status code, or a default message if
               the code is not recognized.
        """
        return cls._STATUS_CODES.get(code, "Unknown Status Code")

    @classmethod
    def get_all_status_codes(self) -> dict:
        """
        Retrieve all status codes and their respective messages.

        Returns:
        - dict: A dictionary containing all status code-message pairs.
        """
        return cls._STATUS_CODES

