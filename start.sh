#!/bin/bash

# Check if address is provided
if [ -z "$1" ]; then
    echo "Usage: ./start.sh <ethereum_address>"
    exit 1
fi

# Build the Docker image if it doesn't exist
if ! docker image inspect eth-transaction-tracker >/dev/null 2>&1; then
    echo "Building Docker image..."
    docker build -t eth-transaction-tracker .
fi

# Run the container
echo "Running transaction tracker for address: $1"
docker run --rm \
    -v "$(pwd)/data:/app/data" \
    eth-transaction-tracker python src/main.py "$1" 