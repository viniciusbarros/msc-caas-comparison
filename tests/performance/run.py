import os
import logging
from datetime import datetime
import time


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("execution.log"),
        logging.StreamHandler()
    ]
)


class Runner:

    def __init__(self) -> None:
        logging.info("-------------------Starting Script Runner-------------------")
        self.sleep_time_between_cases = 10

        self.cases = [
            "k6 run -e DOMAIN='{domain}' -e ENDPOINT='' hello-world.js --insecure-skip-tls-verify --summary-export=metrics/{now}_hello_world_{hosting}_{cpu}_cpu_{memory}_memory.json",
            # 0.00001
            "k6 run -e DOMAIN='{domain}' -e ENDPOINT='/cpu/factorial/10' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_10_{hosting}_{cpu}_cpu_{memory}_memory.json",
            # 0.0005
            "k6 run -e DOMAIN='{domain}' -e ENDPOINT='/cpu/factorial/1000' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_1000_{hosting}_{cpu}_cpu_{memory}_memory.json",
            # 0.5
            "k6 run -e DOMAIN='{domain}' -e ENDPOINT='/cpu/factorial/10000' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_10000_{hosting}_{cpu}_cpu_{memory}_memory.json",
            # 0.5
            "k6 run -e DOMAIN='{domain}' -e ENDPOINT='/cpu/factorial/32000' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_32000_{hosting}_{cpu}_cpu_{memory}_memory.json",
            # 1s
            "k6 run -e DOMAIN='{domain}' -e ENDPOINT='/cpu/factorial/43000' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_43000_{hosting}_{cpu}_cpu_{memory}_memory.json",
            # 2s
            "k6 run -e DOMAIN='{domain}' -e ENDPOINT='/cpu/factorial/50000' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_50000_{hosting}_{cpu}_cpu_{memory}_memory.json",
            # 3s
            "k6 run -e DOMAIN='{domain}' -e ENDPOINT='/cpu/factorial/60000' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_60000_{hosting}_{cpu}_cpu_{memory}_memory.json",
        ]

        self.scenarios = [
            {
                "hosting": "docker",
                "configs": [
                    {
                        "cpu": '1',
                        "memory": '2'
                    },
                    {
                        "cpu": '2',
                        "memory": '2'
                    }
                ],
                "start": "docker run --rm -d -p 8080:80 --name=caas-local --cpus={cpu} --memory={memory}g msc-performance-web-app:latest",
                "stop": "docker stop caas-local && docker rm caas-local",
                "domain": "http://localhost:8080"
            }
        ]

        logging.info(
            f"We have {len(self.scenarios)} scenario(s) to run. {len(self.cases)} cases each.")

    def execute_all(self):
        for scenario in self.scenarios:
            if scenario.get('hosting') == 'docker':
                self.run_docker(scenario)

    def run_docker(self, scenario):
        logging.info(f"Let's run this Docker scenario.")
        logging.info(f"{len(scenario.get('configs',[]))} config(s) to run!")

        for conf in scenario.get('configs', []):
            cpu = conf.get('cpu')
            memory = conf.get('memory')

            # Starting Container
            start_cmd = scenario.get('start').format(
                cpu=cpu,
                memory=memory
            )

            logging.info(f"Running docker w/ CPU: {cpu} and Memory: {memory}")
            self.run_command(start_cmd)

            # Running Test Cases
            for case in self.cases:
                run_cmd = case.format(cpu=cpu, memory=memory, hosting=scenario.get(
                    'hosting'), domain=scenario.get('domain'), now=datetime.now().strftime("%Y_%m_%d_%H%M%S"))
                self.run_command(run_cmd)
                # Sleeping between
                time.sleep(self.sleep_time_between_cases)

            # Stopping Container
            logging.info(f"Stopping Docker w/ CPU: {cpu} and Memory: {memory}")
            self.run_command(scenario.get('stop'))

    def run_command(self, command):
        logging.info(f"Running command: {command}")
        stream = os.popen(command)
        output = stream.read()

        logging.info(f"Output: {output}")


runner = Runner()
runner.execute_all()