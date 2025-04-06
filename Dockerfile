# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the FastAPI app
COPY . .

# Expose the port that FastAPI will run on
EXPOSE 8000

# Set environment variables 
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}

# Start FastAPI using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
