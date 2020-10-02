
import os
import logging
from datetime import datetime
import time
import json
import glob
import re


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("execution.log"),
        logging.StreamHandler()
    ]
)


class MetricReader:
    FILE_NAME_PATTERN = r"metrics/(?P<datetime>\d{4}_\d{2}_\d{2}_\d{6})_(?P<type>factorial_(?P<factorial>\d{1,6})|hello_world)_(?P<csp>[a-zA-Z]*)_(?P<cpu>[0-9Mim.]*)_cpu_(?P<memory>[0-9Mim.]*)_memory.json"
    FILE_NAME_GROUPS = [
        'datetime',
        'type',
        'factorial',
        'csp',
        'cpu',
        'memory'
    ]

    def __init__(self) -> None:
        self.regex_filename = re.compile(self.FILE_PATTERN)

    def read_all(self):
        data = []

        files = glob.glob("metrics/*.json")

        for _, filename in enumerate(files):
            data.append(self.extract_data(filename))

    def extract_data(self, filename):
        data = {}
        try:
            f = open(filename, "r")
            raw = json.loads(f.read())
            match = self.regex_filename.match(filename)
            for i, key in enumerate(self.FILE_NAME_GROUPS):
                data[key] = match.group(i)
            




        except Exception as e:
            logging.error(f"Failed to read file {filename}")


runner = MetricReader()
runner.read_all()
