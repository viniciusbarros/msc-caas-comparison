#!/bin/bash

docker build -t msc-caas-hello-world . && \\
docker run --rm -p 8080:80 msc-caas-hello-world