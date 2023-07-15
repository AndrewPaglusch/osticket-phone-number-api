# Use the official Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code
COPY main.py .

# Expose the port on which the Flask application runs
EXPOSE 5000

# Run the Flask application
CMD ["python", "main.py"]
