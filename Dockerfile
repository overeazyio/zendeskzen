# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements files into the container at /app
COPY zendesk_extractor/requirements.txt /app/
COPY zendesk_extractor/web/requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variables (replace with your actual credentials)
ENV ZENDESK_DOMAIN="your_zendesk_domain"
ENV ZENDESK_EMAIL="your_zendesk_email"
ENV ZENDESK_API_TOKEN="your_zendesk_api_token"

# Run the web server when the container launches
CMD ["uvicorn", "zendesk_extractor.web.main:app", "--host", "0.0.0.0", "--port", "8000"]
