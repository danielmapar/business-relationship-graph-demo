# Loadtest for Platform API

## Setup

### To build the docker image
```bash
docker build -t platform-api-loadtest .
```

### To run the full process (business creation and relationship creation)
```bash
docker run --network="host" \
  -v "$(pwd):/app" \
  -e API_HOST=localhost:8080 \
  -e BUSINESS_COUNT=1000 \
  -e RELATIONSHIPS_PER_BUSINESS=10 \
  platform-api-loadtest
```

### To run only the business creation phase

```bash
docker run --network="host" \
  -v "$(pwd):/app" \
  -e API_HOST=localhost:8080 \
  -e BUSINESS_COUNT=1000 \
  -e SKIP_RELATIONSHIPS=true \
  platform-api-loadtest
```

### To run only the relationship creation phase (using previously created businesses)

```bash
docker run --network="host" \
  -v "$(pwd):/app" \
  -e API_HOST=localhost:8080 \
  -e SKIP_BUSINESSES=true \
  -e RELATIONSHIPS_PER_BUSINESS=30 \
  platform-api-loadtest
```

### Generate chain data: 1 business with 199 hops to another business

```bash
docker run --network="host" \
  -v "$(pwd):/app" \
  -e API_HOST=localhost:8080 \
  platform-api-loadtest python generate_chain_data.py
```

### Generate a business with 100 relationships

```bash
docker run --network="host" \
  -v "$(pwd):/app" \
  -e API_HOST=localhost:8080 \
  platform-api-loadtest python generate_business_with_100_relationships.py
```
