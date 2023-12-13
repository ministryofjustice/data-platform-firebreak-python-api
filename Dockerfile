FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /app

# Copy only necessary files
COPY ./requirements.txt /app/

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./daap_api ./app/daap_api

# Use a non-root user
RUN addgroup -g 31337 -S appuser && adduser -u 31337 -S appuser -G appuser
RUN chown -R appuser:appuser /app
USER 31337

# Start the application
EXPOSE 8000
CMD ["uvicorn", "daap_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
