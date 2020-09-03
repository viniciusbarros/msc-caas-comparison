#!/bin/bash
if [ "$#" -lt 1 ]; then
    echo "Corrrect usage: $0 <Tag>"
    exit 1
fi

TAG=$1
docker build -t msc-performance-web-app:$TAG .