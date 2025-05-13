FROM python:3.11-slim

WORKDIR /app

# Install PostgreSQL client libraries
RUN apt-get update && apt-get install -y libpq-dev gcc && apt-get clean

COPY ./requirements.txt /app/requirements.txt
COPY ./drivers /app/drivers

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir -r /app/drivers/python/requirements.txt
RUN cd /app/drivers/python/ && python setup.py install

COPY . /app


CMD ["fastapi", "run", "/app/main.py", "--port", "8080", "--host", "0.0.0.0"]