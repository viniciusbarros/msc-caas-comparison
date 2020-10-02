import os
import logging
from datetime import datetime
import time
import json


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("execution.log"),
        logging.StreamHandler()
    ]
)


class Runner:
    CASES = [
        "k6 run -e DOMAIN='{domain}' -e ENDPOINT='' hello-world.js --insecure-skip-tls-verify --summary-export=metrics/{now}_hello_world_{hosting}_{cpu}_cpu_{memory}_memory.json",
        # 0.00001
        "k6 run -e DOMAIN='{domain}' -e ENDPOINT='cpu/factorial/10' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_10_{hosting}_{cpu}_cpu_{memory}_memory.json",
        # 0.0005
        "k6 run -e DOMAIN='{domain}' -e ENDPOINT='cpu/factorial/1000' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_1000_{hosting}_{cpu}_cpu_{memory}_memory.json",
        # 0.05
        "k6 run -e DOMAIN='{domain}' -e ENDPOINT='cpu/factorial/10000' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_10000_{hosting}_{cpu}_cpu_{memory}_memory.json",
        # 0.5
        "k6 run -e DOMAIN='{domain}' -e ENDPOINT='cpu/factorial/32000' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_32000_{hosting}_{cpu}_cpu_{memory}_memory.json",
        # 1s
        "k6 run -e DOMAIN='{domain}' -e ENDPOINT='cpu/factorial/43000' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_43000_{hosting}_{cpu}_cpu_{memory}_memory.json",
        # 2s
        "k6 run -e DOMAIN='{domain}' -e ENDPOINT='cpu/factorial/50000' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_50000_{hosting}_{cpu}_cpu_{memory}_memory.json",
        # 3s
        "k6 run -e DOMAIN='{domain}' -e ENDPOINT='cpu/factorial/60000' cpu.js --insecure-skip-tls-verify --summary-export=metrics/{now}_factorial_60000_{hosting}_{cpu}_cpu_{memory}_memory.json",
    ]
    SCENARIOS = [
        {
            "hosting": "docker",
            "configs": [
                {
                    "cpu": '1',
                    "memory": '2'
                },
                {
                    "cpu": '1',
                    "memory": '3'
                },
                {
                    "cpu": '1',
                    "memory": '4'
                },
                {
                    "cpu": '2',
                    "memory": '4'
                }
            ],
            "start": "docker run --rm -d -p 8080:80 --name=caas-local --cpus={cpu} --memory={memory}g msc-performance-web-app:latest",
            "stop": "docker stop caas-local && docker rm caas-local",
            "domain": "http://localhost:8080"
        },
        {
            "hosting": "gcp",
            "configs": [
                {
                    "cpu": '1.0',
                    "memory": '2048Mi'
                },
                {
                    "cpu": '1.0',
                    "memory": '3072Mi'
                },
                {
                    "cpu": '1.0',
                    "memory": '4096Mi'
                },
                {
                    "cpu": '2.0',
                    "memory": '4096Mi'
                }
            ],
            "start": "cd ../../terraform/gcp && terraform plan -out plan -var 'cpu={cpu}' -var 'memory={memory}' && terraform apply -auto-approve -var 'cpu={cpu}' -var 'memory={memory}'",
            "stop": "cd ../../terraform/gcp && terraform destroy -auto-approve",
            "get_url": 'cd ../../terraform/gcp && terraform output -json service_url'
        },
        {
            "hosting": "aws",
            "configs": [
                {
                    "cpu": '1024',
                    "memory": '2048'
                },
                {
                    "cpu": '1024',
                    "memory": '3072'
                },
                {
                    "cpu": '1024',
                    "memory": '4096'
                },
                {
                    "cpu": '2048',
                    "memory": '4096'
                }
            ],
            "start": "cd ../../terraform/aws && terraform plan -out plan -var 'cpu={cpu}' -var 'memory={memory}' && terraform apply -auto-approve -var 'cpu={cpu}' -var 'memory={memory}'",
            "stop": "cd ../../terraform/aws && terraform destroy -auto-approve",
            "get_networks": 'aws ec2 describe-network-interfaces'
        },
        {
            "hosting": "azure",
            "configs": [
                {
                    "cpu": '1',
                    "memory": '2'
                },
                {
                    "cpu": '1',
                    "memory": '3'
                },
                {
                    "cpu": '1',
                    "memory": '4'
                },
                {
                    "cpu": '2',
                    "memory": '4'
                }
            ],
            "start": "cd ../../terraform/azure && terraform plan -out plan -var 'cpu={cpu}' -var 'memory={memory}' && terraform apply -auto-approve -var 'cpu={cpu}' -var 'memory={memory}'",
            "stop": "cd ../../terraform/azure && terraform destroy -auto-approve",
            "get_url": 'cd ../../terraform/azure && terraform output -json service_url'
        }
    ]

    def __init__(self) -> None:
        self.sleep_time_between_cases = 10

        logging.info(
            f"We have {len(self.SCENARIOS)} scenario(s) to run. {len(self.CASES)} cases each.")

    def execute_all(self):
        logging.info("--------Starting Script Runner--------")
        for scenario in self.SCENARIOS:
            hosting = scenario.get('hosting')
            if hosting == 'docker':
                self.run_docker(scenario)
            elif hosting == 'gcp':
                self.run_gcp(scenario)
            elif hosting == 'aws':
                self.run_aws(scenario)
            elif hosting == 'azure':
                self.run_azure(scenario)
            else:
                logging.warning(f'Hosting {hosting} is not yet supported')
        logging.info("--------Ending Script Runner--------")

    def run_command(self, command):
        logging.info(f"Running command: {command}")
        stream = os.popen(command)
        output = stream.read()

        logging.info(f"Output: {output}")
        return output

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
            for case in self.CASES:
                run_cmd = case.format(cpu=cpu, memory=memory, hosting=scenario.get(
                    'hosting'), domain=scenario.get('domain'), now=datetime.now().strftime("%Y_%m_%d_%H%M%S"))
                self.run_command(run_cmd)
                # Sleeping between
                time.sleep(self.sleep_time_between_cases)

            # Stopping Container
            logging.info(f"Stopping Docker w/ CPU: {cpu} and Memory: {memory}")
            self.run_command(scenario.get('stop'))

    def run_gcp(self, scenario):
        logging.info(f"Let's run this GCP scenario.")
        logging.info(f"{len(scenario.get('configs',[]))} config(s) to run!")

        for conf in scenario.get('configs', []):
            cpu = conf.get('cpu')
            memory = conf.get('memory')

            start_cmd = scenario.get('start').format(
                cpu=cpu,
                memory=memory
            )

            # Provisioning infrastructure
            logging.info(
                f"Creating GCP Cloud Run w/ CPU: {cpu} and Memory: {memory}")
            self.run_command(start_cmd)

            # Getting generated dynamic URL
            output = json.loads(self.run_command(scenario.get('get_url')))
            url = output[0].get('url')

            # Running Test Cases
            for case in self.CASES:
                run_cmd = case.format(cpu=cpu, memory=memory, hosting=scenario.get(
                    'hosting'), domain=url, now=datetime.now().strftime("%Y_%m_%d_%H%M%S"))
                self.run_command(run_cmd)
                # Sleeping between
                time.sleep(self.sleep_time_between_cases)

            # Stopping Container
            logging.info(
                f"Destroying GCP Cloud Run w/ CPU: {cpu} and Memory: {memory}")
            self.run_command(scenario.get('stop'))

    def run_aws(self, scenario):
        logging.info(f"Let's run this AWS ECS Fargate scenario.")
        logging.info(f"{len(scenario.get('configs',[]))} config(s) to run!")

        for conf in scenario.get('configs', []):
            cpu = conf.get('cpu')
            memory = conf.get('memory')

            start_cmd = scenario.get('start').format(
                cpu=cpu,
                memory=memory
            )

            # Provisioning infrastructure
            logging.info(
                f"Creating AWS ECS Fargate w/ CPU: {cpu} and Memory: {memory}")
            self.run_command(start_cmd)

            logging.info(
                'Sleeping for 90 sec wainting for network interface & service to be ready')
            time.sleep(90)
            # Getting instance IP
            # Note: Unfortunatelly  ECS/Terraform dont provide an easy way to get the IP or domain
            networks = json.loads(self.run_command(
                scenario.get('get_networks')))
            url = 'http://' + \
                networks['NetworkInterfaces'][0]['Association']['PublicDnsName']

            # Running Test Cases
            for case in self.CASES:
                run_cmd = case.format(cpu=cpu, memory=memory, hosting=scenario.get(
                    'hosting'), domain=url, now=datetime.now().strftime("%Y_%m_%d_%H%M%S"))
                self.run_command(run_cmd)
                # Sleeping between
                time.sleep(self.sleep_time_between_cases)

            # Stopping Container
            logging.info(
                f"Destroying AWS ECS Fargate w/ CPU: {cpu} and Memory: {memory}")
            self.run_command(scenario.get('stop'))

    def run_azure(self, scenario):
        logging.info(f"Let's run this Azure scenario.")
        logging.info(f"{len(scenario.get('configs',[]))} config(s) to run!")

        for conf in scenario.get('configs', []):
            cpu = conf.get('cpu')
            memory = conf.get('memory')

            start_cmd = scenario.get('start').format(
                cpu=cpu,
                memory=memory
            )

            # Provisioning infrastructure
            logging.info(
                f"Creating Azure Container Instance w/ CPU: {cpu} and Memory: {memory}")
            self.run_command(start_cmd)

            # Getting generated dynamic URL
            domain = json.loads(self.run_command(scenario.get('get_url')))
            url = 'http://' + domain

            logging.info(
                'Sleeping for 60 sec wainting for service to be ready')
            time.sleep(60)

            # Running Test Cases
            for case in self.CASES:
                run_cmd = case.format(cpu=cpu, memory=memory, hosting=scenario.get(
                    'hosting'), domain=url, now=datetime.now().strftime("%Y_%m_%d_%H%M%S"))
                self.run_command(run_cmd)
                # Sleeping between
                time.sleep(self.sleep_time_between_cases)

            # Stopping Container
            logging.info(
                f"Destroying Azure Container Instance w/ CPU: {cpu} and Memory: {memory}")
            self.run_command(scenario.get('stop'))


runner = Runner()
runner.execute_all()
