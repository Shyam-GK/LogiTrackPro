FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev

# Copy application code
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Run the app
CMD ["streamlit", "run", "app.py"]