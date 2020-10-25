import os
import base64
from flask import Flask, request
from waitress import serve
from io import BytesIO
import numpy as np
import MySQLdb
from matplotlib.figure import Figure
from pricing import Pricing
from performance import Performance

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

        #objects
        self.performance = Performance(self.db_c, self.FUNCTION_NAME)
        self.pricing = Pricing(self.db_c, self.FUNCTION_NAME)

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
            return self.performance_analysis()
        elif self.report == 'pricing':
            return self.pricing_analysis()

        return f"Oops... I didn't find anything here... <a href='/{self.FUNCTION_NAME}'>Go back to home</a>?"

    def home(self):
        html = "<h1>Reports</h1>"
        html += self.performance.get_reports_links()
        html += self.pricing.get_reports_links()
        
        return html

    def performance_analysis(self):
        cpu = request.args.get('cpu', None)
        memory = request.args.get('memory', None)
        factorial = request.args.get('factorial', None)
        type_of_app = request.args.get('app', None)

        return self.performance.get_diagram(type_of_app, cpu, memory, factorial)
    
    def pricing_analysis(self):
        pricing_scenario = request.args.get('scenario', None)
        if pricing_scenario is not None:
            return self.pricing.get_diagram(pricing_scenario)
        else:
            return self.pricing.get_crossing_diagram()


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
