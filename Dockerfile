# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN apt-get update && \
    apt-get install -y cmake g++ libgl1-mesa-glx libglib2.0-0 && \
    pip install --no-cache-dir -r requirements.txt

# Expose port for Flask app
EXPOSE 5000

# Set environment variable for non-debug mode
ENV DEBUG=False

# Run the Flask app
CMD ["python", "flask_app.py"]
