FROM python:3.9-slim

WORKDIR /app

# Copy the loadtest script - make sure the path is correct
COPY ./generate_data.py /app/

# Install dependencies
RUN pip install aiohttp

# Environment variables with more conservative defaults
ENV API_HOST=localhost:8080
ENV BUSINESS_COUNT=1000
ENV RELATIONSHIPS_PER_BUSINESS=10 
ENV BATCH_SIZE=50
ENV MAX_CONCURRENT_REQUESTS=10
ENV REQUEST_TIMEOUT=10
# Phase control
ENV SKIP_BUSINESSES=false
ENV SKIP_RELATIONSHIPS=false
ENV BUSINESSES_FILE=/app/businesses.json

# Create a volume for persistent data
VOLUME /app

# Run the script with full path
CMD ["python", "/app/generate_data.py"]