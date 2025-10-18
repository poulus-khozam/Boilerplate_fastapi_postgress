
# Use the official lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy project root files
COPY ../LICENSE ../README.md ./

# Set working directory to src because main.py is inside src
WORKDIR /app/src

# Copy requirements.txt (relative to docker folder)
COPY ../src/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for Python
ENV PYTHONUNBUFFERED=1

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
