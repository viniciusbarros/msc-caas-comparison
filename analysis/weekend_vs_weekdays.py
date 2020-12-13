import base64
import re
import numpy as np
from MySQLdb.cursors import Cursor
from matplotlib.figure import Figure
from io import BytesIO

class WeekendVsWeekdays:

    def __init__(self, db_c: Cursor, function_name) -> None:
        self.db_c = db_c
        self.FUNCTION_NAME = function_name

        self.cpu_mem_comb = [(1, 2), (1, 3), (1, 4), (2, 4)]
        self.types = ['internal-caas', 'application-execution-time']
        self.factorials = [10, 1000, 10000, 32000, 43000, 50000, 60000]

        self.query_app_execution_time = """
        SELECT count(resolution) as count, resolution
        FROM(
            SELECT
                results.csp,
                results.combination,
                results.type_combination,
                ROUND(SUM(CASE results.weekend
                        WHEN 'Weekend' THEN results.app_execution_time_avg
                        WHEN 'Monday to Friday' THEN -results.app_execution_time_avg
                    END), 6) AS difference_ms,
                IF(SUM(CASE results.weekend
                        WHEN 'Weekend' THEN results.app_execution_time_avg
                        WHEN 'Monday to Friday' THEN -results.app_execution_time_avg
                    END)  > 0, "Weekend Slower", "Weekend Faster") as resolution,
            sum(results.count) as samples
            FROM (
                SELECT
                    csp,
                    AVG(http_req_waiting_avg) as http_req_waiting_avg,
                    AVG(app_execution_time_avg) as app_execution_time_avg,
                    count(id) as count,
                    memory,
                    cpu,
                    concat(cpu, 'cpu/', memory,'mem') as combination,
                    IF(WEEKDAY(datetime) in (5,6), "Weekend", "Monday to Friday") as weekend,
                    concat(type, ' ', IF(factorial, factorial, "World") ) as type_combination
                FROM metrics
                WHERE
                csp != 'docker'

                GROUP BY type_combination, combination, csp , weekend
                ORDER BY csp, type_combination, combination
            ) as results

            GROUP BY type_combination, combination, csp
            order by csp, combination, type_combination
        ) AS all_results group by resolution
        """

        self.query_internal_caas = """
        SELECT count(resolution) as count, resolution
        FROM(
            SELECT
                results.csp,
                results.combination,
                results.type_combination,
                ROUND(SUM(CASE results.weekend
                        WHEN 'Weekend' THEN results.caas_processing_time
                        WHEN 'Monday to Friday' THEN -results.caas_processing_time
                    END), 2) AS difference_ms,
                IF(SUM(CASE results.weekend
                        WHEN 'Weekend' THEN results.caas_processing_time
                        WHEN 'Monday to Friday' THEN -results.caas_processing_time
                    END)  > 0, "Weekend Slower", "Weekend Faster") as resolution,
            sum(results.count) as samples
            FROM (
                SELECT
                    csp,
                    AVG(http_req_waiting_avg) as http_req_waiting_avg,
                    AVG(app_execution_time_avg) as app_execution_time_avg,
                    round(AVG(http_req_waiting_avg) - AVG(app_execution_time_avg), 2) as caas_processing_time,
                    count(id) as count,
                    memory,
                    cpu,
                    concat(cpu, 'cpu/', memory,'mem') as combination,
                    IF(WEEKDAY(datetime) in (5,6), "Weekend", "Monday to Friday") as weekend,
                    concat(type, ' ', IF(factorial, factorial, "World") ) as type_combination
                FROM metrics
                WHERE
                    csp != 'docker'

                GROUP BY type_combination, combination, csp , weekend
                ORDER BY csp, type_combination, combination
            ) as results

            GROUP BY type_combination, combination, csp
            order by csp, combination, type_combination
        ) AS all_results group by resolution
        """

    def get_reports_links(self):
        html =  "<h3>Weekend vs Weekdays</h3> <ul>"
        html += f'<li><a href="/{self.FUNCTION_NAME}?report=weekend-vs-weekdays&type=internal-caas">Internal CaaS Processing Time</a></li>'
        html += f'<li><a href="/{self.FUNCTION_NAME}?report=weekend-vs-weekdays&type=application-performance">Performance from Application point-of-view</a></li>'
        html += "</ul>"
        return html

    def get_diagram_app_execution_time(self, type):
        if type == 'application-performance':
            title = 'Application Execution Time'
            query = self.query_app_execution_time
        elif type == 'internal-caas':
            title = 'Internal CaaS Processing Time'
            query = self.query_internal_caas
        else:
            return "Type not find", 404
        

        self.db_c.execute(query)
        data = self.db_c.fetchall()
        fig = Figure()
        ax = fig.subplots()
        labels = []
        sizes = []

        for item in data:
            labels.append(item.get('resolution'))
            sizes.append(item.get('count'))

        # Pie chart, where the slices will be ordered and plotted counter-clockwise:

        ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                shadow=False, startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        

        # # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_title(f'{title} \n({sum(sizes)} scenarios)')
        ax.legend()

        buf = BytesIO()
        fig.savefig(buf, format="png")
        img_base64 = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{img_base64}'/>"

    