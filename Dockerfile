# Use an optimized, secure, lightweight python runtime base image
FROM python:3.11-slim

# Set operational directory
WORKDIR /code

# Install system utilities needed for building scientific binary packages if necessary
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 💡 CACHE OPTIMIZATION: Install heavy packages first to freeze the layer cache
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.14.0 scipy==1.18.1 numpy==2.5.3

# Copy requirements for secondary lightweight microservice packages
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy source repository
COPY . /code

# Expose port 8080 for web entry gateway traffic
EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
