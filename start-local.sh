#!/bin/bash

# Check if address is provided
if [ -z "$1" ]; then
    echo "Usage: ./start-local.sh <ethereum_address>"
    exit 1
fi

# Check if Python virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade pip
python -m pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Export environment variables
export ETHERSCAN_API_KEY=W6Q5KQ5J7465ZQ1XZ3XSAVMC8PGI3DG7UY
export ALCHEMY_API_KEY=3eL1ETKO2vJQmnAaTa4wkuACEu8pKVQt

# Run the application
echo "Running transaction tracker for address: $1"
python src/main.py "$1"

# Deactivate virtual environment
deactivate 