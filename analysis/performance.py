import base64
import numpy as np
from MySQLdb.cursors import Cursor
from matplotlib.figure import Figure
from io import BytesIO

class Performance:

    def __init__(self, db_c: Cursor, function_name) -> None:
        self.db_c = db_c
        self.FUNCTION_NAME = function_name

        self.cpu_mem_comb = [(1, 2), (1, 3), (1, 4), (2, 4)]
        self.apps = ['hello-world', 'factorial']
        self.factorials = [10, 1000, 10000, 32000, 43000, 50000, 60000]

    def get_reports_links(self):
        html = ""
        for app in self.apps:
            html = html + f"<h3>App {app}</h3> <ul>"

            if app == 'hello-world':
                for cpu, mem in self.cpu_mem_comb:
                    html = html + \
                        f'<li><a href="/{self.FUNCTION_NAME}?report=performance&app=hello&cpu={cpu}&memory={mem}">Performance Hello World - {cpu} CPU & {mem} Memory</a></li>'
            elif app == 'factorial':
                for cpu, mem in self.cpu_mem_comb:
                    for factorial_param in self.factorials:
                        html += f'<li><a href="/{self.FUNCTION_NAME}?report=performance&app={app}&cpu={cpu}&memory={mem}&factorial={factorial_param}">Performance Factorial {factorial_param} - {cpu} CPU & {mem} Memory</a></li>'
                    html += f'<li><a href="/{self.FUNCTION_NAME}?report=performance&app={app}&cpu={cpu}&memory={mem}&all_in_one=1">All In One - {cpu} CPU & {mem} Memory</a></li>'
                    html += f'<li><a href="/{self.FUNCTION_NAME}?report=performance&app={app}&cpu={cpu}&memory={mem}&all_in_one=1&avg_only=1">All In One AVG Only - {cpu} CPU & {mem} Memory</a></li>'

                    
            
            html = html + '</ul>'
        
        return html

    def get_diagram(self, type_of_app, cpu, memory, factorial, avg_only=False):
        query = f"""SELECT
                    csp,
                    min(app_execution_time_min) as  app_execution_time_min,
                    avg(app_execution_time_avg) as  app_execution_time_avg,
                    max(app_execution_time_max) as  app_execution_time_max,
                    count(id) as count
                    FROM metrics
                    WHERE
                    memory = {memory} AND
                    cpu = {cpu} AND
                    type = '{type_of_app}'
                    """
        if type_of_app == 'factorial':
            query = query + f" AND factorial = {factorial}"

        query = query + """
                    GROUP BY csp
                    ORDER BY csp
                """

        
        self.db_c.execute(query)
        data = self.db_c.fetchall()
        fig = Figure()
        ax = fig.subplots()

        labels = []
        min_data = []
        avg_data = []
        max_data = []
        total_items = 0

        for item in data:
            csp = item.get('csp')
            if csp == 'docker':
                
                if not avg_only:
                    ax.axhline(y=item.get('app_execution_time_min'),xmin=0, label="Docker Min", linestyle=':',  color='#000000')

                ax.axhline(y=item.get('app_execution_time_avg'),xmin=0, label="Docker Avg", linestyle='--', color='#000000')
                if not avg_only:
                    ax.axhline(y=item.get('app_execution_time_max'),xmin=0, label="Docker Max", linestyle='-',  color='#000000')
            else:
                labels.append(csp)
                min_data.append(item.get('app_execution_time_min'))
                avg_data.append(item.get('app_execution_time_avg'))
                max_data.append(item.get('app_execution_time_max'))
                total_items += int(item.get('count'))

        x = np.arange(len(labels))  # the label locations
        width = 0.20 if not avg_only else 0.50  # the width of the bars

        if not avg_only:
            rect_min = ax.bar(x - width, min_data, width, label='Min')
        
        rect_avg = ax.bar(x, avg_data, width, label='Avg')
        
        if not avg_only:
            rect_max = ax.bar(x + width, max_data, width, label='Max')

        # # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('millisecond (ms)')
        ax.set_title(f'Min, Avg and Max application response times for {type_of_app} {factorial if factorial is not None else "world"}.\n {cpu} CPU and {memory}GB of Memory. ({total_items} tests executed)')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        buf = BytesIO()
        fig.savefig(buf, format="png")
        img_base64 = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{img_base64}'/>"

    