# Stage 1: Build the image with dependencies
FROM python:3.9-slim AS builder

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt to install dependencies
COPY requirements.txt .

# Install the required Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Create a minimal image with only the necessary files
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /app /app

# Expose port for FastAPI
EXPOSE 8000

# Command to run the backend with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
