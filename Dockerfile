# Use a lightweight Python base image
FROM python:slim

# Create a working directory
WORKDIR /app

COPY requirements.txt /app/requirements.txt

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy redirect script into the container
COPY dt_redirect.py /app/dt_redirect.py

# Expose port 8080
EXPOSE 8080

# Run via Gunicorn (what a name)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "dt_redirect:app", "--workers=2"]