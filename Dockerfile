# Use a slim Python base image
FROM python:3.9-slim

# Set the working directory inside the container to /guterberg_fast_api/apps
WORKDIR /guterberg_fast_api/apps

# Copy the requirements.txt file from the root directory (outside apps) to the container
COPY ../requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Expose the port for the FastAPI app
EXPOSE 8000

# Set the PYTHONPATH environment variable to include the /guterberg_fast_api/apps directory
ENV PYTHONPATH=/guterberg_fast_api/apps

# Copy the rest of the application files from the /guterberg_fast_api folder to the container
COPY . .

# Run the FastAPI app with --reload for auto-reloading
CMD ["uvicorn", "apps.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
