import os
import base64
from flask import Flask, request
from waitress import serve
from io import BytesIO
import numpy as np
import MySQLdb
from matplotlib.figure import Figure

app = Flask(__name__)


class Analysis:
    def __init__(self) -> None:
        self.DB_HOST = os.environ.get('DB_HOST')
        self.DB_USER = os.environ.get('DB_USER')
        self.DB_PASS = os.environ.get('DB_PASS')
        self.DB_NAME = os.environ.get('DB_NAME')
        self.FUNCTION_NAME = os.environ.get('FUNCTION_NAME', '')
        self.db = None
        self.db_c = None
        self.connect_db()
        # Analysis attributes
        self.report = request.args.get('report', 'home')
        self.cpu = request.args.get('cpu', None)
        self.memory = request.args.get('memory', None)
        self.factorial = request.args.get('factorial', None)
        self.type_of_app = request.args.get('app', None)

        self.cpu_mem_comb = [(1, 2), (1, 3), (1, 4), (2, 4)]
        self.apps = ['hello-world', 'factorial']
        self.factorials = [10, 1000, 10000, 32000, 43000, 50000, 60000]

    def connect_db(self):
        # DB Connection
        self.db = MySQLdb.connect(
            host=self.DB_HOST, db=self.DB_NAME, user=self.DB_USER, passwd=self.DB_PASS)
        # Setting to use dictionaries instead of tuples (default)
        self.db_c = self.db.cursor(MySQLdb.cursors.DictCursor)

    def route(self):

        if self.report == 'home':
            return self.home()
        elif self.report == 'performance':
            return self.performance()

        return f"Oops... I didn't find anything here... <a href='/{self.FUNCTION_NAME}'>Go back to home</a>?"

    def home(self):
        page = "<h1>Reports</h1>"

        for app in self.apps:
            page = page + f"<h2>App {app}</h2> <ul>"

            if app == 'hello-world':
                for cpu, mem in self.cpu_mem_comb:
                    page = page + \
                        f'<li><a href="/{self.FUNCTION_NAME}?report=performance&app=hello&cpu={cpu}&memory={mem}">Performance Hello World - {cpu} CPU & {mem} Memory</a></li>'
            elif app == 'factorial':
                for cpu, mem in self.cpu_mem_comb:
                    for factorial_param in self.factorials:
                        page = page + \
                            f'<li><a href="/{self.FUNCTION_NAME}?report=performance&app={app}&cpu={cpu}&memory={mem}&factorial={factorial_param}">Performance Factorial {factorial_param} - {cpu} CPU & {mem} Memory</a></li>'

            page = page + '</ul>'
        return page

    def performance(self):
        query = f"""SELECT
                    csp,
                    min(app_execution_time_min) as  app_execution_time_min,
                    avg(app_execution_time_avg) as  app_execution_time_avg,
                    max(app_execution_time_max) as  app_execution_time_max
                    FROM metrics
                    WHERE
                    memory = {self.memory} AND
                    cpu = {self.cpu} AND
                    type = '{self.type_of_app}'
                    """
        if self.type_of_app == 'factorial':
            query = query + f" AND factorial = {self.factorial}"

        query = query + """
                    GROUP BY csp
                    ORDER BY csp
                """

        
        self.db_c.execute(query)
        data = self.db_c.fetchall()
        
        labels = []
        min_data = []
        avg_data = []
        max_data = []

        for item in data:
            labels.append(item.get('csp'))
            min_data.append(item.get('app_execution_time_min'))
            avg_data.append(item.get('app_execution_time_avg'))
            max_data.append(item.get('app_execution_time_max'))

        # return str(data)

        x = np.arange(len(labels))  # the label locations
        width = 0.20  # the width of the bars
        fig = Figure()
        ax = fig.subplots()
        rect_min = ax.bar(x - width, min_data, width, label='Min')
        rect_avg = ax.bar(x, avg_data, width, label='Avg')
        rect_max = ax.bar(x + width, max_data, width, label='Max')

        # # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('millisecond (ms)')
        ax.set_title(f'Mininimum, Average and Maximum response times for {self.type_of_app} {self.factorial}')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        # self.label_bars(rects1, ax)
        # self.label_bars(rects2, ax)

        buf = BytesIO()
        fig.savefig(buf, format="png")
        img_base64 = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{img_base64}'/>"


@app.route("/")
def main():
    analysis = Analysis()
    return analysis.route()

# Handler for GCP Cloud Function
def handler(request):
    analysis = Analysis()
    return analysis.route()


if __name__ == "__main__":
    # Serving the app using Waitress
    app.logger.info("Starting Webserver")
    serve(app, host='0.0.0.0', port=5000, threads=4)
