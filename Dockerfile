FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create necessary directories
RUN mkdir -p data/output

# Set environment variables
ENV PYTHONPATH=/app
ENV ETHERSCAN_API_KEY=W6Q5KQ5J7465ZQ1XZ3XSAVMC8PGI3DG7UY
ENV ALCHEMY_API_KEY=3eL1ETKO2vJQmnAaTa4wkuACEu8pKVQt

# Command to run the application
CMD ["python", "main.py"] 