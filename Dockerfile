# Use a lightweight Python base image
FROM python:slim

# Create a working directory
WORKDIR /app

# Copy your redirect script into the container
COPY dt_redirect.py /app/dt_redirect.py

# Install PRAW (and any other needed packages)
RUN pip install --no-cache-dir praw

# Expose port 8080
EXPOSE 8080

# Start your Python script
CMD ["python", "dt_redirect.py"]