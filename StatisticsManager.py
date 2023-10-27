from typing import List, Tuple, Dict
from datetime import timedelta

class StatisticsManager:
    """
    A class to manage and calculate statistics of HTTP requests.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of StatisticsManager.
        """
        # A list of tuples to store hostname, response code, response reason, and response time
        self._data: List[Tuple[str, int, str, timedelta]] = []

    def add_data(self, hostname: str, response_code: int, response_message: str, response_time: timedelta) -> None:
        """
        Adds new data to the list.

        :param hostname: the hostname the request was made to
        :param response_code: the HTTP response code
        :param response_message: the HTTP response message
        :param response_time: the time it took to get the response
        """
        # Appending a new data tuple to the internal list
        self._data.append((hostname, response_code, response_message, response_time))

    @staticmethod
    def timedelta_to_str(td: timedelta) -> str:
        """
        Convert a timedelta object into a string format representing seconds 
        followed by two digits of microseconds.
    
        :param td: timedelta object to be converted
        :return: string representing the timedelta in custom format
        """
        total_seconds = td.total_seconds()
    
        # Formatting the string to show seconds followed by two digits of microseconds
        result_str = f"{total_seconds:.2f}"
    
        return result_str

    def calculate_statistics(self) -> Dict[str, object]:
        """
        Calculates min, max, and average response times, and the count of each unique HTTP response code and message.

        :return: a dictionary containing the statistics
        """

        # Checking if there is any data to calculate statistics
        if not self._data:
            return {}  # Returning an empty dictionary if no data available

        # Finding the minimum response time
        #min_time = min(data[3] for data in self._data)
        # Ensuring that only datetime.timedelta objects are used in the comparison
        min_time = min(data[3] for data in self._data if isinstance(data[3], timedelta))

        
        # Finding the maximum response time
        #max_time = max(data[3] for data in self._data)
        max_time = max(data[3] for data in self._data if isinstance(data[3], timedelta))


        # Calculating the total time by summing the total seconds of each timedelta object
        #total_time = sum(data[3].total_seconds() for data in self._data)
        total_time = sum(data[3].total_seconds() for data in self._data if isinstance(data[3], timedelta))
        
        # Calculating the average time
        avg_time = total_time / len(self._data)
        f_avg_time = f"{avg_time:.2f}"

        # Counting the occurrences of each unique representation of HTTP response code and response reason
        response_codes = {}
        for _, response_code, response_message, _ in self._data:
            # Creating a unique key as a tuple of response_code and response_message
            key = (response_code, response_message)
            
            # Counting each unique key occurrence
            response_codes[key] = response_codes.get(key, 0) + 1

        # Returning the calculated statistics as a dictionary
        return {
            'min_time': self.timedelta_to_str(min_time),  # Minimum response time
            'max_time': self.timedelta_to_str(max_time),  # Maximum response time
            'avg_time': f_avg_time,  # Average response time
            'response_codes': response_codes  # Count of each unique HTTP response code and message
        }
