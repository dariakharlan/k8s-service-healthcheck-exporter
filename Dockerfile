# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements and install them
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Prometheus exporter script into the container
COPY main.py .

# Expose the exporter port
EXPOSE 9100

# Run the exporter script
CMD ["python", "main.py"]
