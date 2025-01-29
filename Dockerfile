# Use a slim Python base image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

EXPOSE 5432

# Copy the rest of the application files to the container
COPY . .

# Run the FastAPI app with --reload for auto-reloading
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

