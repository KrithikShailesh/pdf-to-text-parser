# Use official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy files to the container
COPY . /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port
EXPOSE 8080

# Start the Flask app
CMD ["python", "app.py"]
