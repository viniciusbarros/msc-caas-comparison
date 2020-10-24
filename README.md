# msc-caas-comparison

![Docker Pulls](https://img.shields.io/docker/pulls/viniciusbarros/msc-performance-web-app)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/viniciusbarros/msc-performance-web-app)

The goal of this project is to help organising the development of the MSc research that compares "Container as a Service" solutions available in public Cloud Service Providers (CSP).

This project will also host the source code that will be used to perform the tests and anylises.

The goal is to have this repository publicly available once the project is finished, so other enthusiasts could benefit from the outcome of the study.

## The application
A Docker application was created to be deployed and utilised in each of the studied CSP.
It consists of a Flask (Python3 web app), served via a Waitress webserver, which is recommended by [Flask](https://flask.palletsprojects.com/en/1.1.x/tutorial/deploy/#run-with-a-production-server)

The application is in this repository, but the Docker image built from the Dockerfil is being hosted in Dockerhub: [viniciusbarros/msc-performance-web-app](https://hub.docker.com/repository/registry-1.docker.io/viniciusbarros/msc-performance-web-app)

There are two main functionalities:
### Hello World
A GET HTTP request to **/** in the application, you'll answer:

```json
{
"data": "Hello World MSC - Container as a Service Comparison",
"duration": 0.0000074
}
```

### High CPU (Factorial)
When you access the path **/cpu/factorial/<NUMBER>**, the application will calculate the factorial for the given number and return:

```json
{
"data": "Factorial of 10 is: 3628800",
"duration": 0.0000155,
"end": 1601134255.7055125,
"start": 1601134255.705497
}
```


## Backlog
To help organising the development of the project, the study was divided into GitHub projects and tasks.

* [Initial Extra Info](https://github.com/viniciusbarros/msc-caas-comparison/projects/1)
* [Truly Serverless?](https://github.com/viniciusbarros/msc-caas-comparison/projects/2)
* [Which Solution is cheaper?](https://github.com/viniciusbarros/msc-caas-comparison/projects/3)
* [Which Solution performs better?](https://github.com/viniciusbarros/msc-caas-comparison/projects/4)
* [Are there any cold starts?](https://github.com/viniciusbarros/msc-caas-comparison/projects/5)
* [How well do they scale?](https://github.com/viniciusbarros/msc-caas-comparison/projects/6)
* [Which Solution to recommend?](https://github.com/viniciusbarros/msc-caas-comparison/projects/7)

## Overleaf 
The project is being edited in Overleaf:
https://www.overleaf.com/project/5ed2258d6ab9030001ece10f
