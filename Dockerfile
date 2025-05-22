FROM python:3.10-slim

# Install ffmpeg
RUN apt update && apt install -y ffmpeg

# Set the working directory
WORKDIR /app

# Copy all project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the app
CMD ["python", "app.py"]
