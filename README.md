# msc-caas-comparison

![Docker Pulls](https://img.shields.io/docker/pulls/viniciusbarros/msc-performance-web-app)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/viniciusbarros/msc-performance-web-app)

The goal of this project is to help organising the development of the MSc research that compares serverless CaaS (Container as a Service) solutions available in public Cloud Service Providers (CSP).

This project will also host the source code that will be used to perform the tests and anylises.

The goal is to have this repository publicly available once the project is finished, so other enthusiasts could benefit from the outcome of the study.

## The application
A Docker application was created to be deployed and utilised in each of the studied CSP.
It consists of a Flask (Python3 web app), served via a Waitress webserver, which is recommended by [Flask](https://flask.palletsprojects.com/en/1.1.x/tutorial/deploy/#run-with-a-production-server)

The application is in this repository, but the Docker image built from the Dockerfile is being hosted in Dockerhub: [viniciusbarros/msc-performance-web-app](https://hub.docker.com/repository/registry-1.docker.io/viniciusbarros/msc-performance-web-app)

There are two main functionalities in the application, which are exposed by two different endpoints: **Hello World** and **High CPU**.

![Image describing containerised application](static/containerised-application-diagram.png)

### Hello World Endpoint
A GET HTTP request to **/** in the application, you'll answer:

```json
{
"data": "Hello World MSC - Container as a Service Comparison",
"duration": 0.0000074
}
```

### High CPU (Factorial) Endpoint
When you access the path **/cpu/factorial/<NUMBER>**, the application will calculate the factorial for the given number and return:

```json
{
"data": "Factorial of 10 is: 3628800",
"duration": 0.0000155,
"end": 1601134255.7055125,
"start": 1601134255.705497
}
```


## Execution of Tests
Tests can be executed in parallel. An example of these executions can be found in the image below.

![Image describing execution of tests in parallel](static/parallel-execution.png)


## Results
A dump of the database with the collected metrics for the initial study can be found in [static/dump.sql.zip](./static/dump.sql.zip)

### Real time information
Some real time information extracted directly from the database displays some insights about the tests.
Plots can be generated on demand using the application inside the folder /analysis.

Example of the Analysis Dashboard:

![Image showing example of dashboard with some results](static/example-dashboard.png)
