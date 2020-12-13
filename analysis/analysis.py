import os
from flask import Flask, request, render_template
from waitress import serve
from io import BytesIO
import numpy as np
import MySQLdb
from matplotlib.figure import Figure
from pricing import Pricing
from performance import Performance
from weekend_vs_weekdays import WeekendVsWeekdays

app = Flask(__name__)


class Analysis:
    """
    This class is responsible for managing and showing
    some basic metrics and also links for plots generated
    on demand.
    It can be served either by Waitress + Flask,
    or it can also be served as a plain python app.
    It is also ready to run in GCP Cloud Function.
    """

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

        # objects
        self.performance = Performance(self.db_c, self.FUNCTION_NAME)
        self.pricing = Pricing(self.db_c, self.FUNCTION_NAME)
        self.weekend_vs_weekdays = WeekendVsWeekdays(
            self.db_c, self.FUNCTION_NAME)

    def connect_db(self):
        # DB Connection
        self.db = MySQLdb.connect(
            host=self.DB_HOST, db=self.DB_NAME, user=self.DB_USER, passwd=self.DB_PASS)
        # Setting to use dictionaries instead of tuples (default)
        self.db_c = self.db.cursor(MySQLdb.cursors.DictCursor)

    def route(self):
        """Based on the report GET/query string parameter, 
        routes and returns a specific function

        Returns:
           response, http code
        """
        if self.report == 'home':
            return self.home()
        elif self.report == 'performance':
            return self.performance_analysis()
        elif self.report == 'pricing':
            return self.pricing_analysis()
        elif self.report == 'weekend-vs-weekdays':
            return self.weekend_vs_weekdays_analysis()

        return f"Oops... I didn't find anything here... <a href='/{self.FUNCTION_NAME}'>Go back to home</a>?", 404

    def home(self):

        return render_template(
            'home.html',
            summary=self.get_summary(),
            performance_links=self.performance.get_reports_links(),
            pricing_links=self.pricing.get_reports_links(),
            weekend_vs_weekdays_links=self.weekend_vs_weekdays.get_reports_links(),
        )

    def get_summary(self):
        query = """
        SELECT 
        min(datetime) as first_date, 
        max(datetime) as last_date,
        datediff(max(datetime),min(datetime)) duration_days,
        count(id) as tests_executed,
        sum(http_reqs_count) as total_request,
        ROUND(sum(data_received_count)/1e+9,2) as downloaded_gb,
        ROUND(sum(data_sent_count)/1e+9,2) as uploaded_gb,
        count(distinct(csp)) as caas_tested,
        csp
        FROM metrics
        WHERE csp != 'docker'
        """

        # total
        self.db_c.execute(query)
        total = self.db_c.fetchall()

        # per csp
        self.db_c.execute(query + " GROUP BY csp")
        csps = self.db_c.fetchall()
        total_csps = {}
        for item in csps:
            total_csps[item['csp']] = item

        return {
            'total': total[0],
            'csp': total_csps
        }

    def performance_analysis(self):
        cpu = request.args.get('cpu', None)
        memory = request.args.get('memory', None)
        factorial = request.args.get('factorial', None)
        type_of_app = request.args.get('app', None)
        avg_only = bool(int(request.args.get('avg_only', False)))
        all_in_one = bool(int(request.args.get('all_in_one', False)))

        if all_in_one:
            diagrams = [
                self.performance.get_diagram(
                    type_of_app, cpu, memory, '10', avg_only),
                self.performance.get_diagram(
                    type_of_app, cpu, memory, '1000', avg_only),
                self.performance.get_diagram(
                    type_of_app, cpu, memory, '10000', avg_only),
                self.performance.get_diagram(
                    type_of_app, cpu, memory, '32000', avg_only),
                self.performance.get_diagram(
                    type_of_app, cpu, memory, '43000', avg_only),
                self.performance.get_diagram(
                    type_of_app, cpu, memory, '50000', avg_only),
                self.performance.get_diagram(
                    type_of_app, cpu, memory, '60000', avg_only),
            ]
            html = ''
            for item in diagrams:
                html += item

            return html

        return self.performance.get_diagram(type_of_app, cpu, memory, factorial, avg_only)

    def pricing_analysis(self):
        pricing_scenario = request.args.get('scenario', None)
        if pricing_scenario == 'crossing':
            return self.pricing.get_crossing_diagram()
        elif pricing_scenario == 'pricing_factorial_60000':
            return self.pricing.get_pricing_based_on_factorial_60000_execution_time()
        else:
            return self.pricing.get_diagram(pricing_scenario)

    def weekend_vs_weekdays_analysis(self):
        type = request.args.get('type', None)
        return self.weekend_vs_weekdays.get_diagram_app_execution_time(type)


@app.route("/")
def main():
    analysis = Analysis()
    return analysis.route()

def handler(request):
    """
    Handler for running in GCP Cloud Function
    instead of Waitress and Flask
    """
    analysis = Analysis()
    return analysis.route()


if __name__ == "__main__":
    # Serving the app using Waitress
    app.logger.info("Starting Webserver")
    serve(app, host='0.0.0.0', port=5000, threads=4)
