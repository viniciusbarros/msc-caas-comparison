#!/bin/bash
if [ "$#" -lt 1 ]; then
    echo "Corrrect usage: $0 <TAG>"
    exit 1
fi

TAG=$1
docker run --rm -p 8080:80 msc-performance-web-app:$TAG