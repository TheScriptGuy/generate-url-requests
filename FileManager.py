# Author:                   TheScriptGuy
# Date:                     2023-10-24
# Version:                  0.01
# Description:              FileManager class used for file operations

import os
import random
import sys
import requests
import csv
import zipfile


class FileManager:
    def __init__(self, __date: str):
        self.CLASS_VERSION = "0.01"
        self.url = f"http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m-{__date}.csv.zip"
        self.zip_path = "top-1m.csv.zip"
        self.response = None
        self.hostnames = []
        self.random_sample = []

    def download_file(self, __url: str) -> requests.Response:
        """
        Download the file and return the response.
        """
        print(f"Attempting to download source file {__url}")
        try:
            self.response = requests.get(__url)
            self.response.raise_for_status()  # Check for HTTP errors (404 in this case)
            print("Download successful.")
        except requests.exceptions.RequestException as e:
            print(f"Error while downloading the file. {e}")
            sys.exit(1)

    @staticmethod
    def save_file(__response_content, __zip_path: str) -> None:
        """
        Save the response content to a file.
        """
        print("Saving contents to file.")
        with open(__zip_path, 'wb') as file:
            file.write(__response_content)
        print("Save successful.")

    @staticmethod
    def unzip_file(__zip_path: str) -> None:
        """
        Unzip the downloaded file.
        """
        print(f"Attempting to extract {__zip_path}")
        try:
            with zipfile.ZipFile(__zip_path, 'r') as zip_ref:
                zip_ref.extractall()
            print(f"Extraction successful.")
        except zipfile.BadZipFile:
            print(f"Downloaded zip file is not a zip file.")
            sys.exit(1)

    def download_and_extract_file(self, date: str) -> None:
        """
        Download and extract the ZIP file containing hostnames.
        """
        # Download the file from self.url
        self.download_file(self.url)  # Download the file

        # Save the response to the zip_path
        self.save_file(self.response.content, self.zip_path)  # Save the downloaded file

        # Set the response to None
        self.response = None

        # Unzip the file.
        self.unzip_file(self.zip_path)  # Unzip the saved file

    def load_csv(self) -> None:
        """
        Load the hostnames from the CSV file into a list.
        """

        with open("top-1m.csv", mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                self.hostnames.append(row[1])

    @staticmethod
    def cleanup_files(files_to_remove: list[str]) -> None:
        """
        Remove specified files and directories.
        """
        for file_path in files_to_remove:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Successfully removed {file_path}")
                else:
                    print(f"No such file: '{file_path}'")
            except Exception as e:
                print(f"An error occurred while trying to remove '{file_path}': {e}")
                sys.exit(1)

    def get_random_sample(self, __num_connections: int) -> None:
        """
        Get a random sample of from the __hostnames.
        """
        self.random_sample = random.sample(self.hostnames, __num_connections)
