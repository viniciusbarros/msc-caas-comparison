
import os
import logging
from datetime import datetime
import time
import json
import glob
import re
import MySQLdb


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("execution.log"),
        logging.StreamHandler()
    ]
)


class MetricReader:
    FILE_NAME_PATTERN = r"metrics/(?P<datetime>[0-9_]{19})_(?P<type>factorial_(?P<factorial>\d{1,6})|hello_world)_(?P<csp>[a-zA-Z]*)_(?P<cpu>[0-9Mim.]*)_cpu_(?P<memory>[0-9Mim.]*)_memory.json"
    DB_HOST = os.environ.get('DB_HOST')
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')
    DB_NAME = os.environ.get('DB_NAME')

    def __init__(self) -> None:
        self.regex_filename = re.compile(self.FILE_NAME_PATTERN)
        self.db = MySQLdb.connect(
            host=self.DB_HOST, db=self.DB_NAME, user=self.DB_USER, passwd=self.DB_PASS)
        self.db_c = self.db.cursor()

    def read_all(self):
        data = []

        files = glob.glob("metrics/*.json")

        for _, filename in enumerate(files):
            data_filename = self.extract_data_from_filename(filename)
            data_content = self.extract_data_from_content(filename)
            full_data = {**data_filename, **data_content}
            data.append(tuple(full_data.values()))

        self.save_in_db(data)
        # Moving read files
        for _, filename in enumerate(files):
            os.rename(filename, filename.replace('metrics/', 'saved_metrics/'))

    def extract_data_from_filename(self, filename):

        match = self.regex_filename.match(filename)
        data = match.groupdict()
        # fixing some
        data['datetime'] = data['datetime'].replace(
            '_', '-', 2).replace('_', ' ', 1).replace('_', ':')
        data['type'] = data['type'].split('_')[0]
        data['cpu'] = data['cpu'].split('.')[0]
        data['memory'] = data['memory'].split('.')[0]
        # normalizing CPU/Memory values
        for item in (('1024', '1'), ('2048', '2'), ('3072', '3'), ('4096', '4'), ('Mi', '')):
            data['cpu'] = data['cpu'].replace(*item)
            data['memory'] = data['memory'].replace(*item)

        return data

    def extract_data_from_content(self, filename):

        f = open(filename, "r")
        raw = json.loads(f.read())

        data = {}
        for prefix in raw['metrics']:

            for metric, val in raw['metrics'][prefix].items():
                metric = metric.replace('(', '').replace(')', '')
                data[f"{prefix}_{metric}"] = val

        return data

    def save_in_db(self, data):
        self.db_c.executemany(
            """INSERT INTO metrics (datetime, type, factorial, csp, cpu, memory, app_execution_time_avg, app_execution_time_max, app_execution_time_med, app_execution_time_min, app_execution_time_p90, app_execution_time_p95, checks_fails, checks_passes, checks_value, data_received_count, data_received_rate, data_sent_count, data_sent_rate, http_req_blocked_avg, http_req_blocked_max, http_req_blocked_med, http_req_blocked_min, http_req_blocked_p90, http_req_blocked_p95, http_req_connecting_avg, http_req_connecting_max, http_req_connecting_med, http_req_connecting_min, http_req_connecting_p90, http_req_connecting_p95, http_req_duration_avg, http_req_duration_max, http_req_duration_med, http_req_duration_min, http_req_duration_p90, http_req_duration_p95, http_req_receiving_avg, http_req_receiving_max, http_req_receiving_med, http_req_receiving_min, http_req_receiving_p90, http_req_receiving_p95, http_req_sending_avg, http_req_sending_max, http_req_sending_med, http_req_sending_min, http_req_sending_p90, http_req_sending_p95, http_req_tls_handshaking_avg, http_req_tls_handshaking_max, http_req_tls_handshaking_med, http_req_tls_handshaking_min, http_req_tls_handshaking_p90, http_req_tls_handshaking_p95, http_req_waiting_avg, http_req_waiting_max, http_req_waiting_med, http_req_waiting_min, http_req_waiting_p90, http_req_waiting_p95, http_reqs_count, http_reqs_rate, iteration_duration_avg, iteration_duration_max, iteration_duration_med, iteration_duration_min, iteration_duration_p90, iteration_duration_p95, iterations_count, iterations_rate, vus_max, vus_min, vus_value, vus_max_max, vus_max_min, vus_max_value)
            VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s )""",
            data
        )
        self.db.commit()


runner = MetricReader()
runner.read_all()
