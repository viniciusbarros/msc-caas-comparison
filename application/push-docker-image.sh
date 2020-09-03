#!/bin/bash
if [ "$#" -lt 1 ]; then
    echo "Corrrect usage: $0 <Tag>"
    exit 1
fi

TAG=$1
docker tag  msc-performance-web-app viniciusbarros/msc-performance-web-app:$TAG
docker push viniciusbarros/msc-performance-web-app:$TAG

