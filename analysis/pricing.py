import base64
import numpy as np
import math
from MySQLdb.cursors import Cursor
from matplotlib.figure import Figure
from io import BytesIO


class Pricing:

    def __init__(self, db_c: Cursor, function_name) -> None:
        self.db_c = db_c
        self.FUNCTION_NAME = function_name

        self.PROVIDERS_MAPPING = {
            "aws": 'AWS',
            'gcp': 'GCP',
            'azure': 'Azure'
        }

        self.PROVIDERS = {
            "AWS": {
                "pricing": {
                    "cpu": 0.0000112444,
                    "memory": 0.0000012347,
                },
                "monthly_free_tier": {
                    "seconds_per_cpu": 0,
                    "seconds_per_memory": 0,
                }
            },
            "Azure": {
                "pricing": {
                    "cpu":  0.0000113,
                    "memory": 0.0000013,
                },
                "monthly_free_tier": {
                    "seconds_per_cpu": 0,
                    "seconds_per_memory": 0,
                }
            },
            "GCP": {
                "pricing": {
                    "cpu": 0.0000240,
                    "memory": 0.0000025,
                },
                "monthly_free_tier": {
                    "seconds_per_cpu": 180000,
                    "seconds_per_memory": 360000,
                }
            }
        }

        self.SCENARIOS = [
            {
                "cpu": 1,
                "memory": 2,
                "hours_per_day": 1,
                "days": 1,
            },
            {
                "cpu": 1,
                "memory": 2,
                "hours_per_day": 1,
                "days": 7,
            },
            {
                "cpu": 1,
                "memory": 2,
                "hours_per_day": 24,
                "days": 7,
            },
            {
                "cpu": 1,
                "memory": 2,
                "hours_per_day": 24,
                "days": 365,
            },
            {
                "cpu": 1,
                "memory": 2,
                "hours_per_day": 2.5,
                "days": 20,
                "months_running": 1,
                "monthly_free_tier": True
            },
            {
                "cpu": 1,
                "memory": 2,
                "hours_per_day": 5,
                "days": 20,
                "months_running": 1,
                "monthly_free_tier": True
            },
        ]

    def get_reports_links(self):
        html = "<h2>Pricing</h2> <ul>"
        for ind, scenario in enumerate(self.SCENARIOS):
            html += f"<li><a href='/{self.FUNCTION_NAME}?report=pricing&scenario={ind}'>Scenario [{ind}]: {scenario['cpu']} CPU, {scenario['memory']} Memory, {scenario['hours_per_day']} Hours/Day </a></li>"

        html += f"<li><a href='/{self.FUNCTION_NAME}?report=pricing&scenario=crossing'>Scenario Crossing Prices (1 CPU, 2 Memory)</a></li>"
        html += f"<li><a href='/{self.FUNCTION_NAME}?report=pricing&scenario=pricing_factorial_60000'>Pricing factorial 60000 (1 CPU, 2 Memory)</a></li>"

        html += "</ul>"
        return html

    def autolabel(self, rects, ax):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format("%.2f" % height),
                        xy=(rect.get_x() + rect.get_width() / 2, rect.get_y()),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
        return ax

    def get_diagram(self, scenario_index):
        try:
            scenario_index = int(scenario_index)
            scenario = self.SCENARIOS[scenario_index]
            html = "<h1>Scenario</h1>"
            html += f"<p>{scenario['cpu']} CPU and {scenario['memory']} GB of Memory for {scenario['hours_per_day']} hour(s) for {scenario['days']} days. Free tier {'considered' if scenario.get('monthly_free_tier', False) else 'not considered'} </p>"

            execution_in_sec = scenario['hours_per_day'] * \
                60 * 60 * scenario['days']

            labels = []
            cpu_price_data = []
            memory_price_data = []

            for provider_name, provider in self.PROVIDERS.items():
                labels.append(provider_name)

                if scenario.get('monthly_free_tier', False):
                    # discount = months * freetier/number of resources
                    discount_cpu_seconds = scenario.get(
                        'months_running', 0) * (provider['monthly_free_tier']['seconds_per_cpu']/scenario['cpu'])
                    discount_mem_seconds = scenario.get('months_running', 0) * (
                        provider['monthly_free_tier']['seconds_per_memory']/scenario['memory'])
                else:
                    discount_cpu_seconds = 0
                    discount_mem_seconds = 0

                cpu_price = provider['pricing']['cpu'] * scenario['cpu'] * \
                    max(execution_in_sec - discount_cpu_seconds, 0)
                memory_price = provider['pricing']['memory'] * scenario['memory'] * max(
                    execution_in_sec - discount_mem_seconds, 0)

                cpu_price_data.append(cpu_price)
                memory_price_data.append(memory_price)

            x = np.arange(len(labels))  # the label locations
            width = 0.30  # the width of the bars
            fig = Figure()
            ax = fig.subplots()

            rect_cpu = ax.bar(labels, cpu_price_data, width, label='CPU')
            ax = self.autolabel(rect_cpu, ax)

            rect_memory = ax.bar(labels, memory_price_data,
                                 width, label='Memory', bottom=cpu_price_data)
            ax = self.autolabel(rect_memory, ax)

            # # Add some text for labels, title and custom x-axis tick labels, etc.
            ax.set_ylabel('US Dollars ($)')
            ax.set_title(f"{scenario['cpu']} CPU and {scenario['memory']} GB of Memory for {scenario['hours_per_day']} hour(s) for {scenario['days']} days. \n Free tier {'considered' if scenario.get('monthly_free_tier', False) else 'not considered'}.")
            ax.legend()

            buf = BytesIO()
            fig.savefig(buf, format="png")
            img_base64 = base64.b64encode(buf.getbuffer()).decode("ascii")
            html += f"<img src='data:image/png;base64,{img_base64}'/>"

            return html

        except IndexError:
            return f"Scenario {scenario_index} not found!", 404
        except Exception as e:
            return f"Some error happened while trying to generate graphic for scenario {scenario_index}: {e}", 500

    def get_crossing_diagram(self):
        fig = Figure()
        ax = fig.subplots()
        cpu = 1
        memory = 2
        for provider_name, provider in self.PROVIDERS.items():
            hours = []
            price = []

            for hour in range(0, 120):
                # discount = months * freetier/number of resources
                discount_cpu_seconds = (
                    provider['monthly_free_tier']['seconds_per_cpu']/cpu)
                discount_mem_seconds = (
                    provider['monthly_free_tier']['seconds_per_memory']/memory)

                cpu_price = provider['pricing']['cpu'] * cpu * \
                    max((hour * 60 * 60) - discount_cpu_seconds, 0)
                memory_price = provider['pricing']['memory'] * memory * \
                    max((hour * 60 * 60) - discount_mem_seconds, 0)

                hours.append(hour)
                price.append(cpu_price+memory_price)

            ax.plot(hours, price, label=provider_name)

        ax.set_title(
            f"Finding when the price for {cpu} CPU and {memory} GB of Memory \n is the same in all CSP. Free tier considered.")
        ax.set_ylabel('Price in Dollars ($)')
        ax.set_xlabel('Hours running application in a month')
        ax.legend()

        buf = BytesIO()
        fig.savefig(buf, format="png")
        img_base64 = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{img_base64}'/>"

    def get_pricing_based_on_factorial_60000_execution_time(self):
        cpu = 1
        memory = 2
        query = f"""
        SELECT
            csp,
            avg(app_execution_time_avg) as app_execution_time_avg
        FROM metrics
        WHERE
            memory = {memory} AND
            cpu = {cpu} AND
            type = 'factorial' AND
            factorial = 60000 AND
            csp != 'docker'
        GROUP BY csp
        ORDER BY csp
        """

        self.db_c.execute(query)
        data = self.db_c.fetchall()

        fig = Figure()
        ax = fig.subplots()

        for item in data:
            csp = self.PROVIDERS_MAPPING[item.get('csp')]
            # divided by 1000 as it is stored in ms
            app_execution_time =  float(item.get('app_execution_time_avg'))/1000

            cpu_price = self.PROVIDERS[csp]['pricing']['cpu'] * cpu
            mem_price = self.PROVIDERS[csp]['pricing']['memory'] * memory
            price_per_execution = (app_execution_time * cpu_price) + (app_execution_time * mem_price)

            executions = []
            price = []
            range_to_plot = range(0, 100000, 100)

            for num_executions in range_to_plot:
                executions.append(num_executions)
                price.append(price_per_execution*num_executions)

            ax.plot(executions, price, label=csp)
            # Check if Freetier is available and plot it as well
            if self.PROVIDERS[csp]['monthly_free_tier']['seconds_per_cpu'] > 0 \
            or self.PROVIDERS[csp]['monthly_free_tier']['seconds_per_memory'] > 0:
                discount_cpu_seconds = self.PROVIDERS[csp]['monthly_free_tier']['seconds_per_cpu']/cpu
                discount_mem_seconds = self.PROVIDERS[csp]['monthly_free_tier']['seconds_per_memory']/memory
                executions = []
                price = []
                for num_executions in range_to_plot:
                    executions.append(num_executions)
                    price.append((max(app_execution_time * num_executions - discount_cpu_seconds, 0) * cpu_price) + (max(app_execution_time * num_executions - discount_mem_seconds, 0) * mem_price))
                ax.plot(executions, price, label=f"{csp} (including free tier)")


        # # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Price in Dollars ($)')
        ax.set_title('Price per execution when calculating factorial of 60000 based on the avg \n execution time from performance test (1 CPU and 2GB of Memory)')
        ax.set_xlabel('Number of Executions')
        ax.legend()

        buf = BytesIO()
        fig.savefig(buf, format="png")
        img_base64 = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"<img src='data:image/png;base64,{img_base64}'/>"
