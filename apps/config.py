import os

# Read from environment variables (Render injects them automatically)
DATABASE_URL = os.getenv("DATABASE_URL")
ENV = os.getenv("ENV", "local")  # Default to 'local' if not set
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
