from typing import List, Tuple, Dict
from datetime import timedelta
from HttpStatusCodes import HttpStatusCode

class StatisticsManager:
    """
    A class to manage and calculate statistics of HTTP requests.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of StatisticsManager.
        """
        # Define the class version

        self.CLASS_VERSION = "0.01"
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

    def print_statistics(self) -> None:
        """
        Print the statistics for user friendly output.
        """
        print("-" * 30)
        print("Statistics:")
        finished_output = self.calculate_statistics()

        # Formatting the output
        print(f"Minimum time: {finished_output['min_time']}s")
        print(f"Maximum time: {finished_output['max_time']}s")
        print(f"Average time: {finished_output['avg_time']}s\n")

        # Print headers
        print(f"{'HTTP Response Code':<30}{'Count':<10}")

        # Collating the counts of each unique HTTP response code
        collated_counts = {}
        for (code, _), count in finished_output['response_codes'].items():
            if code not in collated_counts:
                collated_counts[code] = 0
            collated_counts[code] += count

        # Sorting the collated counts in descending order
        sorted_collated_counts = sorted(collated_counts.items(), key=lambda x: x[1], reverse=True)

        # Printing the sorted, collated counts
        for code, count in sorted_collated_counts:
            print(f"{code:03} - {HttpStatusCode.get_status_message(code):<24}{count:<10}")
