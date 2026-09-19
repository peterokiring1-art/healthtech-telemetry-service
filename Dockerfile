# Use an optimized, secure, lightweight python runtime base image
FROM python:3.11-slim

# Set the operational workspace folder inside the virtual container
WORKDIR /code

# Copy system parameters and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy all application codebase configurations into the container image
COPY . /code

# Expose port 8080 for our FastAPI gateway microservice traffic
EXPOSE 8080

# Production-ready entrypoint execution command that fires up our Uvicorn gateway
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
