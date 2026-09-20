# 1. Use a rock-solid, production-stable slim Python base image
FROM python:3.11-slim

# 2. Set internal system variables to keep Python performing optimally inside Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Establish the file destination directory within the container layer
WORKDIR /app

# 4. Install essential OS-level tools required by numerical packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy the requirements layout first to utilize Docker's lightning-fast cache layers
COPY requirements.txt /app/

# 6. Upgrade package installers and deploy the explicit healthtech package tree
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Move your production application script and trained model weights into the container workspace
COPY app.py /app/
COPY arrhythmia_model_weights.pth /app/

# 8. Unblock the explicit port that your FastAPI production gateway listens on
EXPOSE 8585

# 9. Set the immutable startup instruction to launch your live secure Uvicorn server cluster
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8585"]
