# Use official Python image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install python-dotenv

# Copy the application files
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

ENV PYTHONPATH=/app


# Run FastAPI server
CMD ["sh", "-c", "python core/seed_arduinos.py && uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info --use-colors"]
